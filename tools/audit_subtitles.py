"""Audit actual source coverage and cue bounds without treating ASR as review."""
from pathlib import Path
import json,re,collections
mapping=json.loads(Path('translation/glyph_map_extended.json').read_text(encoding='utf-8'))
inventory=json.loads(Path('work/audio_inventory.json').read_text())
report={'banks':{},'translation_status':{},'issues':[]}
statuses=collections.Counter();seen={}
for folder in ('scenes','voice','cinematics'):
 for p in sorted(Path('translation',folder).glob('*.json')):
  d=json.loads(p.read_text(encoding='utf-8'));statuses[d.get('status','unmarked')]+=1
  if folder!='cinematics':
   assert d['hash'] not in seen,(p,seen.get(d['hash']))
   seen[d['hash']]=str(p)
  last=0
  for i,r in enumerate(d['segments']):
   if not r.get('ko'):continue
   assert 0<=r['start']<r['end']<=d['duration']+0.25,(p,i,r)
   assert r['start']>=last-0.05,(p,i,'overlapping cues')
   last=r['end']
   assert all(ord(c)<128 or c in mapping for c in r['ko']),(p,i,'missing glyph')
   if not r.get('jp'):report['issues'].append([str(p),i,'missing source text'])
   if len(r['ko'].replace('\n',''))/(r['end']-r['start'])>22:
    report['issues'].append([str(p),i,'fast subtitle'])
for name,folder in [('STREAMS_SCENE_JP','scenes'),('STREAMS_MISC_JP','voice'),('STREAMS_VOICE_JP','voice')]:
 bank=next(r for r in inventory if r['name']==name)
 rows=[]
 for stream in bank['streams']:
  h=f"{stream['hash']:08x}"
  src=Path('work/scene_audio/asr' if folder=='scenes' else 'work/voice_audio/'+name)/(h+'.json')
  tr=Path('translation',folder,h+'.json')
  status='not_transcribed'
  if src.exists():
   d=json.loads(src.read_text(encoding='utf-8'));text=''.join(r['jp'] for r in d['segments'])
   status='source_review_required' if text else 'no_speech_candidate'
  if tr.exists():
   t=json.loads(tr.read_text(encoding='utf-8'))
   status=t.get('status','unmarked') if any(r.get('ko') for r in t['segments']) or t.get('status','').startswith('no_caption_') else 'no_caption_candidate'
  rows.append({'hash':h,'status':status})
 report['banks'][name]={'total':len(rows),'counts':dict(collections.Counter(r['status'] for r in rows)),'clips':rows}
report['translation_status']=dict(statuses)
Path('build/subtitle_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:{'total':v['total'],'counts':v['counts']} for k,v in report['banks'].items()},ensure_ascii=False,indent=2))
print('Reading-speed/source issues:',len(report['issues']))
if report['issues']:
 raise SystemExit('Subtitle audit failed; inspect build/subtitle_audit.json before packaging.')
