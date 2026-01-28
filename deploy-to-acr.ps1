# Deploy to Azure Container Registry
# ACR: crhack26llmcommerce001
# Resource Group: hack26-llmcommerce-rg

param(
    [string]$ImageName = "checkoutmcp",
    [string]$Tag = "",  # Auto-generate if not provided
    [string]$ACRName = "crhack26llmcommerce001",
    [string]$ResourceGroup = "hack26-llmcommerce-rg"
)

$ErrorActionPreference = "Stop"

# Auto-generate tag with timestamp if not provided
if ([string]::IsNullOrEmpty($Tag)) {
    $Tag = "v" + (Get-Date -Format "yyyyMMdd-HHmmss")
}

# Colors for output
function Write-Info { Write-Host $args -ForegroundColor Cyan }
function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Error { Write-Host $args -ForegroundColor Red }

$ACRLoginServer = "$ACRName.azurecr.io"
$FullImageName = "$ACRLoginServer/${ImageName}:$Tag"

Write-Info "=========================================="
Write-Info "  Deploying to Azure Container Registry"
Write-Info "=========================================="
Write-Info ""
Write-Info "ACR: $ACRName"
Write-Info "Resource Group: $ResourceGroup"
Write-Info "Image: $FullImageName"
Write-Info ""

# Step 1: Check if Azure CLI is installed
Write-Info "Step 1: Checking Azure CLI..."
try {
    $azVersion = az version --output json 2>$null | ConvertFrom-Json
    Write-Success "Azure CLI version: $($azVersion.'azure-cli')"
} catch {
    Write-Error "Azure CLI is not installed. Please install it from https://aka.ms/installazurecliwindows"
    exit 1
}

# Step 2: Check if logged into Azure
Write-Info "Step 2: Checking Azure login status..."
try {
    $account = az account show --output json 2>$null | ConvertFrom-Json
    Write-Success "Logged in as: $($account.user.name)"
    Write-Success "Subscription: $($account.name)"
} catch {
    Write-Info "Not logged in. Initiating Azure login..."
    az login
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Azure login failed"
        exit 1
    }
}

# Step 3: Verify ACR exists
Write-Info "Step 3: Verifying ACR exists..."
try {
    $acr = az acr show --name $ACRName --resource-group $ResourceGroup --output json 2>$null | ConvertFrom-Json
    Write-Success "ACR found: $($acr.loginServer)"
} catch {
    Write-Error "ACR '$ACRName' not found in resource group '$ResourceGroup'"
    exit 1
}

# Step 4: Login to ACR
Write-Info "Step 4: Logging into ACR..."
az acr login --name $ACRName
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to login to ACR"
    exit 1
}
Write-Success "Successfully logged into ACR"

# Step 5: Build Docker image
Write-Info "Step 5: Building Docker image..."
docker build -t $FullImageName .
if ($LASTEXITCODE -ne 0) {
    Write-Error "Docker build failed"
    exit 1
}
Write-Success "Docker image built successfully"

# Step 6: Push to ACR
Write-Info "Step 6: Pushing image to ACR..."
docker push $FullImageName
if ($LASTEXITCODE -ne 0) {
    Write-Error "Docker push failed"
    exit 1
}
Write-Success "Image pushed successfully to $FullImageName"

# Step 7: Verify image in ACR
Write-Info "Step 7: Verifying image in ACR..."
az acr repository show-tags --name $ACRName --repository $ImageName --output table
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to verify image in ACR"
    exit 1
}

Write-Info ""
Write-Info "=========================================="
Write-Success "  Deployment Complete!"
Write-Info "=========================================="
Write-Info ""
Write-Info "Image URL: $FullImageName"
Write-Info ""
Write-Info "To pull this image:"
Write-Info "  docker pull $FullImageName"
Write-Info ""
Write-Info "To run this image:"
Write-Info "  docker run -p 8000:8000 -p 8001:8001 $FullImageName"
Write-Info ""
