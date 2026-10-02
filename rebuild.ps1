param([string]$Python = 'python')
$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    New-Item -ItemType Directory -Force work,build,translation | Out-Null
    foreach ($step in @('inspect_initial.py','extract_paks.py','build_resources.py','patch_elf.py','repack.py','build_iso.py','verify_text.py','verify_build.py')) {
        & $Python (Join-Path 'tools' $step)
        if ($LASTEXITCODE -ne 0) { throw "Build failed: $step" }
    }
} finally { Pop-Location }
