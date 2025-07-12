#!/bin/bash
# src/macos/build_simple.sh

echo "🚀 Building Simple THOR UI for Swift 6.0..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if we have Swift
if ! command -v swift &> /dev/null; then
    echo "❌ Swift not found. Please install Xcode or Swift toolchain."
    exit 1
fi

echo "📱 Swift version: $(swift --version | head -n1)"

# Build simple Swift file with Swift 6.0 compatible flags
echo "🏗️  Compiling Swift file for Swift 6.0..."
swiftc -parse-as-library -o ThorUISimple ThorUISimple.swift

if [ $? -eq 0 ]; then
    echo "✅ Simple build succeeded!"
    echo "🚀 Run: ./ThorUISimple"
    
    # Create app bundle
    APP_PATH="ThorUISimple.app"
    rm -rf "$APP_PATH"
    mkdir -p "$APP_PATH/Contents/MacOS"
    
    cp ThorUISimple "$APP_PATH/Contents/MacOS/"
    
    # Create minimal Info.plist
    cat > "$APP_PATH/Contents/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>ThorUISimple</string>
    <key>CFBundleIdentifier</key>
    <string>com.realcharredapps.thor-simple</string>
    <key>CFBundleName</key>
    <string>THOR Simple</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSMinimumSystemVersion</key>
    <string>14.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF
    
    chmod +x "$APP_PATH/Contents/MacOS/ThorUISimple"
    
    echo "📁 App bundle: $APP_PATH"
    echo "🚀 Launch: open '$APP_PATH'"
    
    # Test launch
    open "$APP_PATH"
    
else
    echo "❌ Build failed. Trying alternative approach..."
    
    # Alternative: Use swift run with package
    echo "🔄 Trying Swift Package approach..."
    mkdir -p SimpleThorPackage/Sources/SimpleThorPackage
    
    # Create Package.swift for Swift 6.0
    cat > SimpleThorPackage/Package.swift << 'EOF'
// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "SimpleThorPackage",
    platforms: [.macOS(.v14)],
    products: [
        .executable(name: "SimpleThorPackage", targets: ["SimpleThorPackage"])
    ],
    targets: [
        .executableTarget(
            name: "SimpleThorPackage"
        )
    ]
)
EOF
    
    # Move Swift file to package
    cp ThorUISimple.swift SimpleThorPackage/Sources/SimpleThorPackage/main.swift
    
    # Build package
    cd SimpleThorPackage
    swift build -c release
    
    if [ $? -eq 0 ]; then
        echo "✅ Package build succeeded!"
        
        # Create app bundle from package
        cd ..
        APP_PATH="ThorUIPackage.app"
        rm -rf "$APP_PATH"
        mkdir -p "$APP_PATH/Contents/MacOS"
        
        cp SimpleThorPackage/.build/release/SimpleThorPackage "$APP_PATH/Contents/MacOS/"
        
        # Create Info.plist
        cat > "$APP_PATH/Contents/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>SimpleThorPackage</string>
    <key>CFBundleIdentifier</key>
    <string>com.realcharredapps.thor-package</string>
    <key>CFBundleName</key>
    <string>THOR Package</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSMinimumSystemVersion</key>
    <string>14.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF
        
        chmod +x "$APP_PATH/Contents/MacOS/SimpleThorPackage"
        
        echo "📁 Package App bundle: $APP_PATH"
        echo "🚀 Launch: open '$APP_PATH'"
        
        open "$APP_PATH"
    else
        echo "❌ Package build also failed."
        exit 1
    fi
fi