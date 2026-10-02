"""Individually retry selected unresolved lexical clips with the larger model."""
from pathlib import Path
import json,time,shutil
from faster_whisper import WhisperModel

hashes=['cda4df4f','03978ed5','f36fdf8e','c47a42f1','a698604f','24725eeb',
 'f2a3d7dc','892d422f','bfb8a87e','55eab109','a119b553','b9d2e563',
 '2011d407','1790d165','153ba8c4','553f391d','18ddcabb','e3366572',
 '960cd3ee','9bfea6e6','f55db801','1f862f87','97d9ed91']
backup=Path('work/final_review');backup.mkdir(exist_ok=True)
model=WhisperModel('work/asr_large',device='cpu',compute_type='int8',cpu_threads=2,local_files_only=True)
for h in hashes:
 if Path('translation/voice',h+'.json').exists():continue
 files=list(Path('work/voice_audio').rglob(h+'.json'));assert len(files)==1,h
 p=files[0];review=p.with_suffix('.review.json')
 if review.exists() and json.loads(review.read_text(encoding='utf-8')).get('recognition')=='large_individual':continue
 if review.exists():shutil.copyfile(review,backup/(h+'.previous.json'))
 d=json.loads(p.read_text(encoding='utf-8'));t=time.time();print('START',h,flush=True)
 seg,info=model.transcribe(str(p.with_suffix('.wav')),language='ja',beam_size=5,temperature=0.0,vad_filter=False,condition_on_previous_text=False,word_timestamps=True,max_new_tokens=440)
 d['segments']=[dict(start=max(0,float(s.start)),end=min(d['duration'],float(s.end)),jp=s.text,logprob=s.avg_logprob,no_speech=s.no_speech_prob) for s in seg]
 d['recognition']='large_individual'
 review.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
 print('DONE',h,round(time.time()-t,1),' | '.join(s['jp'] for s in d['segments']),flush=True)
