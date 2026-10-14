"""Data-driven Manim film. All IDs come from measured tokenizer output."""
import json, os
from pathlib import Path
import numpy as np
from manim import *
import manimpango

ROOT=Path(__file__).resolve().parent
font_file=ROOT/'assets/fonts/Lato-Regular.ttf'
if not font_file.exists():font_file=ROOT.parent/'brutalist.art/runtime/manim/fonts/Lato-Regular.ttf'
manimpango.register_font(str(font_file))
BG='#F5F0E8'; INK='#242220'; MUTED='#746F69'; ORANGE='#D35B21'; PINK='#AC285C'; TEAL='#197B70'; LIGHT='#DED6CA'
config.background_color=BG
config.frame_width=14.222222
config.frame_height=8
EVIDENCE=json.loads((ROOT/'evidence/tokenization.json').read_text(encoding='utf-8'))
SHEET=json.loads((ROOT/'beat_sheet.json').read_text(encoding='utf-8'))

def txt(s,size=30,color=INK,width=12.3):
    t=Text(str(s),font='Lato',font_size=size,color=color,disable_ligatures=True)
    if t.width>width:t.scale_to_fit_width(width)
    return t

def rowdata(enc='cl100k_base',word='strawberry'):
    return next(x for x in EVIDENCE['rows'] if x['encoding']==enc and x['text']==word)

def banner(s,y=-2.25,color=TEAL):
    label=txt(s,29,color,width=11.6)
    rect=RoundedRectangle(width=12.2,height=.65,corner_radius=.12,stroke_width=0,fill_color=color,fill_opacity=.08)
    return VGroup(rect,label).move_to([0,y,0])

def tokens(enc='cl100k_base',word='strawberry',y=.45,scale=1):
    data=rowdata(enc,word);items=[]
    for i,(part,tid) in enumerate(zip(data['fragments'],data['token_ids'])):
        color=[ORANGE,PINK,TEAL][i%3]
        box=RoundedRectangle(width=3.15,height=1.45,corner_radius=.12,color=color,stroke_width=2,fill_color=WHITE,fill_opacity=.45)
        label=txt(part,40,color,width=2.8).move_to(box.get_center()+UP*.2)
        num=txt(f'ID {tid}',23,MUTED).move_to(box.get_center()+DOWN*.4)
        items.append(VGroup(box,label,num))
    group=VGroup(*items).arrange(RIGHT,buff=.28).scale(scale).move_to([0,y,0])
    return group

def letters(word='strawberry',letter='r',y=.4,indices=True):
    items=[]
    for i,c in enumerate(word):
        color=PINK if c==letter else MUTED
        box=RoundedRectangle(width=.64,height=.76,corner_radius=.08,stroke_color=LIGHT,stroke_width=1,fill_color=WHITE,fill_opacity=.5)
        label=txt(c,34,color)
        item=VGroup(box,label)
        if indices:item.add(txt(i,15,MUTED).next_to(box,DOWN,buff=.15))
        items.append(item)
    return VGroup(*items).arrange(RIGHT,buff=.1).move_to([0,y,0])

