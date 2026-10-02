from pathlib import Path
import json,time
from faster_whisper import WhisperModel
from faster_whisper.audio import decode_audio
out=Path('work/critical_review');out.mkdir(exist_ok=True)
tasks=[('fury_idiom','work/scene_audio/f71222d1.wav',61,72,'ja'),('fury_closing','work/scene_audio/f71222d1.wav',82,101,'ja'),('beetle_report','work/scene_audio/f71222d1.wav',20,30,'ja'),('radio_scene','work/scene_audio/80892268.wav',0,None,'ja'),('police_scene','work/scene_audio/88dd1e61.wav',0,None,'ja'),('sable_scene','work/scene_audio/4daf224d.wav',0,None,'ja'),('family_scene','work/scene_audio/e0395bdd.wav',0,None,'ja'),('attract','work/cinematics/attract.wav',0,None,None)]
for h in ['387d1688','c47a42f1','f36fdf8e','f9279bc3','df41ec74','22a9a68b']:
 tasks.append((h,str(next(Path('work/voice_audio').rglob(h+'.wav'))),0,None,'ja'))
model=WhisperModel('work/asr_large',device='cpu',compute_type='int8',cpu_threads=2,local_files_only=True)
for name,path,start,end,lang in tasks:
 dest=out/(name+'.json')
 if dest.exists():continue
 audio=decode_audio(path,sampling_rate=16000);clip=audio[round(start*16000):round(end*16000) if end else None]
 print('START',name,flush=True);t=time.time()
 segments,info=model.transcribe(clip,language=lang,beam_size=5,vad_filter=True,condition_on_previous_text=False,word_timestamps=True)
 rows=[dict(start=float(s.start+start),end=float(s.end+start),jp=s.text,logprob=s.avg_logprob,no_speech=s.no_speech_prob) for s in segments]
 dest.write_text(json.dumps(dict(name=name,source=path,language=info.language,segments=rows,model='large-v3'),ensure_ascii=False,indent=2),encoding='utf-8')
 print('DONE',name,round(time.time()-t,1),rows,flush=True)
