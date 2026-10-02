from pathlib import Path
import json,subprocess,sys,iso
from faster_whisper import WhisperModel
rows=json.loads(Path('work/audio_inventory.json').read_text());wanted=set(sys.argv[1:]);tasks=[]
cli=next(Path('work/reference/vgmstream').rglob('vgmstream-cli.exe'))
sl=next(l for p,l,s,r in iso.walk() if p=='PACKS/SOUNDS.PAK')
for bank in rows:
 for i,s in enumerate(bank['streams']):
  h=f"{s['hash']:08x}"
  if h not in wanted:continue
  out=Path('work/voice_audio')/bank['name'];out.mkdir(parents=True,exist_ok=True);wbk=out/(bank['name']+'.wbk')
  if not wbk.exists():
   with open(iso.ISO,'rb') as f:f.seek(sl*2048+bank['offset']);wbk.write_bytes(f.read(bank['size']))
  wav=out/(h+'.wav')
  if not wav.exists():
   p=subprocess.run([str(cli),'-s',str(i+1),'-o',str(wav),str(wbk)],capture_output=True);assert p.returncode==0
  tasks.append((h,bank['name'],wav))
model=WhisperModel('work/asr_medium',device='cpu',compute_type='int8',cpu_threads=2,local_files_only=True)
for h,bank,wav in tasks:
 seg,info=model.transcribe(str(wav),language='ja',beam_size=5,vad_filter=True,condition_on_previous_text=False,word_timestamps=True)
 segments=[dict(start=s.start,end=s.end,jp=s.text,logprob=s.avg_logprob,no_speech=s.no_speech_prob) for s in seg]
 d=dict(hash=h,bank=bank,duration=info.duration,segments=segments,recognition='medium_individual')
 (wav.with_suffix('.review.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
 print(h,segments,flush=True)
