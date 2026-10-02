from pathlib import Path
import json,subprocess,time,iso
from faster_whisper import WhisperModel
rows=json.loads(Path('work/audio_inventory.json').read_text())
sl=next(l for p,l,s,r in iso.walk() if p=='PACKS/SOUNDS.PAK')
cli=next(Path('work/reference/vgmstream').rglob('vgmstream-cli.exe'))
model=WhisperModel('work/asr_medium',device='cpu',compute_type='int8',cpu_threads=2,local_files_only=True)
for name in ['STREAMS_VOICE_JP','STREAMS_MISC_JP']:
 r=next(r for r in rows if r['name']==name);out=Path('work/voice_audio')/name;out.mkdir(parents=True,exist_ok=True)
 bank=out/(name+'.wbk')
 if not bank.exists():
  with open(iso.ISO,'rb') as f:f.seek(sl*2048+r['offset']);bank.write_bytes(f.read(r['size']))
 for i,s in enumerate(r['streams']):
  target=out/f"{s['hash']:08x}.json"
  if target.exists():continue
  wav=out/f"{s['hash']:08x}.wav"
  if not wav.exists():
   p=subprocess.run([str(cli),'-s',str(i+1),'-o',str(wav),str(bank)],capture_output=True);assert p.returncode==0,p.stderr
  t=time.time();seg,info=model.transcribe(str(wav),language='ja',beam_size=3,vad_filter=True,condition_on_previous_text=False)
  segments=[dict(start=x.start,end=x.end,jp=x.text,logprob=x.avg_logprob,no_speech=x.no_speech_prob) for x in seg]
  target.write_text(json.dumps(dict(hash=f"{s['hash']:08x}",bank=name,duration=info.duration,segments=segments),ensure_ascii=False,indent=2),encoding='utf-8')
  print(name,i+1,len(r['streams']),s['hash'],len(segments),round(time.time()-t,1),flush=True)
