from pathlib import Path
import json,struct,lzokay,hashlib,shutil
p=bytearray(Path('work/AMALGA.PAK').read_bytes());report=[]
for r in json.loads(Path('work/pak_manifest.json').read_text()):
 f=Path('build',r['name']+'.bin')
 if not f.exists():continue
 d=f.read_bytes();orig=Path('work/packs',r['name']+'.bin').read_bytes();assert len(d)==len(orig)
 chunks=[];off=0
 while off<len(d):
  lo=1;hi=min(131072,len(d)-off)//128;best=None
  while lo<=hi:
   mid=(lo+hi)//2;raw=d[off:off+mid*128];comp=lzokay.compress(raw)
   if len(comp)<=32704:best=(raw,comp);lo=mid+1
   else:hi=mid-1
  assert best
  chunks.append(best);off+=len(best[0])
 assert len(chunks)*32768<=r['size'],(r['name'],len(chunks),r['size'])
 total=sum(len(c) for u,c in chunks);uz=cz=0;out=bytearray()
 for i,(u,c) in enumerate(chunks):
  h=bytearray(64);h[:4]=b'nFlC';struct.pack_into('<HHII',h,4,0x101,i,0x80000000|len(chunks),(0x80000000 if i<len(chunks)-1 else 0)|(0x8000 if i else 0))
  struct.pack_into('<HH7I',h,16,0x901,len(c),0,len(u),0,total,cz,len(d),uz)
  out.extend(h+c+bytes(32768-64-len(c)));uz+=len(u);cz+=len(c)
 out.extend(bytes(r['size']-len(out)))
 # Validate exact round trip for every block before writing.
 decoded=b''.join(lzokay.decompress(bytes(out[i*32768+64:i*32768+64+len(c)]),len(u)) for i,(u,c) in enumerate(chunks));assert decoded==d
 p[r['offset']:r['offset']+r['size']]=out
 report.append(dict(pack=r['name'],blocks=len(chunks),compressed=total,reserved=r['size'],sha256=hashlib.sha256(d).hexdigest(),checksum_fields='zero; consult release QA report for runtime verification'))
Path('build/AMALGA.PAK').write_bytes(p);Path('build/resource_build.json').write_text(json.dumps(report,indent=2));print(report)

