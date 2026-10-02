"""Subtitle the promotional cards; preserve the original PS2 ADPCM PES audio."""
from pathlib import Path
import struct,subprocess,json,hashlib
import imageio_ffmpeg
out=Path('build/cinematics');out.mkdir(exist_ok=True)
cards=[(8.55,10.85,'모든 도시에는'),(14.8,16.8,'이야기가 있다'),(21.85,24.0,'모든 이야기에는'),(27.65,29.9,'영웅이 있다'),(32.0,34.2,'모든 영웅에게는'),(38.0,40.6,'적이 있다'),(58.0,60.8,'선과'),(61.7,63.0,'악'),(64.7,68.8,'양쪽 모두를 플레이하라'),(76.8,80.2,'궁극의 모험을 경험하라')]
def stamp(t):
 n=round(t*100);return f'{n//360000}:{n//6000%60:02}:{n//100%60:02}.{n%100:02}'
header='''[Script Info]
ScriptType: v4.00+
PlayResX: 512
PlayResY: 448
[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Default,NanumSquare Neo,23,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,2,0.7,2,24,24,26,1
[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
'''
ass=out/'attract.ass';ass.write_text(header+'\n'.join(f'Dialogue: 0,{stamp(a)},{stamp(b)},Default,,0,0,0,,{s}' for a,b,s in cards)+'\n',encoding='utf-8-sig')
src=Path('work/cinematics/41dab593.pss');video=out/'attract_video.ps'
cmd=[imageio_ffmpeg.get_ffmpeg_exe(),'-v','warning','-y','-i',str(src),'-vf',f'ass={ass.as_posix()}:fontsdir=.','-an','-c:v','mpeg2video','-threads','1','-g','15','-bf','0','-b:v','5000k','-maxrate','5000k','-bufsize','1835008','-muxrate','6000000','-muxpreload','0.192055','-muxdelay','0.7','-f','vob',str(video)]
p=subprocess.run(cmd,capture_output=True);(out/'attract.ffmpeg.log').write_bytes(p.stderr);assert p.returncode==0,p.stderr
def packets(data):
 i=0
 while i<len(data):
  assert data[i:i+3]==b'\0\0\1',(hex(i),data[i:i+12])
  tag=data[i+3]
  if tag==0xb9:n=4
  elif tag==0xba:n=14+(data[i+13]&7) if data[i+4]&0xc0==0x40 else 12
  else:n=6+int.from_bytes(data[i+4:i+6],'big')
  yield tag,data[i:i+n];i+=n
def pts(p):return ((p[0]>>1&7)<<30)|(p[1]<<22)|((p[2]>>1)<<15)|(p[3]<<7)|(p[4]>>1)
def packet_time(p,previous):return pts(p[9:14])/90000 if p[7]&0x80 else previous
original=list(packets(src.read_bytes()));audio=[];clock=0
for tag,p in original:
 if tag==0xbd:clock=packet_time(p,clock);audio.append((clock,p))
new=list(packets(video.read_bytes()));first=next(p for tag,p in new if tag==0xe0)
first_original=next(p for tag,p in original if tag==0xe0)
assert abs(packet_time(first,0)-packet_time(first_original,0))<0.04,(packet_time(first,0),packet_time(first_original,0))
result=bytearray();ai=0;clock=0
for tag,p in new:
 if tag==0xb9:continue
 if tag==0xbb:
  result.extend(next(b for t,b in original if t==0xbb));continue
 if tag==0xe0:
  clock=packet_time(p,clock)
  while ai<len(audio) and audio[ai][0]<=clock:
   result.extend(audio[ai][1]);ai+=1
 result.extend(p)
for _,p in audio[ai:]:result.extend(p)
result.extend(b'\0\0\1\xb9')
assert len(result)<=src.stat().st_size,(len(result),src.stat().st_size)
assert b''.join(p for t,p in packets(result) if t==0xbd)==b''.join(p for _,p in audio)
dest=out/'41dab593.pss';dest.write_bytes(result)
(out/'attract.quality.json').write_text(json.dumps(dict(bytes=len(result),original_bytes=src.stat().st_size,audio_packets=len(audio),audio_preserved=True,first_video_pts=packet_time(first,0),cards=len(cards)),indent=2))
print('PSS',len(result),'audio preserved',len(audio),'cards',len(cards))
# Retail PS2 playback needs the original 16 KiB pack layout.
import sys
subprocess.run([sys.executable,'tools/mux_attract_pss.py'],check=True)
