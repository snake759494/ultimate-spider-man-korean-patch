from pathlib import Path
import sys,re,struct,json
sys.path.insert(0,'tools')
import iso
rows=iso.walk()
Path('work/iso_manifest.json').write_text(json.dumps(rows,indent=2))
for p,l,s,r in rows:
 if p in ['SLPM_664.04','GAME.INI','SYSTEM.CNF','PACKS/AMALGA.PAK']:
  d=iso.read(l,s); Path('work',Path(p).name).write_bytes(d)
  print(p,s,d[:128].hex(' '))
d=Path('work/SLPM_664.04').read_bytes()
ss=[x.decode('ascii') for x in re.findall(rb'[ -~]{5,}',d)]
Path('work/elf_strings.txt').write_text('\n'.join(ss))
print('\n'.join(x for x in ss if any(t in x.lower() for t in ['font','amalga','.pak','.loc','.txt','japan','subtitle']) )[:16000])
