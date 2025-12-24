#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Deploy Nutcracker to Raspberry Pi using rsync

.PARAMETER Clean
    Perform a clean rebuild before deployment

.PARAMETER SkipBuild
    Skip the build step and only deploy existing publish output

.PARAMETER Target
    Target Pi address (default: nutcracker-2)

.PARAMETER User
    SSH username (default: jfritz)

.PARAMETER Path
    Remote deployment path (default: /home/jfritz/www)

.EXAMPLE
    .\deploy.ps1
    .\deploy.ps1 -Clean
    .\deploy.ps1 -Target "192.168.1.100" -User "pi"
#>

param(
    [switch]$Clean,
    [switch]$SkipBuild,
    [string]$Target = "nutcracker-2",
    [string]$User = "jfritz", 
    [string]$Path = "/home/jfritz/www"
)

$ErrorActionPreference = "Stop"

# Check if rsync is available
if (!(Get-Command rsync -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: rsync not found" -ForegroundColor Red
    Write-Host "Install via: choco install rsync" -ForegroundColor Yellow
    exit 1
}

# Setup paths
$ProjectDir = Join-Path $PSScriptRoot "Nutcracker"
$PublishDir = Join-Path $ProjectDir "bin\Release\net10.0\linux-arm64\publish"

Write-Host ""
Write-Host "=== Nutcracker Deployment ===" -ForegroundColor Cyan
Write-Host "Target: $User@$Target`:$Path" -ForegroundColor Gray
Write-Host ""

# Build step
if (-not $SkipBuild) {
    Write-Host "[1/4] Building application..." -ForegroundColor Cyan
    
    Push-Location $ProjectDir
    try {
        if ($Clean) {
            Write-Host "  Cleaning..." -ForegroundColor Gray
            dotnet clean -c Release | Out-Null
        }
        
        Write-Host "  Publishing for linux-arm64..." -ForegroundColor Gray
        dotnet publish -c Release -r linux-arm64 --self-contained
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Build failed!" -ForegroundColor Red
            exit 1
        }
        
        Write-Host "  Build complete" -ForegroundColor Green
    }
    finally {
        Pop-Location
    }
} else {
    Write-Host "[1/4] Skipping build" -ForegroundColor Yellow
}

# Check if publish directory exists
if (!(Test-Path $PublishDir)) {
    Write-Host "ERROR: Publish directory not found" -ForegroundColor Red
    Write-Host $PublishDir -ForegroundColor Gray
    exit 1
}

# Test SSH connection
Write-Host "[2/4] Testing SSH connection..." -ForegroundColor Cyan
$remoteHost = "$User@$Target"
ssh -o ConnectTimeout=5 -o BatchMode=yes $remoteHost "exit" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Cannot connect to $remoteHost" -ForegroundColor Red
    Write-Host "Make sure SSH is configured and your key is added" -ForegroundColor Yellow
    exit 1
}
Write-Host "  Connected to $remoteHost" -ForegroundColor Green

# Ensure remote directory exists
ssh $remoteHost "mkdir -p $Path" 2>$null

# Perform file sync with rsync
Write-Host "[3/4] Syncing files with rsync..." -ForegroundColor Cyan

# Convert Windows path to Unix-style for rsync (D:\path -> /D/path)
$publishDirUnix = $PublishDir -replace '\\', '/' -replace '^([A-Za-z]):', '/$1'

# Use --rsync-path to bypass shell startup issues
rsync -avz --delete --rsync-path="/usr/bin/rsync" --exclude='*.pdb' --exclude='*.xml' -e "ssh -q" "$publishDirUnix/" "${remoteHost}:${Path}/"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Rsync failed! Checking for shell startup output..." -ForegroundColor Red
    Write-Host "Run this on the Pi to check: ssh $remoteHost 'echo test'" -ForegroundColor Yellow
    Write-Host "If you see anything besides 'test', comment out output in ~/.bashrc" -ForegroundColor Yellow
    exit 1
}

Write-Host "  Files synced successfully" -ForegroundColor Green

# Set execute permissions
ssh $remoteHost "chmod +x $Path/Nutcracker" 2>$null

# Restart the service if it's running
Write-Host "[4/4] Restarting service..." -ForegroundColor Cyan
$serviceStatus = ssh $remoteHost "sudo systemctl is-active nutcracker 2>/dev/null; echo `$?"
$isActive = $serviceStatus -match "active"

if ($isActive) {
    ssh $remoteHost "sudo systemctl restart nutcracker" 2>$null
    Write-Host "  Service restarted" -ForegroundColor Green
} else {
    Write-Host "  Service not running (start manually if needed)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Deployment Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Access: http://$Target`:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Gray
Write-Host "  View logs:    ssh $remoteHost sudo journalctl -u nutcracker -f"
Write-Host "  Start app:    ssh $remoteHost cd $Path '&&' sudo ./Nutcracker"
Write-Host "  Stop service: ssh $remoteHost sudo systemctl stop nutcracker"
Write-Host ""