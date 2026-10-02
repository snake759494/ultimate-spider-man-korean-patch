"""Decode final IPU resources at representative subtitle frames for visual QA."""
from pathlib import Path
import json,subprocess,struct
from PIL import Image,ImageDraw
import imageio_ffmpeg
out=Path('work/cinematic_qa');out.mkdir(exist_ok=True)
samples=[]
for p in sorted(Path('translation/cinematics').glob('*.json')):
 d=json.loads(p.read_text(encoding='utf-8'));h=d['video_hash'];src=Path('build/cinematics',h+'.ipu')
 rows=[r for r in d['segments'] if r.get('ko')]
 picks=[max(rows,key=lambda r:len(r['ko'])),rows[len(rows)//2]]
 for i,r in enumerate(picks):
  frame=round((r['start']+r['end'])/2*30);dest=out/f'{h}_{i}.png'
  cmd=[imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-y','-r','30','-i',str(src),'-vf',rf'select=eq(n\,{frame})','-vsync','0','-frames:v','1',str(dest)]
  result=subprocess.run(cmd,capture_output=True);assert result.returncode==0,result.stderr
  assert dest.exists();samples.append((dest,r['ko'],frame))
for page in range((len(samples)+5)//6):
 im=Image.new('RGB',(1024,3*478),'#202020');draw=ImageDraw.Draw(im)
 for i,(p,ko,frame) in enumerate(samples[page*6:page*6+6]):
  x=i%2*512;y=i//2*478;im.paste(Image.open(p),(x,y));draw.text((x+8,y+451),f'{p.stem} frame {frame}',fill='white')
 im.save(out/f'page_{page+1}.jpg',quality=92)
(out/'samples.json').write_text(json.dumps([dict(path=str(p),ko=ko,frame=n) for p,ko,n in samples],ensure_ascii=False,indent=2),encoding='utf-8')
print('Decoded final IPU samples',len(samples))
