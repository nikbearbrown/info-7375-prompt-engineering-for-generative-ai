"""Reproducible audio-first Brutalist / Manim / FFmpeg build on Windows."""
import argparse, importlib.util, json, math, os, shutil, subprocess, sys, time, wave
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent
WORK=ROOT.parent
TOOLKIT=Path(os.environ.get('ART_HOME',WORK/'brutalist.art')).resolve()
os.environ['PYTHONIOENCODING']='utf-8'
os.environ['TIKTOKEN_CACHE_DIR']=str(WORK/'.tokenizer-cache')
os.environ['PATH']=str(WORK/'.tools')+os.pathsep+str(TOOLKIT/'runtime/remotion/node_modules/@remotion/compositor-win32-x64-msvc')+os.pathsep+os.environ['PATH']
FFMPEG=shutil.which('ffmpeg')
FFPROBE=shutil.which('ffprobe')
FPS=24

def log(msg):
    line=f"{datetime.now(timezone.utc).isoformat()} {msg}"
    print(line,flush=True)
    (ROOT/'evidence').mkdir(exist_ok=True)
    with (ROOT/'evidence/build.log').open('a',encoding='utf-8') as f:f.write(line+'\n')

def run(args, name):
    log('COMMAND '+subprocess.list2cmdline([str(x) for x in args]))
    target=ROOT/'evidence'/f'{name}.log'
    if target.exists():
        shutil.copy2(target,target.with_name(target.stem+'-previous-'+str(time.time_ns())+'.log'))
    with target.open('w',encoding='utf-8') as f:
        proc=subprocess.run([str(x) for x in args],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,env=os.environ)
    log(f'{name}: exit={proc.returncode}; output=evidence/{name}.log')
    if proc.returncode: raise RuntimeError(target.read_text(encoding='utf-8',errors='replace')[-4500:])

def read_sheet():return json.loads((ROOT/'beat_sheet.json').read_text(encoding='utf-8'))
def save_sheet(sheet):(ROOT/'beat_sheet.json').write_text(json.dumps(sheet,indent=2),encoding='utf-8')

def audio(speed,only=None):
    sys.path.insert(0,str(TOOLKIT/'runtime/scripts'))
    import generate_audio_kokoro as toolkit_audio
    engine=toolkit_audio.load_engine()
    sheet=read_sheet()
    assets=ROOT/'assets/audio'; assets.mkdir(parents=True,exist_ok=True)
    cursor=0
    for beat in sheet['beats']:
        if only and beat['beat_id'] not in only:
            beat['global_start_s']=cursor
            cursor+=beat['actual_duration_s']
            continue
        chunks=[]; cues=[]; offset=0
        for i,text in enumerate(beat['segments']):
            samples,sr=engine.create(toolkit_audio.normalize_for_tts(text),voice='am_onyx',speed=speed,lang='en-us')
            samples=np.asarray(samples,dtype=np.float32)
            # Small real pause per sentence group, included in the master clock.
            samples=np.concatenate([samples,np.zeros(round(sr*.18),dtype=np.float32)])
            duration=len(samples)/sr
            cues.append(dict(index=i,start_s=round(offset,5),duration_s=round(duration,5),narration=text))
            chunks.append(samples);offset+=duration
        count_frames=math.ceil(offset*FPS)+6
        duration=count_frames/FPS
        tail=round(duration*sr)-sum(len(c) for c in chunks)
        joined=np.concatenate(chunks+[np.zeros(max(0,tail),dtype=np.float32)])
        out=assets/f"{beat['beat_id']}.wav"
        with wave.open(str(out),'wb') as f:
            f.setnchannels(1);f.setsampwidth(2);f.setframerate(sr)
            f.writeframes((np.clip(joined,-1,1)*32767).astype('<i2').tobytes())
        beat.update(audio_file=out.relative_to(ROOT).as_posix(),actual_duration_s=duration,
                    global_start_s=cursor,cues=cues,timing_status='measured from PCM sample count',tts_speed=speed)
        cursor+=duration
        log(f"AUDIO {beat['beat_id']}: {duration:.3f}s; {len(joined)} samples at {sr}Hz; speed={speed}")
    sheet['metadata']['runtime_s']=cursor
    save_sheet(sheet)
    log(f'TOTAL AUDIO TIMELINE {cursor:.3f}s')

def fit(target=170):
    """Fit measured audio to an exact frame budget with pitch-preserving tempo."""
    sheet=read_sheet(); total=sum(b['actual_duration_s'] for b in sheet['beats'])
    cumulative=0; used_frames=0; cursor=0
    for b in sheet['beats']:
        old=b['actual_duration_s'];cumulative+=old
        end_frames=round(cumulative/total*target*FPS)
        duration=(end_frames-used_frames)/FPS;used_frames=end_frames
        factor=old/duration
        src=ROOT/b['audio_file'];tmp=src.with_name(src.stem+'-fit.wav')
        run([FFMPEG,'-y','-v','error','-i',src,'-af',f'atempo={factor:.10f},apad','-t',f'{duration:.10f}','-ar','24000','-ac','1','-c:a','pcm_s16le',tmp],f"fit-{b['beat_id']}")
        os.replace(tmp,src)
        for cue in b['cues']:
            cue['start_s']=round(cue['start_s']/factor,6)
            cue['duration_s']=round(cue['duration_s']/factor,6)
        b.update(actual_duration_s=duration,global_start_s=cursor,tempo_adjustment=factor,
                 timing_status='Measured speech; pitch-preserving tempo conformed to exact frame budget')
        cursor+=duration
    sheet['metadata'].update(runtime_s=target,target_duration_s=[target,target])
    save_sheet(sheet);log(f'EXACT TIMELINE: {target}s / {used_frames} frames; original measured audio {total:.6f}s')

