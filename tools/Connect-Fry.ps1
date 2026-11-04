param(
    [Parameter(Mandatory = $true)][string]$InstanceId,
    [Parameter(Mandatory = $true)][string]$Profile,
    [ValidateSet('Website', 'Shell', 'Start', 'Stop')][string]$Action = 'Website',
    [string]$Region = 'us-east-1',
    [string]$SessionManagerPluginDirectory = ''
)
$ErrorActionPreference = 'Stop'
if ($InstanceId -notmatch '^i-[0-9a-f]{8,17}$') { throw 'Use the instance ID from the migration outputs.' }
if ($SessionManagerPluginDirectory) {
    $pluginDirectory = (Resolve-Path -LiteralPath $SessionManagerPluginDirectory).Path
    $env:PATH = "$pluginDirectory;$env:PATH"
}
$awsCommand = Get-Command aws -ErrorAction SilentlyContinue
if (-not $awsCommand) {
    $userCli = Join-Path $env:LOCALAPPDATA 'Programs/Amazon/AWSCLIV2/aws.exe'
    if (Test-Path -LiteralPath $userCli) { $awsCommand = Get-Item -LiteralPath $userCli }
    else { throw 'Install AWS CLI v2 from Amazon, then open this script again.' }
}
$awsPath = if ($awsCommand.Source) { $awsCommand.Source } else { $awsCommand.FullName }
$env:AWS_PAGER = ''
& $awsPath sts get-caller-identity --profile $Profile --region $Region --query Arn --output text
if ($LASTEXITCODE -ne 0) { throw "Sign in first with: aws login --profile $Profile --region $Region" }
switch ($Action) {
    'Start' { & $awsPath ec2 start-instances --instance-ids $InstanceId --profile $Profile --region $Region }
    'Stop' { & $awsPath ec2 stop-instances --instance-ids $InstanceId --profile $Profile --region $Region }
    'Shell' {
        & $awsPath ssm start-session --target $InstanceId --document-name Fry-AdminShell --profile $Profile --region $Region
    }
    'Website' {
        if (-not (Get-Command session-manager-plugin -ErrorAction SilentlyContinue)) {
            throw 'Supply the directory containing the official Session Manager plugin, or install it from Amazon.'
        }
        Write-Host 'Keep this connection open. When the session says the port is ready, browse to http://localhost:8002.'
        Write-Host 'Press Ctrl+C to close the private connection. The website has no public listener.'
        & $awsPath ssm start-session --target $InstanceId --document-name AWS-StartPortForwardingSession `
            --parameters 'portNumber=8000,localPortNumber=8002' --profile $Profile --region $Region
    }
}
if ($LASTEXITCODE -ne 0) { throw 'The AWS operation failed; inspect the message above.' }
