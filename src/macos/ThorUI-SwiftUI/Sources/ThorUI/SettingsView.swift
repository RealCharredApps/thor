// src/macos/ThorUI-SwiftUI/Sources/ThorUI/SettingsView.swift
import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var appState: AppState
    @State private var selectedTab = 0
    @Environment(\.dismiss) var dismiss
    
    var body: some View {
        VStack(spacing: 0) {
            // Header
            HStack {
                Text("⚙️ THOR Settings")
                    .font(.title2)
                    .fontWeight(.semibold)
                
                Spacer()
                
                Button("Done") {
                    appState.saveSettings()
                    showingSettings = false
                }
                .buttonStyle(.borderedProminent)
            }
            .padding()
            
            Divider()
            
            // Tab Content
            TabView(selection: $selectedTab) {
                ConnectionSettingsView()
                    .tabItem {
                        Label("Connection", systemImage: "network")
                    }
                    .tag(0)
                
                ModelSettingsView()
                    .tabItem {
                        Label("Models", systemImage: "brain.head.profile")
                    }
                    .tag(1)
                
                SwarmSettingsView()
                    .tabItem {
                        Label("Swarm", systemImage: "network.connected")
                    }
                    .tag(2)
                
                GeneralSettingsView()
                    .tabItem {
                        Label("General", systemImage: "gear")
                    }
                    .tag(3)
            }
        }
        .frame(width: 600, height: 500)
    }
    
    @State private var showingSettings = true
}

struct ConnectionSettingsView: View {
    @EnvironmentObject var appState: AppState
    @State private var showAPIKey = false
    @State private var tempAPIKey = ""
    
    var body: some View {
        Form {
            Section("🔑 API Configuration") {
                VStack(alignment: .leading, spacing: 8) {
                    HStack {
                        Text("Anthropic API Key:")
                            .fontWeight(.medium)
                        Spacer()
                        Button(showAPIKey ? "Hide" : "Show") {
                            showAPIKey.toggle()
                        }
                        .font(.caption)
                    }
                    
                    if showAPIKey {
                        TextField("sk-ant-api03-...", text: $tempAPIKey)
                            .textFieldStyle(.roundedBorder)
                            .font(.system(.body, design: .monospaced))
                            .onAppear {
                                tempAPIKey = appState.settings.apiKey
                            }
                    } else {
                        SecureField("Enter your Anthropic API key", text: $tempAPIKey)
                            .textFieldStyle(.roundedBorder)
                            .onAppear {
                                tempAPIKey = appState.settings.apiKey
                            }
                    }
                    
                    HStack {
                        Button("Save API Key") {
                            appState.updateAPIKey(tempAPIKey)
                        }
                        .disabled(tempAPIKey.isEmpty)
                        .buttonStyle(.borderedProminent)
                        
                        if !appState.settings.apiKey.isEmpty {
                            Text("✅ Saved")
                                .font(.caption)
                                .foregroundColor(.green)
                        }
                    }
                    
                    Text("Get your API key from: https://console.anthropic.com")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                HStack {
                    Text("Connection Status:")
                    Spacer()
                    HStack {
                        Circle()
                            .fill(appState.isConnected ? .green : .red)
                            .frame(width: 8, height: 8)
                        Text(appState.isConnected ? "Connected" : "Disconnected")
                            .font(.caption)
                    }
                }
                
                Button("Test Connection") {
                    appState.checkCost()
                }
                .disabled(appState.settings.apiKey.isEmpty)
            }
            
            // ... rest of the settings view remains the same
        }
        .padding()
    }
}

struct ModelSettingsView: View {
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        Form {
            Section("🤖 Model Selection") {
                Picker("Default Model", selection: $appState.settings.defaultModel) {
                    Text("Claude 3.5 Sonnet (Recommended)").tag("sonnet-4")
                    Text("Claude 3 Opus (Most Capable)").tag("opus-4")
                    Text("Claude 3 Haiku (Fastest)").tag("haiku-4")
                }
                .pickerStyle(.menu)
                
                Toggle("Smart Model Selection", isOn: $appState.settings.smartModelSelection)
                    .help("Automatically choose the best model for each task")
            }
            
            Section("⚙️ Model Parameters") {
                HStack {
                    Text("Temperature:")
                    Spacer()
                    Slider(value: $appState.settings.temperature, in: 0...1, step: 0.1)
                        .frame(width: 200)
                    Text("\(appState.settings.temperature, specifier: "%.1f")")
                        .frame(width: 30)
                }
                
                HStack {
                    Text("Max Tokens:")
                    Spacer()
                    TextField("4000", value: $appState.settings.maxTokens, format: .number)
                        .textFieldStyle(.roundedBorder)
                        .frame(width: 80)
                }
                
                Toggle("Use System Prompt", isOn: $appState.settings.useSystemPrompt)
            }
            
            Section("💡 Model Costs (per 1K tokens)") {
                VStack(alignment: .leading, spacing: 4) {
                    HStack {
                        Text("Claude 3.5 Sonnet:")
                        Spacer()
                        Text("$0.003")
                            .font(.system(.body, design: .monospaced))
                    }
                    
                    HStack {
                        Text("Claude 3 Opus:")
                        Spacer()
                        Text("$0.015")
                            .font(.system(.body, design: .monospaced))
                    }
                    
                    HStack {
                        Text("Claude 3 Haiku:")
                        Spacer()
                        Text("$0.00025")
                            .font(.system(.body, design: .monospaced))
                    }
                }
                .font(.caption)
                .foregroundColor(.secondary)
            }
        }
        .padding()
    }
}

