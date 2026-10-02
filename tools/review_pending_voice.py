"""Individually recheck uncaptioned lexical fragments; resume safely per clip."""
from pathlib import Path
import json,re,time
from faster_whisper import WhisperModel
root=Path('work/voice_audio/STREAMS_VOICE_JP')
model=WhisperModel('work/asr_medium',device='cpu',compute_type='int8',cpu_threads=1,local_files_only=True)
tasks=[]
for p in root.glob('*.json'):
 if p.name.endswith('.review.json') or Path('translation/voice',p.name).exists() or p.with_suffix('.review.json').exists():continue
 d=json.loads(p.read_text(encoding='utf-8'));text=''.join(s['jp'] for s in d['segments'])
 if not text or re.fullmatch(r'[あぁアァいぃイィうぅウゥえぇエェおぉオォんンっッー〜～!！?？、。…・ふフはハへヘほホ゛\s]+',text):continue
 tasks.append((p,d))
# Longer lexical lines first, then fragments that might have lost a word.
tasks.sort(key=lambda t:-len(''.join(s['jp'] for s in t[1]['segments'])))
for i,(p,d) in enumerate(tasks):
 if Path('translation/voice',p.name).exists():continue
 t=time.time();seg,info=model.transcribe(str(p.with_suffix('.wav')),language='ja',beam_size=3,vad_filter=True,condition_on_previous_text=False)
 d['segments']=[dict(start=float(s.start),end=float(s.end),jp=s.text,logprob=s.avg_logprob,no_speech=s.no_speech_prob) for s in seg]
 d['recognition']='medium_individual'
 p.with_suffix('.review.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
 print(i+1,len(tasks),p.stem,round(time.time()-t,1),' | '.join(s['jp'] for s in d['segments']),flush=True)
