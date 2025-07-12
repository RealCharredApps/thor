// swift-tools-version: 6.0
// src/macos/ThorUI-SwiftUI/Package.swift

import PackageDescription

let package = Package(
    name: "ThorUI",
    platforms: [.macOS(.v14)],
    products: [
        .executable(name: "ThorUI", targets: ["ThorUI"])
    ],
    dependencies: [
        .package(url: "https://github.com/apple/swift-argument-parser", from: "1.0.0")
    ],
    targets: [
        .executableTarget(
            name: "ThorUI",
            dependencies: [
                .product(name: "ArgumentParser", package: "swift-argument-parser")
            ],
            path: "Sources/ThorUI"
        )
    ]
)