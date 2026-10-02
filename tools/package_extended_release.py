"""Create a separate, hash-verified subtitle build without touching v0.9."""
from pathlib import Path
import hashlib,json,subprocess,shutil,zipfile,sys

root=Path(__file__).resolve().parent.parent
source=root/'Ultimate Spider-Man (Japan).iso'
build=root/'build/Ultimate Spider-Man (Japan) [Korean-subtitle-test].iso'
release=root/'release_extended'
release.mkdir(exist_ok=True)
patch=release/'Ultimate_Spider-Man_JP_KO_subtitles.xdelta'
roundtrip=root/'work/extended_xdelta_roundtrip.iso'
xdelta=root/'xdelta.exe'
def sha(path):
 with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
report=json.loads((root/'build/extended_verification.json').read_text())
runtime_test=json.loads((root/'build/runtime_tests.json').read_text())
assert runtime_test['passed'] and runtime_test['source_sha256']==sha(root/'tools/subtitle_runtime.c')
assert not json.loads((root/'build/subtitle_audit.json').read_text(encoding='utf-8'))['issues']
assert json.loads((root/'build/caption_layout_verification.json').read_text())['all_glyphs_within_viewport']
assert sha(source)==report['source_sha256']
assert sha(build)==report['build_sha256']
if '--reuse-verified-patch' in sys.argv:
 old=json.loads((release/'verification.json').read_text())
 assert old['xdelta_apply_matches_build']
 assert old['source_sha256']==report['source_sha256'] and old['build_sha256']==report['build_sha256']
 assert sha(patch)==old['patch_sha256']
 print('Reusing the already verified patch; checking decoded ISO hash again...',flush=True)
else:
 print('Creating xdelta patch...',flush=True)
 subprocess.run([str(xdelta),'-f','-e','-6','-B','67108864','-W','8388608','-s',str(source),str(build),str(patch)],check=True)
 print('Reapplying patch to original ISO...',flush=True)
 subprocess.run([str(xdelta),'-f','-d','-s',str(source),str(patch),str(roundtrip)],check=True)
