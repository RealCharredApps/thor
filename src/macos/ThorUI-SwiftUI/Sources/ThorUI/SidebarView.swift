// src/macos/ThorUI-SwiftUI/Sources/ThorUI/SidebarView.swift
import SwiftUI

struct SidebarView: View {
    @EnvironmentObject var appState: AppState
    @State private var selectedTab = 0
    
    var body: some View {
        VStack(spacing: 0) {
            // Tab Selector
            Picker("View", selection: $selectedTab) {
                Text("Sessions").tag(0)
                Text("Files").tag(1)
                Text("Tools").tag(2)
            }
            .pickerStyle(.segmented)
            .padding()
            
            // Content - Using conditional views instead of TabView
            Group {
                if selectedTab == 0 {
                    SessionsListView()
                } else if selectedTab == 1 {
                    FilesListView()
                } else {
                    ToolsListView()
                }
            }
            
            Spacer()
            
            // Bottom Info
            VStack(alignment: .leading, spacing: 4) {
                Divider()
                
                HStack {
                    Text("💰 Budget:")
                        .font(.caption)
                    
                    Spacer()
                    
                    Text("$\(appState.dailyUsage, specifier: "%.4f")")
                        .font(.caption)
                        .fontWeight(.medium)
                }
                
                ProgressView(value: appState.dailyUsage, total: appState.dailyBudget)
                    .progressViewStyle(.linear)
                    .frame(height: 4)
                
                HStack {
                    Text("Requests: \(appState.dailyRequests)")
                        .font(.caption2)
                        .foregroundColor(.secondary)
                    
                    Spacer()
                    
                    Text("Remaining: $\(appState.dailyBudget - appState.dailyUsage, specifier: "%.4f")")
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }
            }
            .padding()
        }
        .background(Color(NSColor.controlBackgroundColor))
    }
}

struct SessionsListView: View {
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        List {
            ForEach(appState.sessions.keys.sorted(), id: \.self) { sessionId in
                SessionRowView(sessionId: sessionId)
            }
        }
        .listStyle(.sidebar)
    }
}

struct SessionRowView: View {
    let sessionId: String
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        HStack {
            Circle()
                .fill(sessionId == appState.currentSessionId ? Color.blue : Color.gray)
                .frame(width: 8, height: 8)
            
            VStack(alignment: .leading, spacing: 2) {
                Text(sessionId)
                    .font(.system(size: 12, weight: .medium))
                
                if let session = appState.sessions[sessionId] {
                    Text("\(session.messageCount) messages")
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }
            }
            
            Spacer()
            
            if sessionId != "default" {
                Button(action: {
                    appState.deleteSession(sessionId)
                }) {
                    Image(systemName: "trash")
                        .font(.caption)
                        .foregroundColor(.red)
                }
                .buttonStyle(.plain)
            }
        }
        .padding(.vertical, 2)
        .onTapGesture {
            appState.switchToSession(sessionId)
        }
    }
}

struct FilesListView: View {
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        List {
            ForEach(appState.recentFiles, id: \.self) { file in
                HStack {
                    Image(systemName: fileIcon(for: file))
                        .foregroundColor(.blue)
                    
                    VStack(alignment: .leading, spacing: 2) {
                        Text(file.lastPathComponent)
                            .font(.system(size: 12))
                        
                        Text(file.path)
                            .font(.caption2)
                            .foregroundColor(.secondary)
                            .lineLimit(1)
                    }
                    
                    Spacer()
                }
                .onTapGesture {
                    appState.openFile(file)
                }
            }
        }
        .listStyle(.sidebar)
    }
    
    private func fileIcon(for url: URL) -> String {
        let ext = url.pathExtension.lowercased()
        switch ext {
        case "py": return "doc.text"
        case "js", "ts": return "curlybraces"
        case "json": return "doc.badge.gearshape"
        case "md": return "doc.richtext"
        case "txt": return "doc.plaintext"
        default: return "doc"
        }
    }
}

struct ToolsListView: View {
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        List {
            ToolRowView(
                icon: "folder",
                title: "List Files",
                description: "Browse current directory",
                action: { appState.runTool("list_files") }
            )
            
            ToolRowView(
                icon: "terminal",
                title: "Run Command",
                description: "Execute system commands",
                action: { appState.showCommandDialog = true }
            )
            
            ToolRowView(
                icon: "magnifyingglass",
                title: "Search Files",
                description: "Search content in files",
                action: { appState.showSearchDialog = true }
            )
            
            ToolRowView(
                icon: "chart.bar",
                title: "Analyze Code",
                description: "Code quality analysis",
                action: { appState.showAnalyzeDialog = true }
            )
            
            ToolRowView(
                icon: "network",
                title: "Swarm Status",
                description: "Check Argus connections",
                action: { appState.runTool("swarm_status") }
            )
        }
        .listStyle(.sidebar)
    }
}

struct ToolRowView: View {
    let icon: String
    let title: String
    let description: String
    let action: () -> Void
    
    var body: some View {
        HStack {
            Image(systemName: icon)
                .foregroundColor(.blue)
                .frame(width: 16)
            
            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(.system(size: 12, weight: .medium))
                
                Text(description)
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
        }
        .padding(.vertical, 2)
        .onTapGesture {
            action()
        }
    }
}