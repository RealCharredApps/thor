// src/macos/ThorUI-SwiftUI/Sources/ThorUI/ThorApp.swift
import SwiftUI
import Foundation

@main
struct ThorApp: App {
    @StateObject private var appState = AppState()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appState)
                .onAppear {
                    appState.initializeThor()
                }
        }
        .windowStyle(.titleBar)
        .windowResizability(.contentSize)
        .commands {
            ThorCommands()
        }
        
        Settings {
            SettingsView()
                .environmentObject(appState)
        }
    }
}

struct ThorCommands: Commands {
    var body: some Commands {
        CommandGroup(replacing: .newItem) {
            Button("New Session") {
                // Handle new session
            }
            .keyboardShortcut("n", modifiers: .command)
        }
        
        CommandGroup(after: .toolbar) {
            Button("Upload File") {
                // Handle file upload
            }
            .keyboardShortcut("u", modifiers: .command)
            
            Button("Export Chat") {
                // Handle export
            }
            .keyboardShortcut("e", modifiers: .command)
        }
    }
}