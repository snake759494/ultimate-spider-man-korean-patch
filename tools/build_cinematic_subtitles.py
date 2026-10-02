from pathlib import Path
import json,subprocess,struct,textwrap,imageio_ffmpeg,sys
from PIL import ImageFont
FF=imageio_ffmpeg.get_ffmpeg_exe()
IPU='work/reference/IPUenc/IPUenc/bin/Release/net6.0/IPUenc.dll'
out=Path('build/cinematics');out.mkdir(exist_ok=True)
font=ImageFont.truetype('NanumSquareNeo-cBd.ttf',21)
def wrap(s):
 lines=[];line=''
 for word in s.split():
  new=(line+' '+word).strip()
  if font.getlength(new)>464 and line:lines.append(line);line=word
  else:line=new
 if line:lines.append(line)
 assert len(lines)<=2,(s,lines)
 return '\\N'.join(lines)
def stamp(t):
 cs=round(t*100);return f'{cs//360000}:{cs//6000%60:02}:{cs//100%60:02}.{cs%100:02}'
for p in Path('translation/cinematics').glob('*.json'):
 data=json.loads(p.read_text(encoding='utf-8'));h=data['video_hash'];ass=out/f'{h}.ass'
 if len(sys.argv)>1 and h not in sys.argv[1:]:continue
 header='''[Script Info]
ScriptType: v4.00+
PlayResX: 512
PlayResY: 448
WrapStyle: 2
[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Default,NanumSquare Neo,21,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,1.7,0.6,2,24,24,22,1
[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
'''
 events=[]
 for r in data['segments']:
  if not r.get('ko'):continue
  assert r['end']>r['start']
  events.append(f"Dialogue: 0,{stamp(r['start'])},{stamp(r['end'])},Default,,0,0,0,,{wrap(r['ko'])}")
 ass.write_text(header+'\n'.join(events)+'\n',encoding='utf-8-sig')
 src=Path('work/cinematics')/f'{h}.ipu';m2v=out/f'{h}.m2v';dest=out/f'{h}.ipu'
 # IPU carries frames, not a reliable playback-rate tag. This NTSC game plays
 # cinematic frames at 30fps; preserve the exact original frame count.
 frames=struct.unpack_from('<I',src.read_bytes(),12)[0]
 for quality in range(2,8):
  cmd=[FF,'-v','warning','-y','-r','30','-i',str(src),'-vf',f"ass={ass.as_posix()}:fontsdir=.",'-an','-c:v','mpeg2video','-g','1','-bf','0','-q:v',str(quality),'-pix_fmt','yuv420p','-frames:v',str(frames),'-f','mpeg2video',str(m2v)]
  log=subprocess.run(cmd,capture_output=True);(out/f'{h}.ffmpeg.log').write_bytes(log.stderr);assert log.returncode==0,log.stderr
  log=subprocess.run(['dotnet',IPU,'-encode','-mode1',str(m2v),str(dest)],capture_output=True)
  (out/f'{h}.ipuenc.log').write_bytes(log.stdout+log.stderr);assert log.returncode==0,log.stderr
  if dest.stat().st_size<=src.stat().st_size:break
 assert dest.stat().st_size<=src.stat().st_size
 (out/f'{h}.quality.json').write_text(json.dumps(dict(quantizer=quality,original=src.stat().st_size,patched=dest.stat().st_size,frames=frames)))
 assert struct.unpack_from('<I',dest.read_bytes(),12)[0]==frames
 print(h,frames,src.stat().st_size,dest.stat().st_size,flush=True)
