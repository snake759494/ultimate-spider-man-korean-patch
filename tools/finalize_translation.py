from pathlib import Path
import json
p=Path('translation/globaltext.json');rows=json.loads(p.read_text(encoding='utf-8'))
rows[66]['ko']='슬롯%s의 %s에 공간이 부족합니다.\\n저장하려면 %dKB 이상의 빈 공간이 있는\\nPS2 메모리 카드(8MB)가 필요합니다.'
p.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
Path('translation/ko.tsv').write_text('\n'.join(str(r['id'])+'\t'+r['ko'] for r in rows)+'\n',encoding='utf-8')
