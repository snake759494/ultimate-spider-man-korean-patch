from pathlib import Path
import requests,hashlib,json,time
root=Path('work/asr_kotoba');root.mkdir(exist_ok=True)
base='https://huggingface.co/kotoba-tech/kotoba-whisper-v2.0-faster/resolve/main/'
manifest=[]
for name in ['config.json','preprocessor_config.json','tokenizer.json','vocabulary.json','model.bin']:
 dest=root/name
 if dest.exists():continue
 print('DOWNLOAD',name,flush=True);t=time.time();h=hashlib.sha256();n=0
 with requests.get(base+name,stream=True,timeout=(30,180)) as r:
  r.raise_for_status()
  with dest.with_suffix(dest.suffix+'.part').open('wb') as f:
   for chunk in r.iter_content(4*1024*1024):
    f.write(chunk);h.update(chunk);n+=len(chunk)
 dest.with_suffix(dest.suffix+'.part').replace(dest)
 manifest.append(dict(file=name,bytes=n,sha256=h.hexdigest(),url=base+name))
 print('DONE',name,n,round(time.time()-t,1),flush=True)
(root/'download_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
