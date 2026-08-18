& {
    $ErrorActionPreference = 'Stop'

    $hf1Root = 'C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1'
    $hf1Vsce = 'C:\Users\tag5916\AppData\Roaming\npm\vsce.cmd'
    $hf1ExpectedHead = 'b2e44c3a1a051aa7fa6008831d225bc06d22e847'
    $hf1ExpectedBranch = 'hotfix/hf1-oracle-fresh-consumer'

    Set-Location -LiteralPath $hf1Root

    if ((git rev-parse HEAD).Trim() -ne $hf1ExpectedHead) {
        throw 'Unexpected HF1 HEAD.'
    }

    if ((git branch --show-current).Trim() -ne $hf1ExpectedBranch) {
        throw 'Unexpected HF1 branch.'
    }

    if (@(git diff --cached --name-only).Count -ne 0) {
        throw 'Staged files detected.'
    }

    $hf1BeforeStatus = @(git status --porcelain=v1 --untracked-files=all)

    if ($hf1BeforeStatus.Count -ne 27) {
        throw "Expected exactly 27 changed files; observed $($hf1BeforeStatus.Count)."
    }

    git diff --check
    if ($LASTEXITCODE -ne 0) {
        throw 'git diff --check failed.'
    }

    if (-not (Test-Path -LiteralPath $hf1Vsce -PathType Leaf)) {
        throw 'Global vsce.cmd not found.'
    }

    if (-not (Test-Path -LiteralPath '.vscodeignore' -PathType Leaf)) {
        throw '.vscodeignore is missing; stop rather than changing package selection.'
    }

    $hf1Temp = Join-Path $env:TEMP (
        'HF1_TEST_PACKAGE_SAFE_{0}' -f (Get-Date -Format 'yyyyMMdd_HHmmss')
    )

    [void](New-Item -ItemType Directory -Path $hf1Temp)

    $hf1Ignore = Join-Path $hf1Temp 'hf1-test.vscodeignore'
    $hf1IgnoreLines = @(
        Get-Content -LiteralPath '.vscodeignore'
    ) + @(
        ''
        '# Temporary HF1 test-package exclusions'
        '.tsbuildinfo.test'
        '*.tsbuildinfo'
        '*.tsbuildinfo.*'
        'tsconfig.test.json'
    )

    [System.IO.File]::WriteAllLines(
        $hf1Ignore,
        [string[]]$hf1IgnoreLines,
        [System.Text.UTF8Encoding]::new($false)
    )

    $hf1Vsix = Join-Path $hf1Temp 'databricks-etl-copilot-hf1-test-safe.vsix'
    $hf1Log = Join-Path $hf1Temp 'vsce-package.log'

    $hf1HadCI = Test-Path Env:CI
    $hf1OldCI = $env:CI
    $env:CI = 'true'

    try {
        & $hf1Vsce package `
            --out $hf1Vsix `
            --ignoreFile $hf1Ignore *> $hf1Log

        $hf1PackageExit = $LASTEXITCODE
    }
    finally {
        if ($hf1HadCI) {
            $env:CI = $hf1OldCI
        }
        else {
            Remove-Item Env:CI -ErrorAction SilentlyContinue
        }
    }

    Get-Content -LiteralPath $hf1Log

    if ($hf1PackageExit -ne 0) {
        throw "VSCE packaging failed with exit $hf1PackageExit."
    }

    if (-not (Test-Path -LiteralPath $hf1Vsix -PathType Leaf)) {
        throw 'VSIX was not created.'
    }

    $hf1AfterStatus = @(git status --porcelain=v1 --untracked-files=all)

    if (($hf1BeforeStatus -join "`n") -cne ($hf1AfterStatus -join "`n")) {
        Write-Host 'Before status:'
        $hf1BeforeStatus
        Write-Host 'After status:'
        $hf1AfterStatus
        throw 'Repository state changed during packaging.'
    }

    Add-Type -AssemblyName System.IO.Compression.FileSystem

    $hf1Archive = [System.IO.Compression.ZipFile]::OpenRead($hf1Vsix)

    try {
        $hf1Entries = @(
            $hf1Archive.Entries |
                ForEach-Object { $_.FullName.Replace('\', '/') }
        )
    }
    finally {
        $hf1Archive.Dispose()
    }

    $hf1Required = @(
        'extension/package.json'
        'extension/out/extension.js'
        'extension/out/sttm-runtime.js'
    )

    foreach ($hf1RequiredEntry in $hf1Required) {
        if ($hf1Entries -notcontains $hf1RequiredEntry) {
            throw "Required VSIX entry missing: $hf1RequiredEntry"
        }
    }

    if (@($hf1Entries | Where-Object {
        $_ -like 'extension/resources/copilot/*'
    }).Count -eq 0) {
        throw 'Required Copilot resources are missing.'
    }

    $hf1ForbiddenPatterns = @(
        '^extension/(?:\.git|\.github|\.vscode-test)(?:/|$)'
        '^extension/docs/eval(?:/|$)'
        '^extension/src/test(?:/|$)'
        '^extension/out/test(?:/|$)'
        '^extension/(?:AGENT|AGENTS)\.md$'
        '^extension/(?:.*\/)?[^\/]*\.tsbuildinfo(?:\..*)?$'
        '^extension/tsconfig\.test\.json$'
        '^extension/.*\.log$'
        '^extension/.*\.vsix$'
    )

    $hf1ForbiddenEntries = @(
        foreach ($hf1Entry in $hf1Entries) {
            foreach ($hf1Pattern in $hf1ForbiddenPatterns) {
                if ($hf1Entry -match $hf1Pattern) {
                    $hf1Entry
                    break
                }
            }
        }
    ) | Sort-Object -Unique

    if ($hf1ForbiddenEntries.Count -ne 0) {
        Write-Host 'Forbidden package entries detected:'
        $hf1ForbiddenEntries | ForEach-Object { Write-Host "  $_" }
        throw 'HF1 safe VSIX content check failed. Do not install this package.'
    }

    $hf1Hash = (Get-FileHash -LiteralPath $hf1Vsix -Algorithm SHA256).Hash

    Write-Host ''
    Write-Host "VSIX: $hf1Vsix"
    Write-Host "SHA-256: $hf1Hash"
    Write-Host "Files inside VSIX: $($hf1Entries.Count)"
    Write-Host 'Repository source state: UNCHANGED'
    Write-Host 'HF1_TEST_VSIX_CREATED_CONTENTS_CHECKED'
}
