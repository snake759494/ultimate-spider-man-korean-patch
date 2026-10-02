from pathlib import Path
import json,struct,shutil,iso
src=Path(iso.ISO)
dst=Path('build/Ultimate Spider-Man (Japan) [Korean-subtitle-test].iso')
if not dst.exists():shutil.copyfile(src,dst)
ml=next(l for p,l,s,r in iso.walk() if p=='PACKS/MOVIES.PAK')
manifest=json.loads(Path('work/movie_manifest.json').read_text())
with dst.open('r+b') as f:
 for i,r in enumerate(manifest):
  if r['type'] not in (32,33):continue
  ext='ipu' if r['type']==32 else 'pss'
  p=Path('build/cinematics')/f"{r['hash']:08x}.{ext}"
  if not p.exists():continue
  d=p.read_bytes();assert len(d)<=r['size'],(p,len(d),r['size'])
  f.seek(ml*2048+r['offset']);f.write(d);f.write(bytes(r['size']-len(d)))
  f.seek(ml*2048+0x308+i*16+12);f.write(struct.pack('<I',len(d)))
  print(p,len(d))
print(dst)
