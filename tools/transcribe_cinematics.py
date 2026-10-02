from pathlib import Path
import json,time,sys
from faster_whisper import WhisperModel
modelpath=sys.argv[1] if len(sys.argv)>1 else 'work/asr_model'
out=Path(sys.argv[2] if len(sys.argv)>2 else 'work/cinematics/asr');out.mkdir(exist_ok=True)
model=WhisperModel(modelpath,device='cpu',compute_type='int8',cpu_threads=2,local_files_only=True)
for p in Path('work/cinematics').glob('*.wav'):
 if any(x in p.name for x in ('LOGO','TAITO','ACTIVISION')):continue
 target=out/(p.stem+'.json')
 if target.exists():continue
 print('START',p.name,flush=True);t=time.time()
 seg,info=model.transcribe(str(p),language='ja',beam_size=5,vad_filter=True,condition_on_previous_text=False,word_timestamps=True)
 rows=[]
 for s in seg:
  r=dict(start=s.start,end=s.end,jp=s.text,logprob=s.avg_logprob,no_speech=s.no_speech_prob,words=[dict(start=w.start,end=w.end,text=w.word) for w in s.words])
  rows.append(r)
 target.write_text(json.dumps(dict(file=p.name,duration=info.duration,segments=rows),ensure_ascii=False,indent=2),encoding='utf-8')
 print('DONE',p.name,time.time()-t,flush=True)
