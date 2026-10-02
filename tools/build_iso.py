from pathlib import Path
import sys,json,struct,shutil,hashlib
sys.path.insert(0,'tools');import iso
src=Path('Ultimate Spider-Man (Japan).iso');dest=Path('build/Ultimate Spider-Man (Japan) [Korean-test].iso')
if not dest.exists():shutil.copyfile(src,dest)
with dest.open('r+b') as f:
 for name,l,s,_ in iso.walk():
  if name in ['PACKS/AMALGA.PAK','SLPM_664.04']:
   d=Path('build',Path(name).name).read_bytes();assert len(d)==s;f.seek(l*2048);f.write(d)
print(dest.resolve())