def render(only=None):
    (ROOT/'renders').mkdir(exist_ok=True)
    for beat in read_sheet()['beats']:
        if only and beat['beat_id'] not in only:continue
        os.environ['BEAT_ID']=beat['beat_id']
        run([sys.executable,'-m','manim','render','scene.py','TokenFilm','--renderer','cairo','-r','1920,1080','--fps',str(FPS),'--disable_caching','--media_dir','media','-o',beat['beat_id']+'.mp4'],f"render-{beat['beat_id']}")
        candidates=list((ROOT/'media/videos/scene').rglob(beat['beat_id']+'.mp4'))
        candidates=[x for x in candidates if 'partial_movie_files' not in x.parts]
        if not candidates:raise RuntimeError('No scene output')
        source=max(candidates,key=lambda x:x.stat().st_mtime)
        run([FFMPEG,'-y','-v','error','-i',source,'-i',ROOT/beat['audio_file'],'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','160k','-t',str(beat['actual_duration_s']),'-movflags','+faststart',ROOT/'renders'/f"{beat['beat_id']}.mp4"],f"mux-{beat['beat_id']}")

def assemble():
    sheet=read_sheet()
    listing=ROOT/'renders/concat.txt'
    listing.write_text('\n'.join("file '"+b['beat_id']+".mp4'" for b in sheet['beats']),encoding='utf-8')
    # Concatenate PCM masters rather than independently encoded AAC segments.
    # Reset timestamps and force an exact constant-frame-rate video timeline.
    master=ROOT/'assets/audio/master.wav'
    with wave.open(str(master),'wb') as out:
        out.setnchannels(1);out.setsampwidth(2);out.setframerate(24000)
        for b in sheet['beats']:
            with wave.open(str(ROOT/b['audio_file']),'rb') as part:
                assert part.getframerate()==24000 and part.getnchannels()==1
                out.writeframes(part.readframes(part.getnframes()))
    target=sheet['metadata']['runtime_s'];frames=round(target*FPS)
    run([FFMPEG,'-y','-v','warning','-f','concat','-safe','0','-i',listing,'-i',master,
         '-map','0:v:0','-map','1:a:0','-vf',f'fps={FPS},tpad=stop_mode=clone:stop_duration=1,trim=end_frame={frames},setpts=N/({FPS}*TB)',
         '-af',f'apad,atrim=duration={target},asetpts=PTS-STARTPTS',
         '-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k',
         '-t',str(target),'-video_track_timescale','24000','-movflags','+faststart',ROOT/'Week01_Tokens_Not_Words.mp4'],'assemble')
    # Sidecar captions match actual synthesized segment boundaries, not word guesses.
    def stamp(seconds):
        ms=round(seconds*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
        return f'{h:02}:{m:02}:{s:02},{ms:03}'
    captions=[];n=1
    for b in sheet['beats']:
        for c in b['cues']:
            start=b['global_start_s']+c['start_s']
            captions.append(f"{n}\n{stamp(start)} --> {stamp(start+c['duration_s'])}\n{c['narration']}\n");n+=1
    (ROOT/'Week01_Tokens_Not_Words.srt').write_text('\n'.join(captions),encoding='utf-8')

def verify():
    movie=ROOT/'Week01_Tokens_Not_Words.mp4'
    data=json.loads(subprocess.check_output([FFPROBE,'-v','error','-show_format','-show_streams','-of','json',str(movie)],text=True))
    (ROOT/'evidence/ffprobe.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
    duration=float(data['format']['duration'])
    assert movie.stat().st_size>100000 and abs(duration-170)<0.025,duration
    assert {'video','audio'} <= {s['codec_type'] for s in data['streams']}
    run([FFMPEG,'-v','error','-i',movie,'-f','null','-'],'full-decode')
    run([FFMPEG,'-hide_banner','-i',movie,'-af','volumedetect','-vn','-f','null','-'],'audio-volume')
    from PIL import Image,ImageDraw
    qc=ROOT/'qc';qc.mkdir(exist_ok=True)
    samples=[]
    for b in read_sheet()['beats']:
        for frac in [.15,.50,.85]:
            t=b['global_start_s']+b['actual_duration_s']*frac
            file=qc/f"{b['beat_id']}-{int(frac*100)}.png"
            run([FFMPEG,'-y','-v','error','-ss',f'{t:.4f}','-i',movie,'-frames:v','1',file],f"frame-{b['beat_id']}-{int(frac*100)}")
            samples.append((file,b['beat_id'],t))
    canvas=Image.new('RGB',(1200,11*250),'#d8d4cf');draw=ImageDraw.Draw(canvas)
    for i,(file,bid,t) in enumerate(samples):
        im=Image.open(file).convert('RGB');im.thumbnail((400,225));x=(i%3)*400;y=(i//3)*250
        canvas.paste(im,(x,y));draw.text((x+8,y+228),f'{bid} | {t:.2f}s',fill='black')
    canvas.save(qc/'contact-sheet.jpg',quality=90)
    log(f'VERIFIED {duration:.3f}s; {movie.stat().st_size} bytes; audio+video; full decode passed')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['audio','fit','render','assemble','verify','all']);p.add_argument('--speed',type=float,default=1.25);p.add_argument('--only',nargs='+');a=p.parse_args()
    if a.stage in ('audio','all'):audio(a.speed,a.only)
    if a.stage in ('fit','all'):fit()
    if a.stage in ('render','all'):render(a.only)
    if a.stage in ('assemble','all'):assemble()
    if a.stage in ('verify','all'):verify()
