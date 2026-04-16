# ============================================================================
# OmegaWiki - One-Click Setup (Windows / PowerShell)
# ============================================================================
# Usage:
#   powershell -ExecutionPolicy Bypass -File .\setup.ps1            # English (default)
#   powershell -ExecutionPolicy Bypass -File .\setup.ps1 -Lang zh   # Chinese
#
# Mirrors setup.sh: prerequisites -> venv + deps -> config -> activate i18n -> verify.
# API key configuration (Semantic Scholar, DeepXiv, Review LLM) is handled
# interactively by Claude Code - run /setup after starting Claude Code.
# ============================================================================

[CmdletBinding()]
param(
    [ValidateSet("en", "zh")]
    [string]$Lang = "en"
)

$ErrorActionPreference = "Stop"

function Write-Info($msg) { Write-Host "[INFO]  $msg" -ForegroundColor Blue }
function Write-Ok($msg)   { Write-Host "[OK]    $msg" -ForegroundColor Green }
function Write-Warn2($msg){ Write-Host "[WARN]  $msg" -ForegroundColor Yellow }
function Write-Fail($msg) { Write-Host "[FAIL]  $msg" -ForegroundColor Red }

$ProjectRoot = $PSScriptRoot
$I18nDir = Join-Path $ProjectRoot "i18n\$Lang"
if (-not (Test-Path $I18nDir)) {
    Write-Fail "i18n\$Lang not found - run from the project root"
    exit 1
}

Write-Host ""
Write-Host "============================================"
Write-Host "  OmegaWiki - Setup (Windows)"
Write-Host "============================================"
Write-Host ""

# -- Step 1: Check prerequisites -------------------------------------------
Write-Info "Checking prerequisites..."

# Python: prefer `python`, fall back to `py -3`
$PythonCmd = $null
foreach ($candidate in @("python", "python3", "py")) {
    if (Get-Command $candidate -ErrorAction SilentlyContinue) {
        $PythonCmd = $candidate
        break
    }
}
if (-not $PythonCmd) {
    Write-Fail "Python not found. Install Python 3.9+ from https://www.python.org/downloads/"
    exit 1
}

$pyVersionRaw = & $PythonCmd --version 2>&1
if ($pyVersionRaw -match "(\d+)\.(\d+)\.(\d+)") {
    $pyMajor = [int]$Matches[1]
    $pyMinor = [int]$Matches[2]
    if ($pyMajor -lt 3 -or ($pyMajor -eq 3 -and $pyMinor -lt 9)) {
        Write-Fail "Python >= 3.9 required, found $pyVersionRaw"
        exit 1
    }
    Write-Ok "Python $pyVersionRaw"
} else {
    Write-Fail "Could not parse Python version: $pyVersionRaw"
    exit 1
}

# pip
& $PythonCmd -m pip --version 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Fail "pip not found. Run: $PythonCmd -m ensurepip"
    exit 1
}
Write-Ok "pip available"

# Claude Code
if (Get-Command claude -ErrorAction SilentlyContinue) {
    Write-Ok "Claude Code installed"
} else {
    Write-Warn2 "Claude Code not found."
    Write-Host ""
    Write-Host "  Claude Code is required to use OmegaWiki skills."
    Write-Host "  Install with:"
    Write-Host "    npm install -g @anthropic-ai/claude-code"
    Write-Host ""
    $reply = Read-Host "  Continue setup without Claude Code? [y/N]"
    if ($reply -notmatch '^[Yy]$') {
        Write-Host "  Install Claude Code first, then re-run setup.ps1"
        exit 1
    }
}

# -- Step 2: Python environment + dependencies -----------------------------
Write-Host ""
Write-Info "Setting up Python environment..."

