from pathlib import Path
import json,re,unicodedata
known={l.split("\t")[0] for l in Path("translation/voice_reviewed.tsv").read_text(encoding="utf-8").splitlines() if l.strip()}
def norm(s):return re.sub(r'[\s!?！？。､、,….「」『』]+','',unicodedata.normalize('NFKC',s))
phrases={norm(l.split('\t')[0]) for p in Path('translation').glob('voice_dictionary*.tsv') for l in p.read_text(encoding='utf-8').splitlines() if l.strip()}
rows=[]
for p in Path("work/voice_audio").rglob("*.review.json"):
 h=p.name.split(".")[0]
 if h in known or Path("translation/voice",h+".json").exists():continue
 try:d=json.loads(p.read_text(encoding="utf-8"))
 except json.JSONDecodeError:continue
 s="".join(r["jp"] for r in d["segments"])
 if norm(s) in phrases:continue
 if len(s)>3 and not re.fullmatch(r"[あぁアァいぃイィうぅウゥえぇエェおぉオォんンっッー〜～!！?？、。…・ふフはハへヘほホひヒ゛\s]+",s):rows.append((p.stat().st_mtime,h,s))
for _,h,s in sorted(rows,reverse=True)[:100]:print(h+"\t"+s)
