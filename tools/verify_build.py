"""Validate source/built ISO layout, permitted ranges, and every NFLC entry."""
from pathlib import Path
import hashlib,json,struct,lzokay,iso
root=Path(__file__).resolve().parent.parent
src=root/'Ultimate Spider-Man (Japan).iso'
dst=root/'build/Ultimate Spider-Man (Japan) [Korean-test].iso'
original=iso.walk(str(src)); patched=iso.walk(str(dst))
assert original==patched
assert src.stat().st_size==dst.stat().st_size
allowed=[(l*2048,l*2048+s,n) for n,l,s,_ in original if n in ('SLPM_664.04','PACKS/AMALGA.PAK')]
sh=hashlib.sha256();dh=hashlib.sha256();changed=0
with src.open('rb') as a,dst.open('rb') as b:
 pos=0
 while True:
  x=a.read(1048576);y=b.read(len(x))
  if not x:break
  sh.update(x);dh.update(y)
  if x!=y:
   for i,(u,v) in enumerate(zip(x,y)):
    if u!=v:
     assert any(lo<=pos+i<hi for lo,hi,_ in allowed),(pos+i,'unexpected ISO change')
     changed+=1
  pos+=len(x)
a=(root/'work/AMALGA.PAK').read_bytes();b=(root/'build/AMALGA.PAK').read_bytes()
records=json.loads((root/'work/pak_manifest.json').read_text())
modified=[]
for r in records:
 lo=r['offset'];hi=lo+r['size']
 if a[lo:hi]==b[lo:hi]:continue
 assert r['name'] in ('GAME','GLOBALTEXT_JAPANESE')
 n=struct.unpack_from('<I',b,lo+8)[0]&0x7fffffff
 raw=bytearray()
 for i in range(n):
  o=lo+i*32768
  assert b[o:o+4]==b'nFlC'
  assert struct.unpack_from('<H',b,o+6)[0]==i
  z=struct.unpack_from('<H',b,o+18)[0];u=struct.unpack_from('<I',b,o+24)[0]
  assert z<=32704
  raw.extend(lzokay.decompress(b[o+64:o+64+z],u))
 assert raw==(root/'build'/f"{r['name']}.bin").read_bytes()
 modified.append(r['name'])
assert sorted(modified)==['GAME','GLOBALTEXT_JAPANESE']
# Directory and any gaps/auxiliary streams must be byte-identical.
cursor=0
for lo,hi in sorted((r['offset'],r['offset']+r['size']) for r in records if r['name'] in modified):
 assert a[cursor:lo]==b[cursor:lo]
 cursor=hi
assert a[cursor:]==b[cursor:]
rows=json.loads((root/'translation/globaltext.json').read_text(encoding='utf-8'))
report=dict(source_sha256=sh.hexdigest(),build_sha256=dh.hexdigest(),iso_size=src.stat().st_size,
 iso_directory_identical=True,changed_bytes=changed,changed_files=[r[2] for r in allowed],
 archive_entries=len(records),modified_entries=modified,unchanged_entries=len(records)-len(modified),
 text_entries=len(rows),hangul_glyphs=len(json.loads((root/'translation/glyph_map.json').read_text(encoding='utf-8'))),
 compression_roundtrip=True)
(root/'build/verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
