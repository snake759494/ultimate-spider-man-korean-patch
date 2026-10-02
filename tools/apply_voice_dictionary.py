"""Apply explicit translations while keeping recognition quality tracked."""
from pathlib import Path
import json,re,unicodedata
def norm(s):return re.sub(r'[\s!?！？。､、,….「」『』]+','',unicodedata.normalize('NFKC',s))
mapping={}
for path in sorted(Path('translation').glob('voice_dictionary*.tsv')):
 for line in path.read_text(encoding='utf-8').splitlines():
  jp,ko=line.split('\t');mapping[norm(jp)]=ko
out=Path('translation/voice');out.mkdir(exist_ok=True)
count=0
for p in Path('work/voice_audio').rglob('*.json'):
 if p.name.endswith('.review.json'):continue
 d=json.loads(p.read_text(encoding='utf-8'))
 jp=norm(''.join(r['jp'] for r in d['segments']))
 if jp not in mapping:continue
 target=out/(d['hash']+'.json')
 # A tiny word clipped at the bank boundary is not a reliable utterance.
 span=max(r['end'] for r in d['segments'])-min(r['start'] for r in d['segments'])
 if span<0.2:
  if target.exists() and json.loads(target.read_text(encoding='utf-8')).get('status')=='translated_batch_asr_review_required':target.unlink()
  continue
 if target.exists() and json.loads(target.read_text(encoding='utf-8')).get('status')!='translated_batch_asr_review_required':continue
 assert len(d['segments'])==1
 d['segments'][0]['ko']=mapping[jp]
 d['status']='translated_batch_asr_review_required'
 target.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8');count+=1
print('dictionary phrases',len(mapping),'matched clips',count)
reviewed=0
for p in Path('work/voice_audio').rglob('*.review.json'):
 d=json.loads(p.read_text(encoding='utf-8'));rows=d['segments']
 jp=norm(''.join(r['jp'] for r in rows))
 if jp not in mapping:continue
 target=out/(d['hash']+'.json')
 if target.exists() and json.loads(target.read_text(encoding='utf-8')).get('status') not in ('translated_batch_asr_review_required','translated_dictionary_individual_asr','translated_dictionary_medium_batch_review_required'):continue
 start=max(0,min(r['start'] for r in rows));end=min(d['duration'],max(r['end'] for r in rows))
 if end-start<0.2:
  if target.exists() and json.loads(target.read_text(encoding='utf-8')).get('status') in ('translated_dictionary_individual_asr','translated_dictionary_medium_batch_review_required'):target.unlink()
  continue
 d['segments']=[dict(start=start,end=end,jp=' '.join(r['jp'] for r in rows),ko=mapping[jp])]
 d['status']='translated_dictionary_individual_asr' if d.get('recognition','').endswith('_individual') else 'translated_dictionary_medium_batch_review_required'
 target.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8');reviewed+=1
print('second-pass ASR dictionary matches',reviewed)
