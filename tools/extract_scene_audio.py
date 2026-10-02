from pathlib import Path
import json,subprocess,iso
rows=json.loads(Path('work/audio_inventory.json').read_text())
r=next(r for r in rows if r['name']=='STREAMS_SCENE_JP')
sl=next(l for p,l,s,r in iso.walk() if p=='PACKS/SOUNDS.PAK')
out=Path('work/scene_audio');out.mkdir(exist_ok=True)
bank=out/'STREAMS_SCENE_JP.wbk'
with open(iso.ISO,'rb') as f:f.seek(sl*2048+r['offset']);bank.write_bytes(f.read(r['size']))
cli=next(Path('work/reference/vgmstream').rglob('vgmstream-cli.exe'))
for i,s in enumerate(r['streams']):
 dest=out/f"{s['hash']:08x}.wav"
 if dest.exists():continue
 p=subprocess.run([str(cli),'-s',str(i+1),'-o',str(dest),str(bank)],capture_output=True)
 assert p.returncode==0,p.stderr
print('scene streams',len(r['streams']))
