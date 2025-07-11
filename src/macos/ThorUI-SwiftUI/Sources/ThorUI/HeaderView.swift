// src/macos/ThorUI-SwiftUI/Sources/ThorUI/HeaderView.swift
import SwiftUI

struct HeaderView: View {
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        HStack {
            // Logo and Title
            HStack(spacing: 12) {
                Image(systemName: "brain.head.profile")
                    .font(.system(size: 24, weight: .bold))
                    .foregroundColor(.blue)
                
                VStack(alignment: .leading, spacing: 2) {
                    Text("THOR")
                        .font(.title2)
                        .fontWeight(.bold)
                    
                    Text("AI Development Assistant")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            
            Spacer()
            
            // Session Selector
            HStack {
                Text("Session:")
                    .font(.caption)
                    .foregroundColor(.secondary)
                
                Picker("Session", selection: $appState.currentSessionId) {
                    ForEach(appState.sessions.keys.sorted(), id: \.self) { sessionId in
                        Text(sessionId)
                            .tag(sessionId)
                    }
                }
                .pickerStyle(.menu)
                .frame(width: 120)
            }
            
            // Action Buttons
            HStack(spacing: 8) {
                Button(action: appState.createNewSession) {
                    Image(systemName: "plus.circle")
                }
                .help("New Session")
                
                Button(action: { appState.showingSettings = true }) {
                    Image(systemName: "gear")
                }
                .help("Settings")
                
                // Status Indicator
                Circle()
                    .fill(appState.isConnected ? Color.green : Color.red)
                    .frame(width: 8, height: 8)
                    .help(appState.isConnected ? "Connected" : "Disconnected")
            }
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 8)
        .background(Color(NSColor.windowBackgroundColor))
    }
}