class TokenFilm(Scene):
    @property
    def time(self):
        return self.renderer.time

    def construct(self):
        bid=os.environ.get('BEAT_ID','B00')
        self.beat=next(x for x in SHEET['beats'] if x['beat_id']==bid)
        b=self.beat
        eyebrow=txt('INFO 7375  /  FIELD NOTES 01',20,MUTED).to_corner(UL,buff=.48)
        folio=txt(f"{int(bid[1:])+1:02d} / {len(SHEET['beats']):02d}",20,MUTED).to_corner(UR,buff=.48)
        title=txt(b['title'],46).move_to([-6.2,2.65,0],aligned_edge=LEFT)
        rule=Line([-6.2,2.17,0],[6.2,2.17,0],color=LIGHT,stroke_width=2)
        footer=txt('TOKENS, NOT WORDS   /   LOCAL EVIDENCE + CONSTRUCTED TEACHING GRAPHICS',15,MUTED).move_to([0,-3.56,0])
        self.add(eyebrow,folio,title,rule,footer)
        getattr(self,b['kind'])()
        end=b['actual_duration_s']
        if self.time>end+.05:raise RuntimeError(f'Animation exceeds audio: {bid} {self.time} > {end}')
        if end>self.time:self.wait(end-self.time)

    def cue(self,i):
        target=self.beat['cues'][i]['start_s']
        if target>self.time:self.wait(target-self.time)

    def hook(self):
        word=letters(y=.75);question=txt('How many r\'s?',35).move_to([0,1.65,0])
        self.play(FadeIn(question),LaggedStart(*[FadeIn(c,shift=UP*.15) for c in word],lag_ratio=.08),run_time=1.2)
        answer=txt('3',90,PINK).move_to([0,-1,0])
        self.play(FadeIn(answer,scale=.6),run_time=.6)
        self.cue(1)
        self.play(FadeOut(answer),FadeOut(question),word.animate.shift(UP*.1),run_time=.7)
        count=txt(f"{rowdata()['character_length']} character positions",28,MUTED).move_to([0,-.55,0])
        chunks=VGroup(*[RoundedRectangle(width=2.2,height=.42,corner_radius=.05,fill_color=c,fill_opacity=.8,stroke_width=0) for c in [ORANGE,PINK,TEAL]]).arrange(RIGHT,buff=.2).move_to([0,-1.3,0])
        self.play(FadeIn(count),LaggedStart(*[FadeIn(c) for c in chunks],lag_ratio=.2),run_time=1)
        self.play(FadeIn(txt('3 token positions',28,MUTED).move_to([0,-1.95,0])),run_time=.5)
        self.cue(2);self.play(FadeIn(banner('Inspect the representation. Then check the count.',y=-2.7)),run_time=.6)

    def pipeline(self):
        raw=txt('"strawberry"',36,ORANGE).move_to([-4.35,.45,0])
        block=VGroup(RoundedRectangle(width=3.2,height=1.35,corner_radius=.12,color=PINK),txt('TOKENIZER',29,PINK)).move_to([0,.45,0])
        ids=VGroup(*[txt(str(x),29,TEAL) for x in rowdata()['token_ids']]).arrange(DOWN,buff=.15).move_to([4.35,.45,0])
        self.play(FadeIn(raw),run_time=.6)
        self.play(GrowArrow(Arrow([-2.8,.45,0],[-1.75,.45,0],buff=.05,color=MUTED)),FadeIn(block),run_time=.7)
        self.play(GrowArrow(Arrow([1.75,.45,0],[3.25,.45,0],buff=.05,color=MUTED)),LaggedStart(*[FadeIn(x) for x in ids],lag_ratio=.2),run_time=1)
        self.cue(1)
        self.play(FadeIn(txt('cl100k_base   /   o200k_base',33).move_to([0,-1.25,0])),run_time=.5)
        self.play(FadeIn(txt('Exact input: lowercase ASCII, no leading space',25,MUTED).move_to([0,-1.9,0])),run_time=.5)
        self.cue(2);self.play(FadeIn(banner('OpenAI encodings; NOT Claude tokenizer measurements.',-2.65,PINK)),run_time=.6)

    def cl100k(self):
        label=txt('cl100k_base  /  measured output',25,MUTED).move_to([0,1.55,0]);cards=tokens()
        self.play(FadeIn(label),LaggedStart(*[FadeIn(c,shift=DOWN*.3) for c in cards],lag_ratio=.35),run_time=1.7)
        self.cue(1)
        nums=VGroup(*[txt(str(c),52,[ORANGE,PINK,TEAL][i]).move_to([cards[i].get_x(),-1,0]) for i,c in enumerate(rowdata()['counts_per_fragment'])])
        self.play(LaggedStart(*[FadeIn(n) for n in nums],lag_ratio=.4),run_time=1.5)
        total=txt('r count:  1 + 0 + 2 = 3',34).move_to([0,-2,0]);self.play(FadeIn(total),run_time=.6)
        self.cue(2);self.play(FadeIn(banner('Token count and letter count are different quantities.',-2.8)),run_time=.6)

    def o200k(self):
        old=tokens(y=1.05,scale=.78);new=tokens('o200k_base',y=-.55,scale=.78)
        self.add(txt('cl100k_base',20,MUTED).move_to([-5.45,1.05,0]),old)
        self.play(FadeIn(txt('o200k_base',20,MUTED).move_to([-5.45,-.55,0])),TransformFromCopy(old,new),run_time=1.5)
        self.cue(1);self.play(FadeIn(txt('r count:  0 + 1 + 2 = 3',35,TEAL).move_to([0,-1.85,0])),run_time=.7)
        self.cue(2);self.play(FadeIn(banner('Different boundaries. Same recoverable spelling.',-2.7)),run_time=.7)

    def other_words(self):
        banana=letters('banana','a',y=1.1,indices=False)
        self.play(FadeIn(banana),run_time=.8)
        b1=rowdata('cl100k_base','banana')['token_ids'][0];b2=rowdata('o200k_base','banana')['token_ids'][0]
        details=txt(f'1 token   /   cl100k: {b1}   /   o200k: {b2}',28,MUTED).move_to([0,.15,0])
        banana_count=txt('3 a\'s',34,PINK).move_to([0,-.55,0])
        self.play(FadeIn(details),FadeIn(banana_count),run_time=.8)
        self.cue(1)
        self.play(*[FadeOut(m) for m in [banana,details,banana_count]],run_time=.5)
        c=tokens(word='occurrence',y=.75,scale=.85)
        self.play(FadeIn(c),run_time=.7)
        self.play(FadeIn(txt('cl100k_base',21,MUTED).move_to([0,1.65,0])),run_time=.3)
        oi=rowdata('o200k_base','occurrence')['token_ids']
        self.play(FadeIn(txt(f'o200k_base:  occ = {oi[0]}   /   urrence = {oi[1]}',26,MUTED).move_to([0,-.35,0])),FadeIn(txt('r count:  0 + 2 = 2',35,TEAL).move_to([0,-1.3,0])),run_time=.8)
        self.cue(2);self.play(FadeIn(banner('Counting chunks is not counting characters.',-2.5)),run_time=.6)

    def embedding(self):
        label=txt('CONSTRUCTED VECTORS  /  NOT MEASURED MODEL WEIGHTS',21,PINK).move_to([0,1.67,0])
        self.add(label)
        cards=tokens(y=.45,scale=.73)
        self.play(FadeIn(cards),run_time=.7)
        vectors=VGroup()
        for i,values in enumerate([['+0.2','-0.7','+0.4'],['-0.1','+0.8','+0.3'],['+0.6','+0.1','-0.5']]):
            x=cards[i].get_x();numbers=VGroup(*[txt(v,23,TEAL) for v in values]).arrange(DOWN,buff=.08).move_to([x,-1.45,0])
            rect=RoundedRectangle(width=1.9,height=1.28,corner_radius=.08,color=TEAL,stroke_width=1)
            rect.move_to(numbers);vectors.add(VGroup(rect,numbers))
        self.play(*[GrowArrow(Arrow([c.get_x(),-.2,0],[c.get_x(),-.7,0],buff=.02,color=MUTED)) for c in cards],run_time=.6)
        self.play(LaggedStart(*[FadeIn(v) for v in vectors],lag_ratio=.25),run_time=1)
        self.cue(1)
        # Replace the schematic with explicit index comparison.
        self.play(FadeOut(cards),FadeOut(vectors),*[FadeOut(m) for m in self.mobjects if isinstance(m,Arrow)],run_time=.5)
        chars=letters(y=.65);self.play(FadeIn(chars),run_time=.6)
        token_index=VGroup(*[txt(f'token position {i}',27,c) for i,c in enumerate([ORANGE,PINK,TEAL])]).arrange(RIGHT,buff=.7).move_to([0,-1,0])
        self.play(FadeOut(chars),FadeIn(token_index,shift=UP*.2),run_time=1)
        self.play(FadeIn(txt(f"{rowdata()['character_length']} character positions  /  {len(rowdata()['token_ids'])} token positions",32).move_to([0,.55,0])),run_time=.6)
        self.cue(2);self.play(FadeIn(banner('Different indexing does NOT prove spelling was erased.',-2.5)),run_time=.7)

    def lossless(self):
        c=tokens(y=.75,scale=.8);word=txt('strawberry',63,PINK).move_to([0,-.85,0])
        self.play(FadeIn(c),run_time=.7)
        self.play(TransformFromCopy(c,word),run_time=1.4)
        self.play(FadeIn(txt('DECODE  /  exact round trip',25,TEAL).move_to([0,-1.7,0])),run_time=.5)
        self.cue(1);checks=txt('6 / 6 round trips passed    •    6 / 6 count checks passed',28).move_to([0,1.75,0]);self.play(FadeIn(checks),run_time=.7)
        self.cue(2);self.play(FadeIn(banner('Less direct access ≠ lost characters.',-2.6)),run_time=.7)

    def prediction(self):
        self.add(txt('CONSTRUCTED PATHWAY COMPARISON  /  NO MODEL BENCHMARK',20,MUTED).move_to([0,1.6,0]))
        top=VGroup(txt('Token representations',29,ORANGE),Arrow(LEFT*.35,RIGHT*.35,buff=0,color=MUTED),txt('Predicted answer',29,PINK)).arrange(RIGHT,buff=.45).move_to([0,.6,0])
        bottom=VGroup(txt('Character sequence',29,TEAL),Arrow(LEFT*.35,RIGHT*.35,buff=0,color=MUTED),txt('Executed count',29,TEAL)).arrange(RIGHT,buff=.45).move_to([0,-.6,0])
        self.play(LaggedStart(*[FadeIn(x) for x in top],lag_ratio=.4),run_time=1.2)
        self.play(LaggedStart(*[FadeIn(x) for x in bottom],lag_ratio=.4),run_time=1.2)
        self.cue(1);self.play(FadeIn(txt('No failure rate measured. No fabricated model answer.',27,PINK).move_to([0,-1.65,0])),run_time=.7)
        self.cue(2);self.play(FadeIn(banner('Mechanism. Evidence. An appropriately narrow conclusion.',-2.65)),run_time=.7)

    def code(self):
        panel=RoundedRectangle(width=11.7,height=3.55,corner_radius=.18,fill_color=INK,fill_opacity=1,stroke_width=0).move_to([0,-.1,0]);self.add(panel)
        label=txt('PYTHON  /  RECORDED LOCAL OUTPUT',21,'#E7C7A8').move_to([-5.35,1.22,0],aligned_edge=LEFT);self.add(label)
        for i,(word,letter) in enumerate([('strawberry','r'),('banana','a'),('occurrence','r')]):
            y=.5-i*.82
            line=txt(f'"{word}".count("{letter}")',31,WHITE).move_to([-5.3,y,0],aligned_edge=LEFT)
            value=txt(str(rowdata(word=word)['character_count']),38,'#E6AE64').move_to([4.65,y,0])
            self.play(FadeIn(line),run_time=.6);self.play(FadeIn(value,shift=UP*.15),run_time=.4)
        self.cue(1);self.play(FadeIn(txt('Typeset reconstruction, not a live screen recording.',25,MUTED).move_to([0,-2.32,0])),run_time=.6)
        self.cue(2);self.play(FadeIn(txt('Run it. Inspect it. Then claim it.',28,TEAL).move_to([0,-2.95,0])),run_time=.6)

    def boundary(self):
        labels=['Correct answers are possible','Scratchpads can help; not a guarantee','Character-level views and tools can help']
        lines=VGroup(*[txt(x,31,TEAL).move_to([-5.8,1.2-i*.8,0],aligned_edge=LEFT) for i,x in enumerate(labels)])
        self.play(LaggedStart(*[FadeIn(x,shift=RIGHT*.2) for x in lines],lag_ratio=.5),run_time=1.8)
        self.cue(1);self.play(FadeIn(txt('Two encodings ≠ every model',31,PINK).move_to([0,-1.5,0])),run_time=.7)
        self.cue(2);self.play(FadeIn(banner('Token positions differ from character positions.',-2.55)),run_time=.7)

    def closing(self):
        steps=txt('Encode / inspect IDs / decode / count',33,TEAL).move_to([0,1.3,0]);self.play(FadeIn(steps),run_time=.7)
        word=letters(y=.05);self.play(LaggedStart(*[FadeIn(c) for c in word],lag_ratio=.07),run_time=1.1)
        self.cue(1);self.play(FadeIn(txt('A processing unit is not a spelling unit.',32).move_to([0,-1.15,0])),run_time=.7)
        self.cue(2);self.play(FadeIn(banner('strawberry  /  3 r\'s  /  verified locally',-2.3,PINK)),run_time=.8)