struct SwarmSettingsView: View {
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        Form {
            Section("🤖 Argus Swarm Integration") {
                Toggle("Enable Swarm", isOn: $appState.settings.enableSwarm)
                
                VStack(alignment: .leading, spacing: 8) {
                    Text("Argus MCPs Path:")
                        .fontWeight(.medium)
                    
                    TextField("/path/to/Argus_Ai_Agent_MCPs", text: $appState.settings.argusPath)
                        .textFieldStyle(.roundedBorder)
                    
                    Text("Path to your Argus AI Agent MCP servers directory")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                Toggle("Auto-start MCPs", isOn: $appState.settings.autoStartMCPs)
            }
            
            Section("🧠 Available MCP Agents") {
                VStack(spacing: 8) {
                    MCPToggleRow(name: "Business Agent", enabled: $appState.settings.enableBusinessMCP)
                    MCPToggleRow(name: "Legal Agent", enabled: $appState.settings.enableLegalMCP)
                    MCPToggleRow(name: "Financial Agent", enabled: $appState.settings.enableFinancialMCP)
                    MCPToggleRow(name: "Science Agent", enabled: $appState.settings.enableScienceMCP)
                    MCPToggleRow(name: "Healthcare Agent", enabled: $appState.settings.enableHealthcareMCP)
                }
            }
            
            Section("⚙️ Swarm Behavior") {
                Picker("Coordination Mode", selection: $appState.settings.coordinationMode) {
                    Text("Collaborative").tag("collaborative")
                    Text("Competitive").tag("competitive")
                    Text("Sequential").tag("sequential")
                }
                .pickerStyle(.menu)
                
                HStack {
                    Text("Max Concurrent Agents:")
                    Spacer()
                    Stepper("\(appState.settings.maxConcurrentAgents)", value: $appState.settings.maxConcurrentAgents, in: 1...10)
                }
            }
        }
        .padding()
    }
}

struct MCPToggleRow: View {
    let name: String
    @Binding var enabled: Bool
    
    var body: some View {
        HStack {
            Toggle("", isOn: $enabled)
                .toggleStyle(.switch)
            
            Text(name)
            
            Spacer()
            
            Circle()
                .fill(enabled ? Color.green : Color.gray)
                .frame(width: 8, height: 8)
        }
        .padding(.vertical, 2)
    }
}

struct GeneralSettingsView: View {
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        Form {
            Section("🎨 Interface") {
                Picker("Theme", selection: $appState.settings.theme) {
                    Text("System").tag("system")
                    Text("Light").tag("light")
                    Text("Dark").tag("dark")
                }
                .pickerStyle(.segmented)
                
                HStack {
                    Text("Font Size:")
                    Spacer()
                    Stepper("\(appState.settings.fontSize)", value: $appState.settings.fontSize, in: 10...20)
                }
                
                Toggle("Show Timestamps", isOn: $appState.settings.showTimestamps)
                Toggle("Auto-scroll", isOn: $appState.settings.autoScroll)
            }
            
            Section("🧠 Memory") {
                HStack {
                    Text("Chat History Limit:")
                    Spacer()
                    TextField("50", value: $appState.settings.chatMemoryLimit, format: .number)
                        .textFieldStyle(.roundedBorder)
                        .frame(width: 80)
                }
                
                HStack {
                    Text("Artifact Limit:")
                    Spacer()
                    TextField("100", value: $appState.settings.artifactMemoryLimit, format: .number)
                        .textFieldStyle(.roundedBorder)
                        .frame(width: 80)
                }
                
                Button("Clear All Memory") {
                    appState.clearAllMemory()
                }
                .foregroundColor(.red)
            }
            
            Section("🔧 Advanced") {
                Toggle("Debug Mode", isOn: $appState.settings.debugMode)
                Toggle("Verbose Logging", isOn: $appState.settings.verboseLogging)
                
                HStack {
                    Text("Log Level:")
                    Spacer()
                    Picker("Log Level", selection: $appState.settings.logLevel) {
                        Text("ERROR").tag("ERROR")
                        Text("WARN").tag("WARN")
                        Text("INFO").tag("INFO")
                        Text("DEBUG").tag("DEBUG")
                    }
                    .pickerStyle(.menu)
                }
                
                Button("Reset to Defaults") {
                    appState.resetToDefaults()
                }
                .foregroundColor(.red)
            }
        }
        .padding()
    }
}