#!/bin/bash

# Deita Manual Deployment Script
# This script can be used to deploy Deita manually using Ansible

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Deita Manual Deployment Script${NC}"
echo "=================================="

# Check if we're in the ansible directory
if [ ! -f "ansible.cfg" ]; then
    echo -e "${RED}❌ Error: Please run this script from the ansible directory${NC}"
    echo "Usage: cd ansible && ./deploy.sh"
    exit 1
fi

# Check if inventory file exists
if [ ! -f "inventory.yml" ]; then
    echo -e "${RED}❌ Error: inventory.yml not found${NC}"
    echo "Please create inventory.yml with your server details"
    exit 1
fi

# Check if Ansible is installed
if ! command -v ansible &> /dev/null; then
    echo -e "${YELLOW}⚠️  Ansible not found. Installing...${NC}"
    pip install -r requirements.txt
fi

# Test connection
echo -e "${YELLOW}🔍 Testing connection to servers...${NC}"
if ansible production -m ping; then
    echo -e "${GREEN}✅ Connection successful${NC}"
else
    echo -e "${RED}❌ Connection failed. Please check your inventory and SSH keys${NC}"
    exit 1
fi

# Run deployment
echo -e "${YELLOW}🚀 Starting deployment...${NC}"
if ansible-playbook -i inventory.yml deploy.yml -v; then
    echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
    echo ""
    echo "Your application should now be running:"
    echo "- Frontend: http://YOUR_SERVER_IP"
    echo "- Backend API: http://YOUR_SERVER_IP:8000"
    echo "- Health Check: http://YOUR_SERVER_IP:8000/health"
else
    echo -e "${RED}❌ Deployment failed!${NC}"
    echo "Check the output above for error details"
    exit 1
fi
