"""Compare all bytes outside declared localization resources against the source."""
from pathlib import Path
import hashlib,json,struct,iso
src=Path(iso.ISO);dst=Path('build/Ultimate Spider-Man (Japan) [Korean-subtitle-test].iso')
entries={p:(l,n,r) for p,l,n,r in iso.walk()}
patched={p:(l,n,r) for p,l,n,r in iso.walk(str(dst))};assert patched.keys()==entries.keys()
ranges=[]
for name in ['SLPM_664.04','PACKS/AMALGA.PAK']:
 l,n,r=patched[name];ranges.append((l*2048,l*2048+n,name))
 if name=='PACKS/AMALGA.PAK':ranges.append((r+10,r+18,'AMALGA directory size'))
ml=entries['PACKS/MOVIES.PAK'][0]*2048
videos=[]
for i,r in enumerate(json.loads(Path('work/movie_manifest.json').read_text())):
 ext='ipu' if r['type']==32 else 'pss'
 p=Path('build/cinematics')/('%08x.%s'%(r['hash'],ext))
 if not p.exists():continue
 ranges.extend([(ml+r['offset'],ml+r['offset']+r['size'],p.name),(ml+0x308+i*16+12,ml+0x308+i*16+16,p.name+' size')]);videos.append(p.name)
ranges.sort();last=0;compared=0
with src.open('rb') as a,dst.open('rb') as b:
 for lo,hi,name in ranges:
  assert lo>=last,(name,lo,last)
  a.seek(last);b.seek(last);remaining=lo-last
  while remaining:
   n=min(4*1024*1024,remaining);x=a.read(n);y=b.read(n);assert x==y,(name,'unexpected preceding change',a.tell()-n)
   compared+=n;remaining-=n
  last=hi
 # Original tail and final disc sector must remain byte-identical.
 a.seek(last);b.seek(last)
 while x:=a.read(4*1024*1024):
  assert x==b.read(len(x)),'original disc tail changed';compared+=len(x)
 assert not b.read(1),'unexpected data after original disc size'
 l,n,_=entries['PACKS/AMALGA.PAK'];a.seek(l*2048+n)
 assert not any(a.read(patched['PACKS/AMALGA.PAK'][1]-n)),'expansion overwrote nonzero source padding'
for name,(l,n,r) in entries.items():assert patched[name][0]==l
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
report=dict(source_sha256=sha(src),build_sha256=sha(dst),source_bytes=src.stat().st_size,build_bytes=dst.stat().st_size,unchanged_bytes_compared=compared,all_file_lbas_preserved=True,modified_files=['SLPM_664.04','PACKS/AMALGA.PAK','PACKS/MOVIES.PAK'],modified_videos=videos,archive_expansion_only_overwrites_zero_padding=True,disc_tail_and_final_sector_preserved=True)
Path('build/extended_verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
