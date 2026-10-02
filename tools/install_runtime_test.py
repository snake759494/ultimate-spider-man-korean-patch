from pathlib import Path
import iso
dest=Path('build/Ultimate Spider-Man (Japan) [Korean-subtitle-test].iso')
name,l,size,_=next(r for r in iso.walk() if r[0]=='SLPM_664.04')
d=Path('build/runtime/SLPM_664.04').read_bytes();assert len(d)==size
with dest.open('r+b') as f:f.seek(l*2048);f.write(d)
print(dest)
