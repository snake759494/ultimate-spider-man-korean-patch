from pathlib import Path
import json,struct,subprocess,sys
import iso
out=Path('work/cinematics');out.mkdir(exist_ok=True)
ml=next(l for p,l,s,r in iso.walk() if p=='PACKS/MOVIES.PAK')
rows=json.loads(Path('work/movie_manifest.json').read_text())
manifest=[]
with open(iso.ISO,'rb') as f:
 for r in rows:
  f.seek(ml*2048+r['offset']);d=f.read(r['size'])
  if r['type']==31:
   name=d[0x20:0x40].split(b'\0')[0].decode('ascii');ext='wbk'
  else:name=f"{r['hash']:08x}";ext='ipu' if r['type']==32 else 'pss'
  p=out/f'{name}.{ext}';p.write_bytes(d)
  e=dict(r,name=name,path=str(p))
  if ext=='ipu':e.update(width=struct.unpack_from('<H',d,8)[0],height=struct.unpack_from('<H',d,10)[0],frames=struct.unpack_from('<I',d,12)[0])
  if ext=='wbk':
   cli=next(Path('work/reference/vgmstream').rglob('vgmstream-cli.exe'))
   proc=subprocess.run([str(cli),'-o',str(p.with_suffix('.wav')),str(p)],capture_output=True)
   e['decode_log']=proc.stdout.decode(errors='replace');assert proc.returncode==0,e
  manifest.append(e)
Path('work/cinematics/manifest.json').write_text(json.dumps(manifest,indent=2))
print([(r['name'],r.get('frames')) for r in manifest])
