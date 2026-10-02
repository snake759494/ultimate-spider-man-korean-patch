from pathlib import Path
import json,re,collections
def norm(s):return re.sub(r'\s+','',s).strip()
def nonverbal(s):return not s or bool(re.fullmatch(r'[あぁアァいぃイィうぅウゥえぇエェおぉオォんンっッー〜～!！?？、。…・ふフはハへヘほホ゛]+',s))
groups=collections.defaultdict(list)
for p in Path('work/voice_audio').rglob('*.json'):
 if p.name.endswith('.review.json'):continue
 d=json.loads(p.read_text(encoding='utf-8'));s=norm(''.join(r['jp'] for r in d['segments']))
 if nonverbal(s):continue
 groups[s].append(dict(hash=d['hash'],path=str(p),duration=d['duration']))
Path('work/voice_unique.json').write_text(json.dumps(groups,ensure_ascii=False,indent=2),encoding='utf-8')
print('lexical phrases',len(groups),'clips',sum(map(len,groups.values())))
for i,(s,rows) in enumerate(sorted(groups.items(),key=lambda t:(len(t[0]),t[0]))):print(i,s,len(rows))
