#!/bin/bash

# Release script for raincloudpy
# Usage: ./release.sh <version> [--test]
# Example: ./release.sh 0.2.0
# Example: ./release.sh 0.2.0 --test  (for TestPyPI)

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if version argument is provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: Version number required${NC}"
    echo "Usage: ./release.sh <version> [--test]"
    echo "Example: ./release.sh 0.2.0"
    exit 1
fi

NEW_VERSION="$1"
TEST_MODE="$2"

echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}  Raincloudpy Release Script v1.0${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

# Validate version format (basic check)
if ! [[ $NEW_VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo -e "${RED}Error: Invalid version format. Use semantic versioning (e.g., 0.1.0)${NC}"
    exit 1
fi

# Check if git working directory is clean
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}Warning: You have uncommitted changes${NC}"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo -e "${GREEN}→ Releasing version ${NEW_VERSION}${NC}"
echo ""

# Step 1: Update version in files
echo -e "${BLUE}[1/7] Updating version numbers...${NC}"

# Update __init__.py
if [ -f "raincloudpy/__init__.py" ]; then
    sed -i.bak "s/__version__ = \".*\"/__version__ = \"${NEW_VERSION}\"/" raincloudpy/__init__.py
    rm raincloudpy/__init__.py.bak 2>/dev/null || true
    echo "  ✓ Updated raincloudpy/__init__.py"
else
    echo -e "${RED}  ✗ raincloudpy/__init__.py not found${NC}"
    exit 1
fi

# Update setup.py
if [ -f "setup.py" ]; then
    sed -i.bak "s/version=\".*\"/version=\"${NEW_VERSION}\"/" setup.py
    rm setup.py.bak 2>/dev/null || true
    echo "  ✓ Updated setup.py"
else
    echo -e "${YELLOW}  ⚠ setup.py not found (skipping)${NC}"
fi

# Update pyproject.toml
if [ -f "pyproject.toml" ]; then
    sed -i.bak "s/^version = \".*\"/version = \"${NEW_VERSION}\"/" pyproject.toml
    rm pyproject.toml.bak 2>/dev/null || true
    echo "  ✓ Updated pyproject.toml"
else
    echo -e "${YELLOW}  ⚠ pyproject.toml not found (skipping)${NC}"
fi

echo ""

# Step 2: Update CHANGELOG.md
echo -e "${BLUE}[2/7] Updating CHANGELOG.md...${NC}"
RELEASE_DATE=$(date +%Y-%m-%d)

if [ -f "CHANGELOG.md" ]; then
    # Check if version already exists in changelog
    if grep -q "\[${NEW_VERSION}\]" CHANGELOG.md; then
        echo -e "${YELLOW}  ⚠ Version ${NEW_VERSION} already in CHANGELOG.md${NC}"
    else
        # Add new version entry after the header
        sed -i.bak "/## \[Unreleased\]/a\\
\\
## [${NEW_VERSION}] - ${RELEASE_DATE}\\
\\
### Changed\\
- Version bump to ${NEW_VERSION}\\
" CHANGELOG.md
        rm CHANGELOG.md.bak 2>/dev/null || true
        echo "  ✓ Added version ${NEW_VERSION} to CHANGELOG.md"
        echo -e "${YELLOW}  ⚠ Please edit CHANGELOG.md to add detailed changes${NC}"
    fi
else
    echo -e "${YELLOW}  ⚠ CHANGELOG.md not found (skipping)${NC}"
fi

echo ""

# Step 3: Show changes and confirm
echo -e "${BLUE}[3/7] Review changes...${NC}"
git diff raincloudpy/__init__.py setup.py pyproject.toml CHANGELOG.md 2>/dev/null || true
echo ""

read -p "Continue with these changes? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}Release cancelled${NC}"
    exit 1
fi

# Step 4: Commit changes
echo -e "${BLUE}[4/7] Committing version changes...${NC}"
git add raincloudpy/__init__.py setup.py pyproject.toml CHANGELOG.md 2>/dev/null || true
git commit -m "Bump version to ${NEW_VERSION}" || echo "  ⚠ Nothing to commit"
echo "  ✓ Changes committed"
echo ""

# Step 5: Create git tag
echo -e "${BLUE}[5/7] Creating git tag...${NC}"
if git tag -l | grep -q "v${NEW_VERSION}"; then
    echo -e "${YELLOW}  ⚠ Tag v${NEW_VERSION} already exists${NC}"
    read -p "Delete and recreate tag? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git tag -d "v${NEW_VERSION}"
        git tag -a "v${NEW_VERSION}" -m "Release version ${NEW_VERSION}"
        echo "  ✓ Tag v${NEW_VERSION} recreated"
    fi
else
    git tag -a "v${NEW_VERSION}" -m "Release version ${NEW_VERSION}"
    echo "  ✓ Tag v${NEW_VERSION} created"
fi
echo ""

# Step 6: Build package
echo -e "${BLUE}[6/7] Building package...${NC}"

# Clean previous builds
if [ -d "dist" ]; then
    rm -rf dist/
    echo "  ✓ Cleaned previous builds"
fi

if [ -d "build" ]; then
    rm -rf build/
fi

# Build
python -m build
echo "  ✓ Package built successfully"
echo ""

# Check package
echo -e "${BLUE}Checking package with twine...${NC}"
python -m twine check dist/*
echo "  ✓ Package check passed"
echo ""

# Step 7: Upload to PyPI
echo -e "${BLUE}[7/7] Publishing package...${NC}"

if [ "$TEST_MODE" == "--test" ]; then
    echo -e "${YELLOW}→ Uploading to TestPyPI...${NC}"
    python -m twine upload --repository testpypi dist/*
    echo ""
    echo -e "${GREEN}✓ Package uploaded to TestPyPI${NC}"
    echo -e "${BLUE}Test installation with:${NC}"
    echo -e "  pip install --index-url https://test.pypi.org/simple/ raincloudpy==${NEW_VERSION}"
else
    echo -e "${YELLOW}→ Uploading to PyPI...${NC}"
    read -p "Upload to PyPI? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python -m twine upload dist/*
        echo ""
        echo -e "${GREEN}✓ Package uploaded to PyPI${NC}"
    else
        echo -e "${YELLOW}Upload skipped${NC}"
    fi
fi

echo ""

# Push to remote
echo -e "${BLUE}Pushing to remote repository...${NC}"
read -p "Push commits and tags to remote? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git push
    git push origin "v${NEW_VERSION}"
    echo -e "${GREEN}✓ Pushed to remote${NC}"
else
    echo -e "${YELLOW}Push skipped. Remember to push manually:${NC}"
    echo "  git push"
    echo "  git push origin v${NEW_VERSION}"
fi

echo ""
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}  Release ${NEW_VERSION} completed!${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "  • Verify installation: pip install raincloudpy==${NEW_VERSION}"
echo "  • Create GitHub release at: https://github.com/bsgarcia/raincloudpy/releases/new"
echo "  • Update documentation if needed"
echo ""
