$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = Join-Path $projectRoot ".venv\Scripts\python.exe"
$pythonArguments = @()
$specPath = Join-Path $projectRoot "BelialTimer.spec"
$temporaryBuildRoot = Join-Path $env:TEMP (
    "BelialTimer-build-" + [Guid]::NewGuid().ToString("N")
)
$temporaryDist = Join-Path $temporaryBuildRoot "dist"
$releaseDirectory = Join-Path $temporaryDist "BelialTimer"
$archivePath = Join-Path $projectRoot "dist\BelialTimer-windows-x64.zip"
$archiveDirectory = Split-Path -Parent $archivePath

Set-Location $projectRoot

if (-not (Test-Path $python)) {
    $python = "py"
    $pythonArguments = @("-3.12")
}

& $python @pythonArguments -m PyInstaller --version | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller não está instalado para Python 3.12. Rode: py -3.12 -m pip install -r requirements-build.txt"
}

New-Item -ItemType Directory -Path $temporaryBuildRoot | Out-Null

try {
    & $python @pythonArguments -m PyInstaller --noconfirm --clean --distpath $temporaryDist --workpath (Join-Path $temporaryBuildRoot "build") $specPath
    if ($LASTEXITCODE -ne 0) {
        throw "A criação do executável falhou."
    }

    if (-not (Test-Path (Join-Path $releaseDirectory "BelialTimer.exe"))) {
        throw "O executável esperado não foi criado em $releaseDirectory."
    }

    @"
Belial Timer para Windows

Como abrir:
1. Extraia todo o conteúdo do arquivo ZIP para uma pasta.
2. Abra a pasta BelialTimer.
3. Execute BelialTimer.exe.

Não mova o executável para fora desta pasta: os arquivos de suporte precisam
permanecer ao lado dele.

O Windows pode exibir um aviso por o programa ser novo e não possuir assinatura
digital. Baixe o pacote somente pela página oficial de Releases do projeto.
"@ | Set-Content -Path (Join-Path $releaseDirectory "LEIA-ME.txt") -Encoding UTF8

    New-Item -ItemType Directory -Path $archiveDirectory -Force | Out-Null
    & $python @pythonArguments (Join-Path $projectRoot "package_release.py") $releaseDirectory $archivePath
    if ($LASTEXITCODE -ne 0) {
        throw "A criação ou validação do ZIP falhou."
    }

    Write-Output "Pacote ZIP: $archivePath"
}
finally {
    if (Test-Path $temporaryBuildRoot) {
        Remove-Item -LiteralPath $temporaryBuildRoot -Recurse -Force
    }
}
