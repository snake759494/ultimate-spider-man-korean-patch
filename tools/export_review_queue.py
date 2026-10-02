"""Export unresolved source evidence without equating recognition with review."""
from pathlib import Path
import csv,json,re,collections

rows=[]
for bank in ('STREAMS_MISC_JP','STREAMS_VOICE_JP'):
 for p in sorted(Path('work/voice_audio',bank).glob('*.json')):
  if p.name.endswith('.review.json') or Path('translation/voice',p.name).exists():continue
  d=json.loads(p.read_text(encoding='utf-8'))
  small=''.join(s['jp'] for s in d['segments'])
  rp=p.with_suffix('.review.json')
  review=''.join(s['jp'] for s in json.loads(rp.read_text(encoding='utf-8'))['segments']) if rp.exists() else ''
  kp=Path('work/kotoba_review',p.name)
  third=''.join(s['jp'] for s in json.loads(kp.read_text(encoding='utf-8'))['segments']) if kp.exists() else ''
  evidence=third or review or small
  kind='empty_recognition' if not evidence else ('nonverbal_candidate' if re.fullmatch(r'[あぁアァいぃイィうぅウゥえぇエェおぉオォんンっッー〜～!！?？、。…・ふフはハへヘほホひヒ゛\s]+',evidence) else 'lexical_or_unclear')
  rows.append(dict(bank=bank,hash=p.stem,duration=round(d['duration'],3),category=kind,first_pass=small,second_pass=review,third_pass=third,audio_path=str(p.with_suffix('.wav'))))
dest=Path('build/review_queue.tsv')
with dest.open('w',encoding='utf-8-sig',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=['bank','hash','duration','category','first_pass','second_pass','third_pass','audio_path'],delimiter='\t');writer.writeheader();writer.writerows(rows)
counts=collections.Counter(r['category'] for r in rows)
Path('build/review_queue_summary.json').write_text(json.dumps(dict(unresolved=len(rows),categories=dict(counts),note='ASR-based triage, not listening verification; empty/nonverbal candidates can still contain missed speech.'),ensure_ascii=False,indent=2),encoding='utf-8')
print(dict(counts))
