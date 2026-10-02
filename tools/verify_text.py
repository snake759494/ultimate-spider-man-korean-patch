from pathlib import Path
import json,re,struct,hashlib
rows=json.loads(Path('translation/globaltext.json').read_text(encoding='utf-8'));mp=json.loads(Path('translation/glyph_map.json').read_text(encoding='utf-8'));rev={v:k for k,v in mp.items()};p=Path('build/GLOBALTEXT_JAPANESE.bin').read_bytes();res=[]
for r in rows:
 start=0x1020+struct.unpack_from('<I',p,0x350+r['id']*4)[0];d=p[start:].split(b'\0')[0];s='';i=0
 while i<len(d):
  if d[i]>=128:code=int.from_bytes(d[i:i+2],'big');s+=rev[code];i+=2
  else:s+=chr(d[i]);i+=1
 assert s==r['ko'],r['id']
 line=max(len(re.sub(r'~\w+','O',x)) for x in s.split('\\n'))
 if '\\n' in s and line>30:res.append([r['id'],line,s])
print('Roundtrip 820/820; long manual lines',[(a,b) for a,b,c in res])
Path('work/long_lines.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8')
