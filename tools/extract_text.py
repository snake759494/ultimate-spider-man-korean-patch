from pathlib import Path
import struct,json
p=Path('work/packs/GLOBALTEXT_JAPANESE.bin').read_bytes();b=0x340
h=struct.unpack_from('<4I',p,b);print(h)
rows=[]
for i in range((h[2]-h[0])//4):
 off=struct.unpack_from('<I',p,b+h[0]+i*4)[0]; start=b+h[2]+off
 if start>=0x7e1a: print('bad',i,hex(start));break
 raw=p[start:].split(b'\0')[0]
 rows.append(dict(id=i,offset=start,jp=raw.decode('cp932'),ko=''))
Path('translation/globaltext.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
Path('work/globaltext_dump.txt').write_text('\n'.join(f"{r['id']}\t{r['jp']}" for r in rows),encoding='utf-8')
print('count',len(rows));print('\n'.join(f"{r['id']}\t{r['jp']}" for r in rows[-30:]))