Push-Location $ProjectRoot
try {
    $UsingExisting = $false
    if ($env:VIRTUAL_ENV) {
        Write-Ok "Using active venv: $env:VIRTUAL_ENV"
        $UsingExisting = $true
    } elseif ($env:CONDA_DEFAULT_ENV -and $env:CONDA_DEFAULT_ENV -ne "base") {
        Write-Ok "Using active conda env: $env:CONDA_DEFAULT_ENV"
        $UsingExisting = $true
    } else {
        if (Test-Path ".venv") {
            Write-Warn2 ".venv already exists, using it"
        } else {
            & $PythonCmd -m venv .venv
            if ($LASTEXITCODE -ne 0) { throw "venv creation failed" }
            Write-Ok "Created .venv"
        }
    }

    # Resolve the python interpreter to use for installs + verification
    if ($UsingExisting) {
        $VenvPython = $PythonCmd
    } else {
        $VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
        if (-not (Test-Path $VenvPython)) {
            Write-Fail "Expected $VenvPython but it does not exist"
            exit 1
        }
        Write-Ok "Using .venv\Scripts\python.exe"
    }

    Write-Info "Installing dependencies..."
    & $VenvPython -m pip install -r requirements.txt -q
    if ($LASTEXITCODE -ne 0) { throw "pip install failed" }
    Write-Ok "Dependencies installed"

    # -- Step 3: Configuration files ---------------------------------------
    Write-Host ""
    Write-Info "Setting up configuration..."

    if (Test-Path ".env") {
        Write-Warn2 ".env already exists, not overwriting"
    } else {
        Copy-Item ".env.example" ".env"
        Write-Ok "Created .env from template"
    }

    if (-not (Test-Path ".claude")) { New-Item -ItemType Directory -Path ".claude" | Out-Null }
    if (Test-Path ".claude\settings.local.json") {
        Write-Warn2 ".claude\settings.local.json already exists, not overwriting"
    } else {
        Copy-Item "config\settings.local.json.example" ".claude\settings.local.json"
        Write-Ok "Created .claude\settings.local.json"
    }

    # -- Step 3b: Activate language files ----------------------------------
    Write-Host ""
    Write-Info "Activating language: $Lang"
    Copy-Item (Join-Path $I18nDir "CLAUDE.md") "CLAUDE.md" -Force

    $skillsSrc = Join-Path $I18nDir "skills"
    Get-ChildItem -Path $skillsSrc -Directory | ForEach-Object {
        $name = $_.Name
        $destDir = Join-Path ".claude\skills" $name
        if (-not (Test-Path $destDir)) { New-Item -ItemType Directory -Path $destDir -Force | Out-Null }
        Get-ChildItem -Path $_.FullName -File | ForEach-Object {
            Copy-Item $_.FullName (Join-Path $destDir $_.Name) -Force
        }
    }

    $sharedDest = ".claude\skills\shared-references"
    if (-not (Test-Path $sharedDest)) { New-Item -ItemType Directory -Path $sharedDest -Force | Out-Null }
    Get-ChildItem -Path (Join-Path $I18nDir "shared-references") -Filter "*.md" | ForEach-Object {
        Copy-Item $_.FullName (Join-Path $sharedDest $_.Name) -Force
    }
    Set-Content -Path ".claude\.current-lang" -Value $Lang -NoNewline
    Write-Ok "Language files activated ($Lang)"

    # -- Step 4: Verify installation ---------------------------------------
    Write-Host ""
    Write-Info "Verifying installation..."

    $errors = 0
    $checks = @(
        @{ name = "fetch_arxiv";    import = "from fetch_arxiv import fetch_recent" },
        @{ name = "fetch_s2";       import = "from fetch_s2 import search" },
        @{ name = "fetch_deepxiv";  import = "from fetch_deepxiv import search" },
        @{ name = "research_wiki";  import = "from research_wiki import slugify" },
        @{ name = "lint";           import = "from lint import check_missing_fields" }
    )
    Push-Location "tools"
    try {
        foreach ($c in $checks) {
            & $VenvPython -c $c.import 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Ok ("tools/{0}.py" -f $c.name)
            } else {
                Write-Fail ("tools/{0}.py import error" -f $c.name)
                $errors++
            }
        }
    } finally {
        Pop-Location
    }
} finally {
    Pop-Location
}

# -- Done ------------------------------------------------------------------
Write-Host ""
Write-Host "============================================"
if ($errors -eq 0) {
    Write-Host "  Setup complete!" -ForegroundColor Green
} else {
    Write-Host "  Setup complete with $errors warning(s)" -ForegroundColor Yellow
}
Write-Host "============================================"
Write-Host ""
Write-Host "  Next steps:"
Write-Host ""
Write-Host "  1. Authenticate Claude Code (if not already):"
Write-Host "       claude login"
Write-Host ""
Write-Host "  2. Activate the venv in your shell (optional, for manual tool use):"
Write-Host "       .\.venv\Scripts\Activate.ps1"
Write-Host ""
Write-Host "  3. Start Claude Code:"
Write-Host "       claude"
Write-Host ""
Write-Host "  4. Complete API key configuration (guided):"
Write-Host "       /setup"
Write-Host ""
Write-Host "  5. Then initialize your wiki:"
Write-Host "       /init [your-research-topic]"
Write-Host ""
Write-Host "  For more, see README.md"
Write-Host ""
