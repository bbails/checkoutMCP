#!/bin/bash

# Deploy to Azure Container Registry
# ACR: crhack26llmcommerce001
# Resource Group: hack26-llmcommerce-rg

set -e

# Configuration
IMAGE_NAME="${IMAGE_NAME:-checkoutmcp}"
ACR_NAME="${ACR_NAME:-crhack26llmcommerce001}"
RESOURCE_GROUP="${RESOURCE_GROUP:-hack26-llmcommerce-rg}"

# Auto-generate tag with timestamp if not provided
if [ -z "$TAG" ]; then
    TAG="v$(date +%Y%m%d-%H%M%S)"
fi

ACR_LOGIN_SERVER="${ACR_NAME}.azurecr.io"
FULL_IMAGE_NAME="${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${TAG}"

# Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

info() { echo -e "${CYAN}$1${NC}"; }
success() { echo -e "${GREEN}✓ $1${NC}"; }
error() { echo -e "${RED}✗ $1${NC}"; exit 1; }

echo -e "${CYAN}==========================================${NC}"
echo -e "${CYAN}  Deploying to Azure Container Registry${NC}"
echo -e "${CYAN}==========================================${NC}"
echo ""
info "ACR: $ACR_NAME"
info "Resource Group: $RESOURCE_GROUP"
info "Image: $FULL_IMAGE_NAME"
echo ""

# Step 1: Check if Azure CLI is installed
info "Step 1: Checking Azure CLI..."
if ! command -v az &> /dev/null; then
    error "Azure CLI is not installed. Please install it from https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
fi
AZ_VERSION=$(az version --query '"azure-cli"' -o tsv)
success "Azure CLI version: $AZ_VERSION"

# Step 2: Check if logged into Azure
info "Step 2: Checking Azure login status..."
if ! az account show &> /dev/null; then
    info "Not logged in. Initiating Azure login..."
    az login
fi
ACCOUNT_NAME=$(az account show --query "user.name" -o tsv)
SUBSCRIPTION=$(az account show --query "name" -o tsv)
success "Logged in as: $ACCOUNT_NAME"
success "Subscription: $SUBSCRIPTION"

# Step 3: Verify ACR exists
info "Step 3: Verifying ACR exists..."
if ! az acr show --name "$ACR_NAME" --resource-group "$RESOURCE_GROUP" &> /dev/null; then
    error "ACR '$ACR_NAME' not found in resource group '$RESOURCE_GROUP'"
fi
success "ACR found: $ACR_LOGIN_SERVER"

# Step 4: Login to ACR
info "Step 4: Logging into ACR..."
az acr login --name "$ACR_NAME"
success "Successfully logged into ACR"

# Step 5: Build Docker image
info "Step 5: Building Docker image..."
docker build -t "$FULL_IMAGE_NAME" .
success "Docker image built successfully"

# Step 6: Push to ACR
info "Step 6: Pushing image to ACR..."
docker push "$FULL_IMAGE_NAME"
success "Image pushed successfully to $FULL_IMAGE_NAME"

# Step 7: Verify image in ACR
info "Step 7: Verifying image in ACR..."
az acr repository show-tags --name "$ACR_NAME" --repository "$IMAGE_NAME" --output table

echo ""
echo -e "${CYAN}==========================================${NC}"
echo -e "${GREEN}  Deployment Complete!${NC}"
echo -e "${CYAN}==========================================${NC}"
echo ""
info "Image URL: $FULL_IMAGE_NAME"
echo ""
info "To pull this image:"
info "  docker pull $FULL_IMAGE_NAME"
echo ""
info "To run this image:"
info "  docker run -p 8000:8000 -p 8001:8001 $FULL_IMAGE_NAME"
echo ""
