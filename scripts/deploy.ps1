# Deployment script for Windows PowerShell

# Configuration
$CONFIG = @{
    ProjectDir = Split-Path -Parent $PSScriptRoot
    VenvName = "venv"
    RequirementsFile = "requirements.txt"
    ConfigFile = "config/local.yaml"
    LogDir = "logs"
}

# Create virtual environment if it doesn't exist
function Create-Virtualenv {
    Write-Host "Creating virtual environment..." -ForegroundColor Green
    if (-not (Test-Path "$($CONFIG.ProjectDir)\$($CONFIG.VenvName)")) {
        python -m venv "$($CONFIG.ProjectDir)\$($CONFIG.VenvName)"
    }
    . "$($CONFIG.ProjectDir)\$($CONFIG.VenvName)\Scripts\Activate.ps1"
}

# Install dependencies
function Install-Dependencies {
    Write-Host "Installing dependencies..." -ForegroundColor Green
    pip install -r "$($CONFIG.ProjectDir)\$($CONFIG.RequirementsFile)"
}

# Create necessary directories
function Create-Directories {
    Write-Host "Creating directories..." -ForegroundColor Green
    $dirs = @(
        "$($CONFIG.ProjectDir)\logs",
        "$($CONFIG.ProjectDir)\data",
        "$($CONFIG.ProjectDir)\models"
    )
    foreach ($dir in $dirs) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir
        }
    }
}

# Check configuration
function Check-Config {
    Write-Host "Checking configuration..." -ForegroundColor Green
    if (-not (Test-Path "$($CONFIG.ProjectDir)\$($CONFIG.ConfigFile)")) {
        Write-Host "Config file not found. Creating from example..." -ForegroundColor Yellow
        Copy-Item "$($CONFIG.ProjectDir)\config\example.yaml" "$($CONFIG.ProjectDir)\$($CONFIG.ConfigFile)"
        Write-Host "Please edit $($CONFIG.ConfigFile) with your settings" -ForegroundColor Red
        exit 1
    }
}

# Run database migrations
function Run-Migrations {
    Write-Host "Running database migrations..." -ForegroundColor Green
    python "$($CONFIG.ProjectDir)\src\db\migrate.py"
}

# Start the application
function Start-Application {
    Write-Host "Starting application..." -ForegroundColor Green
    $env:PYTHONPATH = "$($CONFIG.ProjectDir)"
    Start-Process -FilePath "$($CONFIG.ProjectDir)\$($CONFIG.VenvName)\Scripts\python.exe" -ArgumentList "$($CONFIG.ProjectDir)\src\main.py"
}

# Main deployment process
try {
    Write-Host "Starting deployment..." -ForegroundColor Green
    
    # Create virtual environment and activate it
    Create-Virtualenv
    
    # Install dependencies
    Install-Dependencies
    
    # Create necessary directories
    Create-Directories
    
    # Check configuration
    Check-Config
    
    # Run database migrations
    Run-Migrations
    
    # Start application
    Start-Application
    
    Write-Host "Deployment completed successfully!" -ForegroundColor Green
} catch {
    Write-Host "Deployment failed: $_" -ForegroundColor Red
    exit 1
}
