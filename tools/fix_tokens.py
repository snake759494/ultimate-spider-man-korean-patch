from pathlib import Path
import json,re
rows=json.loads(Path('translation/globaltext.json').read_text(encoding='utf-8'))
for r in rows:
 a=re.findall(r'%[a-zA-Z]|~[a-zA-Z0-9_]+',r['jp']);b=re.findall(r'%[a-zA-Z]|~[a-zA-Z0-9_]+',r['ko'])
 if a!=b:print(r['id'],a,b)
rows[543]['ko']='(점프! 1)\\n~cross 버튼으로 점프!\\n~cross 버튼을 오래 누를수록 더 높이 뛴다!'
Path('translation/globaltext.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
