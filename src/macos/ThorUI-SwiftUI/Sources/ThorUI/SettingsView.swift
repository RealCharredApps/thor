// src/macos/ThorUI-SwiftUI/Sources/ThorUI/SettingsView.swift
import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var appState: AppState
    @State private var selectedTab = 0
    
    var body: some View {
        VStack(spacing: 0) {
            // Header
            HStack {
                Text("THOR Settings")
                    .font(.title2)
                    .fontWeight(.semibold)
                
                Spacer()
                
                Button("Done") {
                    appState.showingSettings = false
                }
            }
            .padding()
            
            Divider()
            
            // Tab Content
            TabView(selection: $selectedTab) {
                GeneralSettingsView()
                    .tabItem {
                        Label("General", systemImage: "gear")
                    }
                    .tag(0)
                
                ModelSettingsView()
                    .tabItem {
                        Label("Models", systemImage: "brain.head.profile")
                    }
                    .tag(1)
                
                SwarmSettingsView()
                    .tabItem {
                        Label("Swarm", systemImage: "network")
                    }
                    .tag(2)
                
                AdvancedSettingsView()
                    .tabItem {
                        Label("Advanced", systemImage: "terminal")
                    }
                    .tag(3)
            }
        }
        .frame(width: 600, height: 500)
    }
}

struct GeneralSettingsView: View {
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        Form {
            Section("API Configuration") {
                SecureField("Anthropic API Key", text: $appState.settings.apiKey)
                    .textFieldStyle(.roundedBorder)
                
                HStack {
                    Text("Daily Budget:")
                    Spacer()
                    TextField("0.17", value: $appState.settings.dailyBudget, format: .currency(code: "USD"))
                        .textFieldStyle(.roundedBorder)
                        .frame(width: 100)
                }
                
                Toggle("Cost Warnings", isOn: $appState.settings.showCostWarnings)
            }
            
            Section("Interface") {
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
            
            Section("Memory") {
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
        }
        .padding()
    }
}

struct ModelSettingsView: View {
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        Form {
            Section("Model Selection") {
                Picker("Default Model", selection: $appState.settings.defaultModel) {
                    Text("Claude 3.5 Sonnet").tag("sonnet-4")
                    Text("Claude 3 Opus").tag("opus-4")
                    Text("Claude 3 Haiku").tag("haiku-4")
                }
                .pickerStyle(.menu)
                
                Toggle("Smart Model Selection", isOn: $appState.settings.smartModelSelection)
                    .help("Automatically choose the best model for each task")
            }
            
            Section("Model Behavior") {
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
            
            Section("Cost Management") {
                HStack {
                    Text("Budget Alert at:")
                    Spacer()
                    TextField("80", value: $appState.settings.budgetAlertPercentage, format: .number)
                        .textFieldStyle(.roundedBorder)
                        .frame(width: 60)
                    Text("%")
                }
                
                Toggle("Auto-switch to Haiku when budget low", isOn: $appState.settings.autoSwitchToCheap)
            }
        }
        .padding()
    }
}

struct SwarmSettingsView: View {
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        Form {
            Section("Argus Integration") {
                HStack {
                    Text("Argus Path:")
                    Spacer()
                    TextField("/path/to/argus", text: $appState.settings.argusPath)
                        .textFieldStyle(.roundedBorder)
                    
                    Button("Browse") {
                        // File browser for Argus path
                    }
                }
                
                Toggle("Enable Swarm", isOn: $appState.settings.enableSwarm)
                
                Toggle("Auto-start MCPs", isOn: $appState.settings.autoStartMCPs)
            }
            
            Section("Available MCPs") {
                List {
                    MCPRowView(name: "Business", enabled: $appState.settings.enableBusinessMCP)
                    MCPRowView(name: "Legal", enabled: $appState.settings.enableLegalMCP)
                    MCPRowView(name: "Financial", enabled: $appState.settings.enableFinancialMCP)
                    MCPRowView(name: "Science", enabled: $appState.settings.enableScienceMCP)
                    MCPRowView(name: "Healthcare", enabled: $appState.settings.enableHealthcareMCP)
                }
                .frame(height: 150)
            }
            
            Section("Swarm Behavior") {
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

struct MCPRowView: View {
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
    }
}

struct AdvancedSettingsView: View {
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        Form {
            Section("Debug") {
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
                
                Button("Export Logs") {
                    appState.exportLogs()
                }
            }
            
            Section("Performance") {
                Toggle("Use Streaming", isOn: $appState.settings.useStreaming)
                    .help("Enable streaming for faster responses")
                
                HStack {
                    Text("Request Timeout:")
                    Spacer()
                    TextField("30", value: $appState.settings.requestTimeout, format: .number)
                        .textFieldStyle(.roundedBorder)
                        .frame(width: 60)
                    Text("seconds")
                }
                
                Toggle("Cache Responses", isOn: $appState.settings.cacheResponses)
            }
            
            Section("Data") {
                Button("Export All Data") {
                    appState.exportAllData()
                }
                
                Button("Import Data") {
                    appState.importData()
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