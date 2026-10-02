from pathlib import Path
import struct,sys,json,subprocess,imageio_ffmpeg
sys.path.insert(0,'tools');import iso
rows=iso.walk();ml=next(l for p,l,s,_ in rows if p=='PACKS/MOVIES.PAK');d=Path('work/movies_header.bin').read_bytes();records=[]
Path('work/movies').mkdir(exist_ok=True)
for o in range(0x308,0x478,16):
 h,t,off,sz=struct.unpack_from('<4I',d,o);records.append(dict(hash=h,type=t,offset=off+0x8000,size=sz))
 if t==32:
  head=iso.read(ml,0) if False else None
  with open(iso.ISO,'rb') as f:f.seek(ml*2048+off+0x8000);head=f.read(min(sz,10_000_000))
  fp=Path('work/movies',f'{h:08x}.pss');fp.write_bytes(head)
  print(hex(h),sz,head[:16].hex(' '))
  subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-y','-i',str(fp),'-vf','select=eq(n\\,120)','-frames:v','1',str(fp.with_suffix('.png'))],capture_output=True)
Path('work/movie_manifest.json').write_text(json.dumps(records,indent=2))
