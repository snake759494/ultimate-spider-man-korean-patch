from pathlib import Path
import json,time
from faster_whisper import WhisperModel
out=Path('work/scene_audio/asr');out.mkdir(exist_ok=True)
model=WhisperModel('work/asr_medium',device='cpu',compute_type='int8',cpu_threads=2,local_files_only=True)
for p in Path('work/scene_audio').glob('*.wav'):
 target=out/(p.stem+'.json')
 if target.exists():continue
 print('START',p.name,flush=True);t=time.time()
 seg,info=model.transcribe(str(p),language='ja',beam_size=5,vad_filter=True,condition_on_previous_text=False,word_timestamps=True)
 rows=[dict(start=s.start,end=s.end,jp=s.text,logprob=s.avg_logprob,no_speech=s.no_speech_prob) for s in seg]
 target.write_text(json.dumps(dict(hash=p.stem,duration=info.duration,segments=rows),ensure_ascii=False,indent=2),encoding='utf-8')
 print('DONE',p.name,len(rows),round(time.time()-t,1),flush=True)
