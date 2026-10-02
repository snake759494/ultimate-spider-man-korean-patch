from pathlib import Path
import json
count=0
timing_path=Path('translation/voice_timing_overrides.json')
timings=json.loads(timing_path.read_text(encoding='utf-8')) if timing_path.exists() else {}
for line in Path('translation/voice_reviewed.tsv').read_text(encoding='utf-8').splitlines():
 h,ko=line.split('\t');files=list(Path('work/kotoba_review').glob(h+'.json'))
 if not files:files=list(Path('work/voice_audio').rglob(h+'.review.json'))
 if not files:continue
 assert len(files)==1
 d=json.loads(files[0].read_text(encoding='utf-8'));rows=d['segments'];assert rows,h
 d['segments']=[dict(start=max(0,min(r['start'] for r in rows)),end=min(d['duration'],max(r['end'] for r in rows)),jp=' '.join(r['jp'] for r in rows),ko=ko)]
 if h in timings:
  t=timings[h];assert 0<=t['start']<t['end']<=d['duration']
  d['segments'][0].update(start=t['start'],end=t['end']);d['timing_note']=t['reason']
 d['status']='translated_from_individual_asr_context_checked' if d.get('recognition','').endswith('_individual') else ('translated_from_kotoba_batch_context_checked_audio_review_required' if d.get('recognition','').startswith('kotoba') else 'translated_from_medium_batch_context_checked_audio_review_required')
 Path('translation/voice',h+'.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8');count+=1
print('Individual-source translations',count)
