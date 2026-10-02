from pathlib import Path
import json,sys,re
bank=sys.argv[1] if len(sys.argv)>1 else 'STREAMS_MISC_JP'
for p in sorted(Path('work/voice_audio',bank).glob('*.json')):
 if p.name.endswith('.review.json') or Path('translation/voice',p.name).exists():continue
 d=json.loads(p.read_text(encoding='utf-8'));s=''.join(r['jp'] for r in d['segments'])
 if s and not re.fullmatch(r'[あぁアァいぃイィうぅウゥえぇエェおぉオォんンっッー〜～!！?？、。…・ふフはハへヘほホ゛\s]+',s):print(p.stem,s)
