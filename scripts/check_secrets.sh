#!/bin/bash

# ================================
# Security Secrets Check Script
# ================================
# Verifies no secrets are committed to the repository

echo "🔒 Checking for secrets in repository..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track if any issues found
ISSUES_FOUND=0

# ================================
# Check 1: Verify .gitignore exists
# ================================
echo "📋 Checking .gitignore..."
if [ ! -f ".gitignore" ]; then
    echo -e "${RED}❌ .gitignore not found!${NC}"
    ISSUES_FOUND=1
else
    echo -e "${GREEN}✅ .gitignore exists${NC}"
fi

# ================================
# Check 2: Verify secrets.toml is ignored
# ================================
echo ""
echo "🔐 Checking secrets.toml..."
if [ -f ".streamlit/secrets.toml" ]; then
    if git check-ignore -q .streamlit/secrets.toml 2>/dev/null; then
        echo -e "${GREEN}✅ secrets.toml is properly gitignored${NC}"
    else
        echo -e "${RED}❌ WARNING: secrets.toml exists but is NOT gitignored!${NC}"
        ISSUES_FOUND=1
    fi
else
    echo -e "${YELLOW}⚠️  secrets.toml not found (okay for first setup)${NC}"
fi

# ================================
# Check 3: Scan for API keys in tracked files
# ================================
echo ""
echo "🔍 Scanning tracked files for API keys..."

# Patterns to search for
PATTERNS=(
    "sk-or-v1-"
    "OPENROUTER_API_KEY\s*=\s*['\"]sk-"
    "api_key\s*=\s*['\"]sk-"
    "password\s*=\s*['\"][^'\"]{8,}"
)

for pattern in "${PATTERNS[@]}"; do
    if git grep -i -E "$pattern" 2>/dev/null | grep -v "\.example" | grep -v "# OPENROUTER_API_KEY"; then
        echo -e "${RED}❌ CRITICAL: API key pattern found in tracked files!${NC}"
        ISSUES_FOUND=1
    fi
done

if [ $ISSUES_FOUND -eq 0 ]; then
    echo -e "${GREEN}✅ No API key patterns found in tracked files${NC}"
fi

# ================================
# Check 4: Check for .env files
# ================================
echo ""
echo "📄 Checking for .env files..."

ENV_FILES=(".env" ".env.local" ".env.production")
for env_file in "${ENV_FILES[@]}"; do
    if [ -f "$env_file" ]; then
        if git check-ignore -q "$env_file" 2>/dev/null; then
            echo -e "${GREEN}✅ $env_file is gitignored${NC}"
        else
            echo -e "${RED}❌ WARNING: $env_file exists but is NOT gitignored!${NC}"
            ISSUES_FOUND=1
        fi
    fi
done

# ================================
# Check 5: Verify secrets.toml.example exists
# ================================
echo ""
echo "📝 Checking secrets template..."
if [ -f ".streamlit/secrets.toml.example" ]; then
    echo -e "${GREEN}✅ secrets.toml.example exists${NC}"

    # Check if example contains actual keys
    if grep -q "sk-or-v1-[a-zA-Z0-9]" .streamlit/secrets.toml.example; then
        echo -e "${RED}❌ WARNING: secrets.toml.example contains real API key!${NC}"
        ISSUES_FOUND=1
    else
        echo -e "${GREEN}✅ secrets.toml.example contains no real keys${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  secrets.toml.example not found${NC}"
fi

# ================================
# Check 6: Verify security modules exist
# ================================
echo ""
echo "🛡️  Checking security modules..."

SECURITY_FILES=(
    "src/security/input_validator.py"
    "src/security/rate_limiter.py"
    "src/security/auth.py"
    "src/config/secure_config.py"
    "src/api/secure_client.py"
)

for file in "${SECURITY_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file exists${NC}"
    else
        echo -e "${RED}❌ $file missing${NC}"
        ISSUES_FOUND=1
    fi
done

# ================================
# Final Report
# ================================
echo ""
echo "================================"
if [ $ISSUES_FOUND -eq 0 ]; then
    echo -e "${GREEN}✅ All security checks passed!${NC}"
    echo "Your repository is secure."
    exit 0
else
    echo -e "${RED}❌ Security issues found!${NC}"
    echo "Please fix the issues above before deploying."
    exit 1
fi
