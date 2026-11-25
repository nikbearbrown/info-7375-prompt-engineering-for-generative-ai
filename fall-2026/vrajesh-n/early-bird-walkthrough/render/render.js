// Render film.html frame by frame (window.seek(i/30)) into ffmpeg, and render the effects track.
// Usage: node render.js            -> ../out/video_silent.mp4 and ../out/effects.wav
const puppeteer = require('puppeteer-core');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const FPS = 30;
const out = path.resolve('../out');
fs.mkdirSync(out, { recursive: true });

(async () => {
  const b = await puppeteer.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: 'new', args: ['--no-sandbox', '--autoplay-policy=no-user-gesture-required'] });
  const p = await b.newPage(); await p.setViewport({ width: 1280, height: 900 });
  const errs = []; p.on('pageerror', (e) => errs.push(String(e)));
  await p.goto(require('url').pathToFileURL(path.resolve('../film.html')).href);
  await p.waitForFunction('window.__ready === true', { timeout: 60000 });
  const D = await p.evaluate(() => window.DURATION);
  const N = Math.ceil(D * FPS);

  // 1) effects (voiceover mix), as 16-bit stereo wav
  console.log('rendering effects...');
  const meta = await p.evaluate(async () => {
    const r = await SFX.render(window.scoreSound, window.DURATION, 48000, { voiceover: true });
    const i16 = new Int16Array(r.inter.length);
    for (let i = 0; i < r.inter.length; i++) i16[i] = Math.max(-32768, Math.min(32767, Math.round(r.inter[i] * 32767)));
    window.__pcm = new Uint8Array(i16.buffer);
    return { bytes: window.__pcm.length, peak: r.peak };
  });
  console.log('effects peak', meta.peak.toFixed(3));
  const chunks = [], CH = 3 * 1024 * 1024;
  for (let o = 0; o < meta.bytes; o += CH) {
    const b64 = await p.evaluate((o, CH) => { const a = window.__pcm.subarray(o, o + CH); let s = ''; for (let i = 0; i < a.length; i += 0x8000) s += String.fromCharCode.apply(null, a.subarray(i, i + 0x8000)); return btoa(s); }, o, CH);
    chunks.push(Buffer.from(b64, 'base64'));
  }
  const pcm = Buffer.concat(chunks), hdr = Buffer.alloc(44);
  hdr.write('RIFF', 0); hdr.writeUInt32LE(36 + pcm.length, 4); hdr.write('WAVEfmt ', 8); hdr.writeUInt32LE(16, 16); hdr.writeUInt16LE(1, 20); hdr.writeUInt16LE(2, 22);
  hdr.writeUInt32LE(48000, 24); hdr.writeUInt32LE(48000 * 4, 28); hdr.writeUInt16LE(4, 32); hdr.writeUInt16LE(16, 34); hdr.write('data', 36); hdr.writeUInt32LE(pcm.length, 40);
  fs.writeFileSync(path.join(out, 'effects.wav'), Buffer.concat([hdr, pcm]));

  // 2) frames
  console.log('rendering', N, 'frames...');
  const ff = spawn('ffmpeg', ['-y', '-f', 'image2pipe', '-framerate', String(FPS), '-vcodec', 'mjpeg', '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', String(FPS), path.join(out, 'video_silent.mp4')], { stdio: ['pipe', 'ignore', 'inherit'] });
  const t0 = Date.now();
  for (let i = 0; i < N; i++) {
    const b64 = await p.evaluate((t) => { window.seek(t); return document.getElementById('stage').toDataURL('image/jpeg', 0.95).split(',')[1]; }, i / FPS);
    if (!ff.stdin.write(Buffer.from(b64, 'base64'))) await new Promise((r) => ff.stdin.once('drain', r));
    if (i % 300 === 0) console.log('frame', i, '/', N, ((Date.now() - t0) / 1000).toFixed(0) + 's');
  }
  ff.stdin.end(); await new Promise((r) => ff.on('close', r));
  console.log('done', ((Date.now() - t0) / 1000).toFixed(0) + 's', 'page errors', errs);
  await b.close();
})();
