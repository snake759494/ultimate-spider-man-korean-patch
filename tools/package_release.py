from pathlib import Path
import hashlib,json,shutil,zipfile
root=Path(__file__).resolve().parent.parent
release=root/'release'
v=json.loads((root/'build/verification.json').read_text())
patch=release/'Ultimate_Spider-Man_JP_KO_v0.9.xdelta'
v['patch_sha256']=hashlib.sha256(patch.read_bytes()).hexdigest()
v['patch_bytes']=patch.stat().st_size
with (root/'work/xdelta_roundtrip.iso').open('rb') as f:
 v['xdelta_apply_sha256']=hashlib.file_digest(f,'sha256').hexdigest()
v['xdelta_apply_matches_build']=v['xdelta_apply_sha256']==v['build_sha256']
assert v['xdelta_apply_matches_build']
(release/'verification.json').write_text(json.dumps(v,indent=2),encoding='utf-8')
for p in (root/'work/pcsx2/snaps').glob('*.png'):
 shutil.copyfile(p,release/'screenshots'/p.name)
with zipfile.ZipFile(root/'Ultimate_Spider-Man_KO_v0.9_patch.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in release.rglob('*'):
  if p.is_file():z.write(p,p.relative_to(root))
print(v['patch_bytes'],v['patch_sha256'])
