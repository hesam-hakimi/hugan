& {
    $ErrorActionPreference = 'Stop'

    $hf1Root = 'C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1'
    $hf1ExpectedHead = 'b2e44c3a1a051aa7fa6008831d225bc06d22e847'
    $hf1Npm = 'C:\Program Files\nodejs\npm.cmd'
    $hf1Stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
    $hf1LogDir = Join-Path $env:TEMP "HF1_validation_$hf1Stamp"

    $authorizedPaths = @(
        'src/core/framework/TrustedFrameworkDefinitionResolver.ts'
        'src/core/trusted/WriteAuthorization.ts'
        'src/test/helpers/mintTestWriteAuthorization.ts'
        'src/test/suite/trustedFrameworkDefinitionResolver.test.ts'
        'src/test/suite/hf1OracleFreshConsumer.test.ts'
        'src/core/framework/FrameworkDiscoveryService.ts'
        'src/core/readiness/JobKnowledgeContract.ts'
        'src/core/readiness/ReadinessProfileCatalog.ts'
        'src/core/readiness/JobDevelopmentReadinessEvaluator.ts'
        'src/validation/PreWriteValidationPipeline.ts'
        'src/tools/TrustedWriteApprovalStore.ts'
        'src/tools/EtlActionToolService.ts'
        'src/writers/RepoWriter.ts'
        'src/core/trusted/index.ts'
        'src/chat/WriteCoordinator.ts'
        'src/chat/DeployCoordinator.ts'
        'src/test/testPatterns.ts'
        'src/test/suite/repoWriterWorkspaceSelection.test.ts'
        'src/test/suite/jobDevelopmentReadiness.test.ts'
        'src/test/suite/onboardingWriteApproval.test.ts'
        'src/test/suite/createPreviewFlow.test.ts'
        'src/test/suite/writeFlow.test.ts'
        'src/test/suite/extension.test.ts'
        'src/test/suite/phase6WriteDeployRun.test.ts'
        'src/test/suite/runtimeCreateFlow.test.ts'
        'package.json'
        'src/test/suite/etlActionTools.test.ts'
    )

    Set-Location -LiteralPath $hf1Root
    New-Item -ItemType Directory -Path $hf1LogDir | Out-Null

    $observedHead = (& git rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0 -or $observedHead -ne $hf1ExpectedHead) {
        throw "Unexpected HEAD: $observedHead"
    }

    $staged = @(& git diff --cached --name-only)
    if ($LASTEXITCODE -ne 0) { throw 'Unable to inspect staged files.' }
    if ($staged.Count -ne 0) {
        throw "Unexpected staged files:`n$($staged -join "`n")"
    }

    $unstaged = @(& git diff --name-only)
    if ($LASTEXITCODE -ne 0) { throw 'Unable to inspect modified files.' }

    $untracked = @(& git ls-files --others --exclude-standard)
    if ($LASTEXITCODE -ne 0) { throw 'Unable to inspect untracked files.' }

    $changedBefore = @(
        $unstaged
        $untracked
    ) |
        ForEach-Object { $_.Trim().Replace('\', '/') } |
        Where-Object { $_ } |
        Sort-Object -Unique

    $unexpected = @(
        $changedBefore | Where-Object { $_ -notin $authorizedPaths }
    )

    $plannedButUnchanged = @(
        $authorizedPaths | Where-Object { $_ -notin $changedBefore }
    )

    Write-Host ''
    Write-Host "Actual changed files: $($changedBefore.Count)"
    $changedBefore | ForEach-Object { Write-Host "  CHANGED: $_" }

    Write-Host ''
    Write-Host "Authorized but unchanged: $($plannedButUnchanged.Count)"
    $plannedButUnchanged | ForEach-Object { Write-Host "  UNCHANGED: $_" }

    if ($unexpected.Count -ne 0) {
        throw "OUT-OF-SCOPE FILES DETECTED:`n$($unexpected -join "`n")"
    }

    & git diff --check
    if ($LASTEXITCODE -ne 0) {
        throw 'git diff --check failed.'
    }

    & git diff --stat

    $sourceHashesBefore = @{}
    foreach ($relativePath in $changedBefore) {
        $absolutePath = Join-Path $hf1Root $relativePath
        if (Test-Path -LiteralPath $absolutePath -PathType Leaf) {
            $sourceHashesBefore[$relativePath] =
                (Get-FileHash -LiteralPath $absolutePath -Algorithm SHA256).Hash
        }
    }

    $compileOutput = @(& $hf1Npm run compile 2>&1)
    $compileExit = $LASTEXITCODE
    $compileOutput | Set-Content -LiteralPath (Join-Path $hf1LogDir 'compile.log') -Encoding UTF8
    Write-Host "Compile exit: $compileExit"
    if ($compileExit -ne 0) {
        $compileOutput | Select-Object -Last 60
        throw 'HF1 compile failed.'
    }

    $lintOutput = @(& $hf1Npm run lint 2>&1)
    $lintExit = $LASTEXITCODE
    $lintOutput | Set-Content -LiteralPath (Join-Path $hf1LogDir 'lint.log') -Encoding UTF8
    Write-Host "Lint exit: $lintExit"
    if ($lintExit -ne 0) {
        $lintOutput | Select-Object -Last 60
        throw 'HF1 lint failed.'
    }

    $env:MOCHA_GREP =
        'HF1|Trusted framework|RepoWriter workspace selection|Job development readiness|WriteAuthorization|EtlActionTools|ETL action tools'

    $focusedOutput = @(& $hf1Npm run test:unit 2>&1)
    $focusedExit = $LASTEXITCODE
    Remove-Item Env:MOCHA_GREP -ErrorAction SilentlyContinue

    $focusedOutput |
        Set-Content -LiteralPath (Join-Path $hf1LogDir 'focused-unit.log') -Encoding UTF8

    Write-Host "Focused tests exit: $focusedExit"
    $focusedOutput | Select-Object -Last 40

    if ($focusedExit -ne 0) {
        throw 'Focused HF1 tests failed.'
    }

    $fullOutput = @(& $hf1Npm run test:unit 2>&1)
    $fullExit = $LASTEXITCODE

    $fullOutput |
        Set-Content -LiteralPath (Join-Path $hf1LogDir 'full-unit.log') -Encoding UTF8

    $ansiPattern = "$([char]27)\[[0-9;]*[A-Za-z]"
    $fullText = (($fullOutput -join "`n") -replace $ansiPattern, '')

    $failureMatches =
        [regex]::Matches($fullText, '(?m)^\s*(\d+)\s+failing\b')

    $failureCount = -1
    if ($failureMatches.Count -gt 0) {
        $failureCount =
            [int]$failureMatches[$failureMatches.Count - 1].Groups[1].Value
    }

    $knownFailures = @(
        'passes against the committed Phase H baseline report'
        'allows deterministic v3 baseline reports without prompt telemetry'
        'excludes dev logs, eval outputs, generated packages, and test artifacts from VSIX candidate'
        'maintainer delivery prompt references real repo-local agents'
        'repo customization assets use valid frontmatter and agent file naming'
        'source tree uses standard AGENTS.md guidance instead of module AGENT.md files'
    )

    $missingKnownFailures = @(
        $knownFailures | Where-Object { -not $fullText.Contains($_) }
    )

    Write-Host ''
    Write-Host "Full unit exit: $fullExit"
    Write-Host "Observed failure count: $failureCount"

    $fullOutput |
        Select-String -Pattern 'passing|pending|failing' |
        Select-Object -Last 8

    if ($failureCount -ne 6 -or $missingKnownFailures.Count -ne 0) {
        Write-Host "Missing known baseline identities: $($missingKnownFailures.Count)"
        $missingKnownFailures | ForEach-Object { Write-Host "  MISSING: $_" }
        throw 'Full-unit result differs from the six-failure baseline.'
    }

    $unstagedAfter = @(& git diff --name-only)
    $untrackedAfter = @(& git ls-files --others --exclude-standard)

    $changedAfter = @(
        $unstagedAfter
        $untrackedAfter
    ) |
        ForEach-Object { $_.Trim().Replace('\', '/') } |
        Where-Object { $_ } |
        Sort-Object -Unique

    $newUnexpected = @(
        $changedAfter | Where-Object { $_ -notin $authorizedPaths }
    )

    if ($newUnexpected.Count -ne 0) {
        throw "VALIDATION CREATED OUT-OF-SCOPE FILES:`n$($newUnexpected -join "`n")"
    }

    $validationMutatedSource = @()

    foreach ($relativePath in $sourceHashesBefore.Keys) {
        $absolutePath = Join-Path $hf1Root $relativePath
        if (-not (Test-Path -LiteralPath $absolutePath -PathType Leaf)) {
            $validationMutatedSource += "$relativePath (missing)"
            continue
        }

        $afterHash =
            (Get-FileHash -LiteralPath $absolutePath -Algorithm SHA256).Hash

        if ($afterHash -ne $sourceHashesBefore[$relativePath]) {
            $validationMutatedSource += $relativePath
        }
    }

    if ($validationMutatedSource.Count -ne 0) {
        throw "VALIDATION MUTATED SOURCE:`n$($validationMutatedSource -join "`n")"
    }

    & git diff --check
    if ($LASTEXITCODE -ne 0) {
        throw 'Final git diff --check failed.'
    }

    Write-Host ''
    Write-Host 'HF1_EXTERNAL_VALIDATION_PASS'
    Write-Host "HEAD: $observedHead"
    Write-Host "Actual changed files: $($changedAfter.Count)"
    Write-Host 'Compile: PASS'
    Write-Host 'Lint: PASS'
    Write-Host 'Focused HF1 tests: PASS'
    Write-Host 'Full unit: exact six pre-existing failures; no seventh failure'
    Write-Host "Logs: $hf1LogDir"
}
