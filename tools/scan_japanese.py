from pathlib import Path
import re,json,struct
hits=[]
for f in Path('work/packs').glob('*.bin'):
 d=f.read_bytes();matches=[]
 for s in ['スパイダーマン','ヴェノム','ピーター','お前','エディ','です','なかった']:
  for m in re.finditer(re.escape(s.encode('cp932')),d):
   a=d.rfind(b'\0',0,m.start())+1;b=d.find(b'\0',m.end());raw=d[a:b]
   if len(raw)<1500:
    try:matches.append([a,raw.decode('cp932')])
    except:pass
 if matches:hits.append(dict(pack=f.stem,matches=matches))
Path('work/japanese_scan.json').write_text(json.dumps(hits,ensure_ascii=False,indent=2),encoding='utf-8');print([(r['pack'],len(r['matches'])) for r in hits])
p=Path('work/AMALGA.PAK').read_bytes();r=json.loads(Path('work/pak_manifest.json').read_text())
print('movies header')
import sys;sys.path.insert(0,'tools');import iso
for name,l,s,_ in iso.walk():
 if name=='PACKS/MOVIES.PAK':
  d=iso.read(l,0x10000);Path('work/movies_header.bin').write_bytes(d);print(d[:128].hex(' '));print(re.findall(rb'[ -~]{5,}',d)[:50])
