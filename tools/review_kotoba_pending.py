"""Individual Japanese-specialized review; --all includes unresolved clips.
Word alignment is disabled: the upstream two-layer model has invalid alignment
head indices in config.json. File boundaries remain exact; no clips are joined.
"""
from pathlib import Path
import json,time,sys
from faster_whisper import WhisperModel

out=Path('work/kotoba_review');out.mkdir(exist_ok=True)
model=WhisperModel('work/asr_kotoba',device='cpu',compute_type='int8',cpu_threads=2,local_files_only=True)
priority=['cda4df4f','03978ed5','f36fdf8e','c47a42f1','a698604f','24725eeb','f2a3d7dc',
 '892d422f','bfb8a87e','55eab109','a119b553','b9d2e563','2011d407','1790d165',
 '153ba8c4','553f391d','18ddcabb','e3366572','960cd3ee','1f862f87','97d9ed91']
priority+=['f9346278','e3268540','e3146cbf','f6fba282','0ff04051']
if '--hashes' in sys.argv:priority=sys.argv[sys.argv.index('--hashes')+1].split(',')
paths={}
for bank in ('STREAMS_MISC_JP','STREAMS_VOICE_JP'):
 for p in Path('work/voice_audio',bank).glob('*.json'):
  if not p.name.endswith('.review.json'):paths[p.stem]=p
done=0
if '--all' in sys.argv:
 priority+=sorted(h for h,p in paths.items() if not Path('translation/voice',p.name).exists() and h not in priority)
for h in priority:
 p=paths[h]
 if (out/p.name).exists():continue
 d=json.loads(p.read_text(encoding='utf-8'));t=time.time()
 segments,info=model.transcribe(str(p.with_suffix('.wav')),language='ja',beam_size=3,temperature=0.0,vad_filter=False,condition_on_previous_text=False,word_timestamps=False,chunk_length=15,max_new_tokens=220)
 d['segments']=[dict(start=max(0,float(s.start)),end=min(d['duration'],float(s.end)),jp=s.text,logprob=s.avg_logprob,no_speech=s.no_speech_prob) for s in segments]
 d['recognition']='kotoba_individual'
 (out/p.name).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8');done+=1
 print('INDIVIDUAL',h,round(time.time()-t,1),' | '.join(s['jp'] for s in d['segments']),flush=True)

