#!/bin/bash
set -e

echo "=== Strapi Build Script ==="
echo "Node version: $(node --version)"
echo "NPM version: $(npm --version)"

# Ensure we're using npm
if command -v yarn &> /dev/null; then
    echo "Yarn detected, but we'll use npm"
fi

echo "Installing dependencies with npm..."
npm ci --only=production

echo "Building Strapi application..."
npm run build

echo "Build completed successfully!" 