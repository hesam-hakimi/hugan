$hf1Source = 'C:\repos\etl-extension\etl_fw2\etl_framework_extension'
$hf1Clone = 'C:\repos\etl-extension\etl_fw2\etl_framework_extension_hf1'

Set-Location -LiteralPath $hf1Source

git rev-parse HEAD
git status --short
Test-Path -LiteralPath $hf1Clone
