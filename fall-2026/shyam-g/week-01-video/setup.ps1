# Run from an extracted submission folder; installs into its parent workspace.
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$toolkitPath = Join-Path $projectRoot 'brutalist.art'
if (-not (Test-Path -LiteralPath $toolkitPath)) {
    git clone https://github.com/nikbearbrown/brutalist.art $toolkitPath
    if ($LASTEXITCODE) { throw 'Toolkit clone failed' }
    git -C $toolkitPath checkout cd4bf20904be4e7d63babd9622b17963c2361b27
    if ($LASTEXITCODE) { throw 'Toolkit checkout failed' }
}
$venvPython = Join-Path $projectRoot '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $venvPython)) {
    py -3.12 -m venv (Join-Path $projectRoot '.venv')
    if ($LASTEXITCODE) { throw 'Python 3.12 environment creation failed' }
}
& $venvPython -m pip install -r (Join-Path $PSScriptRoot 'requirements.txt')
if ($LASTEXITCODE) { throw 'Python dependency install failed' }
npm.cmd --prefix (Join-Path $toolkitPath 'runtime/remotion') install
if ($LASTEXITCODE) { throw 'Remotion dependency install failed' }
$modelDir = Join-Path $toolkitPath 'runtime/models/kokoro'
New-Item -ItemType Directory -Force -Path $modelDir | Out-Null
foreach ($modelFile in @('kokoro-v1.0.onnx','voices-v1.0.bin')) {
    $modelTarget = Join-Path $modelDir $modelFile
    if (-not (Test-Path -LiteralPath $modelTarget)) {
        Invoke-WebRequest -Uri "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/$modelFile" -OutFile $modelTarget
    }
}
$toolsDir = Join-Path $projectRoot '.tools'
New-Item -ItemType Directory -Force -Path $toolsDir | Out-Null
$encoderPath = & $venvPython -c 'import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())'
Copy-Item -LiteralPath $encoderPath -Destination (Join-Path $toolsDir 'ffmpeg.exe')
Write-Output 'Dependencies installed. Run the exact build commands in README.md.'
