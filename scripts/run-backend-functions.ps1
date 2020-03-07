conda activate jmyrberg-website;
foreach ($line in Get-Content ./functions/.env.local) {
    $kvp = $line -split "=",2
    [Environment]::SetEnvironmentVariable($kvp[0].Trim(), $kvp[1].Trim(), "Process") | Out-Null
}
functions-framework --source ./functions/main.py --target index --host localhost --port 8000 --debug;