report['patch_sha256']=sha(patch)
report['patch_bytes']=patch.stat().st_size
report['xdelta_apply_sha256']=sha(roundtrip)
report['xdelta_apply_matches_build']=report['xdelta_apply_sha256']==report['build_sha256']
assert report['xdelta_apply_matches_build']
(release/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
table=json.loads((root/'build/subtitle_table.json').read_text())
queue=json.loads((root/'build/review_queue_summary.json').read_text(encoding='utf-8'))
audit=json.loads((root/'build/subtitle_audit.json').read_text(encoding='utf-8'))
shutil.copyfile(root/'build/subtitle_audit.json',release/'subtitle_audit.json')
shutil.copyfile(root/'build/runtime_tests.json',release/'runtime_tests.json')
shutil.copyfile(root/'build/runtime_smoke_qa.json',release/'runtime_smoke_qa.json')
shutil.copyfile(root/'build/review_queue.tsv',release/'review_queue.tsv')
shutil.copyfile(root/'build/review_queue_summary.json',release/'review_queue_summary.json')
shutil.copyfile(root/'COMPLETION_PLAN.txt',release/'제작_검증_기록.txt')
shutil.copyfile(root/'translation/용어_기준.txt',release/'용어_기준.txt')
font_selection=json.loads((root/'build/font_selection.json').read_text(encoding='utf-8'))
assert font_selection['sha256']==sha(root/font_selection['selected_font'])
shutil.copyfile(root/'build/font_selection.json',release/'font_selection.json')
shutil.copyfile(root/'work/font_comparison.png',release/'글꼴_비교.png')
shutil.copyfile(root/'build/caption_layout_verification.json',release/'caption_layout_verification.json')
shutil.copyfile(root/'build/caption_layout_proof.png',release/'자막_배치_검사.png')
apply=r'''param(
    [Parameter(Mandatory=$true)][string]$SourceIso,
    [string]$OutputIso = '',
    [string]$Xdelta = ''
)
$ErrorActionPreference = 'Stop'
if (-not $OutputIso) { $OutputIso = Join-Path $PSScriptRoot 'Ultimate Spider-Man (Japan) [Korean subtitles].iso' }
if (-not $Xdelta) { $Xdelta = Join-Path $PSScriptRoot '..\xdelta.exe' }
if (Test-Path -LiteralPath $OutputIso) { throw '출력 파일이 이미 있습니다. 다른 OutputIso 경로를 지정하세요.' }
$expected = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'verification.json') -Raw | ConvertFrom-Json
$sourceHash = (Get-FileHash -LiteralPath $SourceIso -Algorithm SHA256).Hash.ToLowerInvariant()
if ($sourceHash -ne $expected.source_sha256) { throw '지원하는 원본 ISO가 아닙니다. SHA-256이 다릅니다.' }
$patch = Join-Path $PSScriptRoot 'Ultimate_Spider-Man_JP_KO_subtitles.xdelta'
if ((Get-FileHash -LiteralPath $patch -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expected.patch_sha256) { throw '패치 파일의 SHA-256이 다릅니다.' }
& $Xdelta -d -s $SourceIso $patch $OutputIso
if ($LASTEXITCODE -ne 0) { throw 'xdelta failed.' }
$outputHash = (Get-FileHash -LiteralPath $OutputIso -Algorithm SHA256).Hash.ToLowerInvariant()
if ($outputHash -ne $expected.build_sha256) { throw '결과 ISO의 SHA-256이 다릅니다.' }
Write-Output "Verified: $OutputIso"
'''
(release/'적용하기.ps1').write_text(apply,encoding='utf-8-sig')
summary={k:dict(total=v['total'],counts=v['counts']) for k,v in audit['banks'].items()}
readme=f'''울티밋 스파이더맨 일본판 PS2 — 한국어 자막 확장 빌드

대상: SLPM-66404 / Ultimate Spider-Man (Japan)
원본 SHA-256: {report['source_sha256']}
결과 SHA-256: {report['build_sha256']}

적용 범위
 - 일반 텍스트 820항목 중 번역 대상 809개, 제작진 직무·감사 문구 169개
 - 대사가 있는 IPU 영상 7개와 홍보 영상의 문구 10개
 - 실시간 음성 {table['clips']:,}개 클립 / 자막 {table['cues']:,}개 구간
 - 원본과 비교해 선정한 NanumSquare Neo Bold 17픽셀 글꼴
 - 2026-10-01 폰트 수정: 한글 2,350자에 원본 팔레트의 검은 1픽셀 외곽선 추가
 - 흰 글자 크기·위치·간격 유지, 투명 배경의 보라색 번짐 제거
 - KS X 1001 한글 2,350자 지원. 영상 음성은 일본어를 유지한다.

현재 검수 상태
음성 인식 결과를 기반으로 번역한 대사가 포함되어 있다. 인식이 불명확한
음성과 아직 번역하지 못한 음성은 임의의 대사로 채우지 않았다.
따라서 이 파일은 모든 음성의 번역·원음 검수가 완료된 완전판이 아니다.
클립별 상태는 subtitle_audit.json, 미확정 원문은 review_queue.tsv에 기록했다.
미해결 음성은 {queue['unresolved']:,}개이며, 비명·신음 또는 무음 후보도 포함한다.
이 수치를 미번역 문장 수나 실제 대사 수로 해석해서는 안 된다.
실제 PS2 및 전 임무 완주, 메모리 카드 저장 후 재로드는 미검증이다.

확인한 사항
 - PCSX2에서 새로 부팅, 제목·프로필·메뉴, 첫 영상과 첫 베놈 전투 이후 도시 진행
 - 전투 중 자막과 튜토리얼 동시 표시, 제작진, 저장 데이터가 없을 때의 안내
 - 홍보 영상 끝까지 재생 및 제목 화면 복귀
 - 최종 영상 자막 14개 표본 화면의 줄바꿈·잘림 검사
 - 실제 글꼴 아틀라스로 전체 자막 글리프의 화면 경계 검사 및 긴 자막 표본 확인
 - ISO 길이/모든 파일 LBA/마지막 섹터 보존, 비변경 영역 바이트 비교
 - 615개 팩 경계·압축 복원·메모리 할당·글리프·실행 파일 검사
 - 원본에 xdelta를 적용한 결과와 빌드 ISO의 SHA-256 일치
전투 이후 화면 검증에는 별도의 QA 저장 상태에만 체력 보조를 적용했다.
배포 ISO와 패치에는 해당 보조 설정이나 BIOS, 저장 파일이 들어 있지 않다.

적용 방법
1. ZIP을 새 폴더에 풀고 본인 소유의 위 SHA-256 원본 ISO를 준비한다.
2. 압축에서 나온 release_extended 폴더에서 PowerShell을 열고 실행한다.
   powershell -ExecutionPolicy Bypass -File .\\적용하기.ps1 -SourceIso "D:\\경로\\Ultimate Spider-Man (Japan).iso"
3. Verified 메시지와 함께 생성된 ISO를 사용한다.
   원본과 기존 출력은 덮어쓰지 않으며, 입력·패치·출력 해시를 검사한다.
4. 복원은 원본 ISO로 돌아가면 된다. 기존 v0.9와는 별도 패치이다.

게임 원본과 BIOS는 포함하지 않는다. 작업 폴더의 xdelta.exe를 사용한다.
다른 위치에 있는 xdelta3 실행 파일은 -Xdelta 매개변수로 지정할 수 있다.
작업 폴더의 rebuild_extended.ps1로 번역 소스에서 빌드를 재생성할 수 있다.
폰트 수정 전 에뮬레이터 상태 저장을 불러오면 메모리에 남은 옛 폰트가
복원될 수 있으므로, 수정 ISO를 완전히 새로 부팅해서 확인한다.

음성 처리 현황
{json.dumps(summary,ensure_ascii=False,indent=2)}
'''
(release/'읽어주세요.txt').write_text(readme,encoding='utf-8-sig')
inputs=sorted({p for folder in ('translation','tools') for p in (root/folder).rglob('*') if p.is_file() and p.suffix in ('.json','.tsv','.py','.c','.h','.txt')})
inputs+=sorted(p for p in root.glob('*') if p.is_file() and (p.name.startswith('requirements-') or p.name=='rebuild_extended.ps1'))
manifest={str(p.relative_to(root)).replace('\\','/'):sha(p) for p in inputs}
(release/'source_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
archive=root/'Ultimate_Spider-Man_KO_subtitles_patch.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(release.rglob('*')):
  if p.is_file():z.write(p,p.relative_to(root))
print(json.dumps(dict(archive=str(archive),archive_bytes=archive.stat().st_size,**report),indent=2),flush=True)
