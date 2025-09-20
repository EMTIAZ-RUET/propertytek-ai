#!/bin/bash

# PropertyTek AI - GitHub Pages Deployment Script
echo "🚀 Starting PropertyTek AI deployment to GitHub Pages..."

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/
rm -rf node_modules/.cache/

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Build the React app
echo "🏗️  Building React app..."
npm run build

# Deploy to GitHub Pages
echo "📤 Deploying to GitHub Pages..."
npx gh-pages -d build

echo "✅ Deployment complete! Your app should be available at:"
echo "   https://emtiaz-ruet.github.io/propertytek-ai/"
echo ""
echo "⏳ Note: GitHub Pages may take a few minutes to update"