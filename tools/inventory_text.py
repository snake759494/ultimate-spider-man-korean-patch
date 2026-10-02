from pathlib import Path
import json,struct
found=[]
for p in Path('work/packs').glob('*.bin'):
 d=p.read_bytes();base=struct.unpack_from('<I',d,28)[0]
 for o in range(0x300,base-15,4):
  h,t,off,n=struct.unpack_from('<4I',d,o)
  if t not in (17,19,48) or not h or not n or base+off+n>len(d):continue
  raw=d[base+off:base+off+n]
  if t==17 and not raw.startswith(b'font'):continue
  if t==19 and sum(32<=v<127 or v in (0,9,10,13) for v in raw)/len(raw)<0.8:continue
  if t==48 and (n<16 or struct.unpack_from('<I',raw)[0]!=16):continue
  found.append(dict(pack=p.stem,type=t,offset=base+off,size=n,preview=raw[:60].hex()))
Path('work/text_inventory.json').write_text(json.dumps(found,indent=2))
print([(r['pack'],r['type'],r['size']) for r in found])
