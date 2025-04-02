# Script to upload to GitHub
param(
    [string]$CommitMessage = "Update project with latest changes",
    [string]$Branch = "main"
)

# Configuration
$CONFIG = @{
    ProjectDir = Split-Path -Parent $PSScriptRoot
    RemoteName = "origin"
    Repository = "https://github.com/lmcdonald6/ATT-FIN-Real-Estate-AI-BOT.git"
}

# Initialize git if needed
function Initialize-Git {
    Write-Host "Initializing git repository..." -ForegroundColor Green
    if (-not (Test-Path "$($CONFIG.ProjectDir)\.git")) {
        Set-Location $CONFIG.ProjectDir
        git init
        git remote add $CONFIG.RemoteName $CONFIG.Repository
    }
}

# Create .gitignore
function Create-Gitignore {
    Write-Host "Creating .gitignore..." -ForegroundColor Green
    $gitignore = @"
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Logs
logs/
*.log

# Local configuration
config/local.yaml

# Data and models
data/
models/

# Environment variables
.env

# Docker
.docker/

# System
.DS_Store
Thumbs.db
"@
    Set-Content -Path "$($CONFIG.ProjectDir)\.gitignore" -Value $gitignore
}

# Stage changes
function Add-Changes {
    Write-Host "Staging changes..." -ForegroundColor Green
    Set-Location $CONFIG.ProjectDir
    git add .
}

# Commit changes
function Commit-Changes {
    param([string]$Message)
    Write-Host "Committing changes..." -ForegroundColor Green
    Set-Location $CONFIG.ProjectDir
    git commit -m $Message
}

# Push to GitHub
function Push-Changes {
    param([string]$BranchName)
    Write-Host "Pushing to GitHub..." -ForegroundColor Green
    Set-Location $CONFIG.ProjectDir
    git push $CONFIG.RemoteName $BranchName
}

# Main process
try {
    Write-Host "Starting GitHub upload process..." -ForegroundColor Green
    
    # Initialize git
    Initialize-Git
    
    # Create .gitignore
    Create-Gitignore
    
    # Add changes
    Add-Changes
    
    # Commit changes
    Commit-Changes -Message $CommitMessage
    
    # Push to GitHub
    Push-Changes -BranchName $Branch
    
    Write-Host "Successfully uploaded to GitHub!" -ForegroundColor Green
} catch {
    Write-Host "Upload failed: $_" -ForegroundColor Red
    exit 1
}
