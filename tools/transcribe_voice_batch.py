from pathlib import Path
import json,subprocess,time,wave,hashlib
import numpy as np
from faster_whisper import WhisperModel
from faster_whisper.audio import decode_audio
rows=json.loads(Path('work/audio_inventory.json').read_text())
cli=next(Path('work/reference/vgmstream').rglob('vgmstream-cli.exe'))
model=WhisperModel('work/asr_model',device='cpu',compute_type='int8',cpu_threads=2,local_files_only=True)
for name in ['STREAMS_MISC_JP','STREAMS_VOICE_JP']:
 r=next(r for r in rows if r['name']==name);out=Path('work/voice_audio')/name;out.mkdir(parents=True,exist_ok=True)
 bank=out/(name+'.wbk')
 if not bank.exists():
  import iso
  sl=next(l for p,l,s,r in iso.walk() if p=='PACKS/SOUNDS.PAK')
  with open(iso.ISO,'rb') as f:f.seek(sl*2048+r['offset']);bank.write_bytes(f.read(r['size']))
 batch=[];parts=[];length=0;batch_num=0
 def flush():
  global batch,parts,length,batch_num
  if not batch:return
  t=time.time();audio=np.concatenate(parts)
  print('START',name,len(batch),round(length,1),flush=True)
  seg,info=model.transcribe(audio,language='ja',beam_size=3,temperature=0.0,vad_filter=True,condition_on_previous_text=False,word_timestamps=True,max_new_tokens=200)
  for s in seg:
   for w in s.words or []:
    def overlap(b):return max(0,min(w.end,b['offset']+b['duration'])-max(w.start,b['offset']))
    clip=max(batch,key=overlap)
    if overlap(clip)<=0:continue
    clip['words'].append(dict(start=max(0,w.start-clip['offset']),end=min(clip['duration'],w.end-clip['offset']),jp=w.word,prob=w.probability))
  for b in batch:
   words=b.pop('words');offset=b.pop('offset');segments=[]
   if words:segments=[dict(start=min(w['start'] for w in words),end=max(w['end'] for w in words),jp=''.join(w['jp'] for w in words),words=words)]
   b['segments']=segments;b['recognition']='small_combined_word_alignment_review_required'
   (out/(b['hash']+'.json')).write_text(json.dumps(b,ensure_ascii=False,indent=2),encoding='utf-8')
  batch_num+=1;print(name,'batch',batch_num,'clips',len(batch),'seconds',round(length,1),'elapsed',round(time.time()-t,1),flush=True)
  batch=[];parts=[];length=0
 for i,s in enumerate(r['streams']):
  h=f"{s['hash']:08x}";target=out/(h+'.json')
  if target.exists():continue
  wav=out/(h+'.wav')
  if not wav.exists():
   p=subprocess.run([str(cli),'-s',str(i+1),'-o',str(wav),str(bank)],capture_output=True);assert p.returncode==0,p.stderr
  a=decode_audio(str(wav),sampling_rate=16000);dur=len(a)/16000
  if length+dur>27:flush()
  batch.append(dict(hash=h,bank=name,duration=dur,offset=length,words=[]));parts.extend([a,np.zeros(6400,np.float32)]);length+=dur+0.4
 flush()
