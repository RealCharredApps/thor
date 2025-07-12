#!/bin/bash
# src/macos/build_thor_ui.sh

echo "🚀 Building THOR macOS UI for Swift 6.0..."

# Get current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check Swift version
SWIFT_VERSION=$(swift --version | head -n1)
echo "📱 Swift version: $SWIFT_VERSION"

# Check for Swift 6.0+
if [[ $SWIFT_VERSION == *"6.0"* ]]; then
    echo "✅ Swift 6.0 detected - using compatible build settings"
    SWIFT_FLAGS="-Xswiftc -swift-version -Xswiftc 6"
else
    echo "⚠️  Using Swift < 6.0 - using legacy build settings"
    SWIFT_FLAGS=""
fi

# Create directory structure if it doesn't exist
mkdir -p ThorUI-SwiftUI/Sources/ThorUI

# Navigate to Swift project
cd ThorUI-SwiftUI

echo "🔧 Resolving dependencies..."
swift package resolve

echo "🏗️  Building project..."
swift build -c release $SWIFT_FLAGS

# Check if build succeeded
if [ ! -f ".build/release/ThorUI" ]; then
    echo "❌ Release build failed. Trying debug build..."
    
    # Try debug build
    swift build $SWIFT_FLAGS
    
    if [ ! -f ".build/debug/ThorUI" ]; then
        echo "❌ Both builds failed. Check error messages above."
        exit 1
    else
        echo "✅ Debug build succeeded"
        BUILD_TYPE="debug"
    fi
else
    echo "✅ Release build succeeded"
    BUILD_TYPE="release"
fi

# Create app bundle
APP_PATH="../ThorUI.app"
rm -rf "$APP_PATH"
mkdir -p "$APP_PATH/Contents/"{MacOS,Resources}

# Copy executable
cp ".build/$BUILD_TYPE/ThorUI" "$APP_PATH/Contents/MacOS/" || {
    echo "❌ Failed to copy executable"
    exit 1
}

# Create Info.plist for macOS 14+
cat > "$APP_PATH/Contents/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>ThorUI</string>
    <key>CFBundleIdentifier</key>
    <string>com.realcharredapps.thor-ui</string>
    <key>CFBundleName</key>
    <string>THOR UI</string>
    <key>CFBundleDisplayName</key>
    <string>THOR</string>
    <key>CFBundleVersion</key>
    <string>2.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>2.0.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSMinimumSystemVersion</key>
    <string>14.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSPrincipalClass</key>
    <string>NSApplication</string>
    <key>LSApplicationCategoryType</key>
    <string>public.app-category.developer-tools</string>
</dict>
</plist>
EOF

# Make executable
chmod +x "$APP_PATH/Contents/MacOS/ThorUI"

echo "✅ THOR UI built successfully!"
echo "📁 App bundle: $APP_PATH"
echo "🚀 Test run: open '$APP_PATH'"

# Test the app
echo "🧪 Testing app launch..."
open "$APP_PATH"