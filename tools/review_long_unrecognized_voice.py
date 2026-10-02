"""Second-model pass for unresolved clips, with explicit clip boundaries."""
from pathlib import Path
import json,re,time,sys
import numpy as np
from faster_whisper import WhisperModel
from faster_whisper.audio import decode_audio
root=Path('work/voice_audio/STREAMS_VOICE_JP')
roots=[root]
if '--all' in sys.argv:roots.insert(0,Path('work/voice_audio/STREAMS_MISC_JP'))
model=WhisperModel('work/asr_medium',device='cpu',compute_type='int8',cpu_threads=2,local_files_only=True)
batch=[];parts=[];length=0;done=0
def flush():
 global batch,parts,length,done
 if not batch:return
 t=time.time();segments,info=model.transcribe(np.concatenate(parts),language='ja',beam_size=3,temperature=0.0,vad_filter=True,condition_on_previous_text=False,word_timestamps=True,max_new_tokens=220,no_repeat_ngram_size=6)
 for s in segments:
  for w in s.words or []:
   def overlap(b):return max(0,min(w.end,b['offset']+b['duration'])-max(w.start,b['offset']))
   b=max(batch,key=overlap)
   if overlap(b)<=0:continue
   b['words'].append(dict(start=max(0,w.start-b['offset']),end=min(b['duration'],w.end-b['offset']),jp=w.word,prob=w.probability))
 for b in batch:
  p=b.pop('path');b.pop('offset');words=b.pop('words')
  b['segments']=[] if not words else [dict(start=min(w['start'] for w in words),end=max(w['end'] for w in words),jp=''.join(w['jp'] for w in words),words=words)]
  b['recognition']='medium_combined_word_alignment_review_required'
  b['recognition_settings']={'no_repeat_ngram_size':6,'note':'Repeated nonverbal ASR tokens are suppressed; listening review remains required.'}
  p.with_suffix('.review.json').write_text(json.dumps(b,ensure_ascii=False,indent=2),encoding='utf-8')
  done+=1
 print('REVIEWED',done,'clips',len(batch),'seconds',round(time.time()-t,1),flush=True)
 batch=[];parts=[];length=0
for p in sorted(p for folder in roots for p in folder.glob('*.json')):
 if p.name.endswith('.review.json') or Path('translation/voice',p.name).exists() or p.with_suffix('.review.json').exists():continue
 d=json.loads(p.read_text(encoding='utf-8'));s=''.join(r['jp'] for r in d['segments'])
 if d['duration']<(0 if '--all' in sys.argv else 2):continue
 a=decode_audio(str(p.with_suffix('.wav')),sampling_rate=16000);duration=len(a)/16000
 if length+duration>25:flush()
 batch.append(dict(hash=p.stem,bank=d['bank'],duration=duration,path=p,offset=length,words=[]));parts.extend([a,np.zeros(9600,np.float32)]);length+=duration+0.6
flush()
