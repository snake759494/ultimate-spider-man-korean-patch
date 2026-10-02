param(
    [string]$Python = 'C:\Python313\python.exe',
    [switch]$ReencodeVideos
)
$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
function Invoke-Step([string]$Step, [string[]]$Arguments = @()) {
    & $Python -X utf8 (Join-Path 'tools' $Step) @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Build failed: $Step" }
}
try {
    # Translation JSON/TSV is the source of truth; review status is kept per clip.
    # ASR is not rerun here.
    foreach ($step in @('build_resources.py','patch_elf.py','localize_credits.py','repack.py')) {
        Invoke-Step $step
    }
    Invoke-Step 'build_extended_font.py' @('--all')
    Invoke-Step 'apply_voice_dictionary.py'
    Invoke-Step 'apply_voice_hash_translations.py'
    Invoke-Step 'apply_reviewed_voice.py'
    Invoke-Step 'apply_voice_nonverbal.py'
    Invoke-Step 'reuse_identical_voice.py'
    Invoke-Step 'audit_subtitles.py'
    Invoke-Step 'export_review_queue.py'
    Invoke-Step 'build_subtitle_table.py'
    Invoke-Step 'verify_caption_layout.py'
    Invoke-Step 'build_subtitle_runtime.py'
    Invoke-Step 'test_subtitle_runtime.py'
    if ($ReencodeVideos) {
        Invoke-Step 'build_cinematic_subtitles.py'
        Invoke-Step 'build_attract_subtitles.py'
    }
    Invoke-Step 'build_subtitle_iso.py'
    Invoke-Step 'install_extended_font.py'
    Invoke-Step 'install_runtime_test.py'
    Invoke-Step 'verify_text.py'
    Invoke-Step 'verify_extended_build.py'
    Invoke-Step 'verify_extended_preservation.py'
} finally { Pop-Location }
