from pathlib import Path
import sys,re,struct
sys.path.insert(0,'tools');import iso
for p,l,s,_ in iso.walk():
 if p=='PACKS/SCNANIMS.PAK':
  d=iso.read(l,s);Path('work/SCNANIMS.PAK').write_bytes(d);print(d[:100].hex(' '));print(re.findall(rb'[ -~]{8,}',d)[:20])
