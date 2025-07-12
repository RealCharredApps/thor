#!/bin/bash
# src/macos/create_xcode_project.sh

echo "🏗️  Creating Xcode project as fallback..."

PROJECT_DIR="ThorUI-Xcode"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Create Xcode project file
cat > "ThorUI.xcodeproj/project.pbxproj" << 'EOF'
// !$*UTF8*$!
{
	archiveVersion = 1;
	classes = {
	};
	objectVersion = 56;
	objects = {
		buildConfigurationList = {
			isa = XCConfigurationList;
			buildConfigurations = (
				"Release Configuration",
				"Debug Configuration",
			);
			defaultConfigurationIsVisible = 0;
			defaultConfigurationName = Release;
		};
		productRefGroup = {
			isa = PBXGroup;
			children = (
			);
			name = Products;
			sourceTree = "<group>";
		};
		mainGroup = {
			isa = PBXGroup;
			children = (
				productRefGroup,
			);
			sourceTree = "<group>";
		};
		project = {
			isa = PBXProject;
			attributes = {
				BuildIndependentTargetsInParallel = 1;
				LastSwiftUpdateCheck = 1500;
				LastUpgradeCheck = 1500;
			};
			buildConfigurationList = buildConfigurationList;
			compatibilityVersion = "Xcode 14.0";
			developmentRegion = en;
			hasScannedForEncodings = 0;
			knownRegions = (
				en,
				Base,
			);
			mainGroup = mainGroup;
			productRefGroup = productRefGroup;
			projectDirPath = "";
			projectRoot = "";
			targets = (
			);
		};
	};
	rootObject = project;
}
EOF

echo "❌ Xcode project creation incomplete. Let's try a simpler approach..."
cd ..