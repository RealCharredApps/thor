// src/macos/ThorUI-SwiftUI/Sources/ThorUI/ContentView.swift - ENHANCED
import SwiftUI
import UniformTypeIdentifiers

struct ContentView: View {
    @EnvironmentObject var appState: AppState
    @State private var messageText = ""
    @State private var selectedFiles: [URL] = []
    @State private var showingFilePicker = false
    @State private var showingSettings = false
    @State private var showingAPIKeySetup = false
    
    var body: some View {
        VStack(spacing: 0) {
            // Header Bar
            HeaderView()
            
            Divider()
            
            // API Key Setup Banner (when not configured)
            if !appState.hasAPIKey {
                APIKeySetupBanner()
                Divider()
            }
            
            // Main Content Area
            HStack(spacing: 0) {
                // Sidebar
                SidebarView()
                    .frame(width: 250)
                
                Divider()
                
                // Chat Area
                ChatAreaView()
            }
            
            Divider()
            
            // Input Area
            InputAreaView(
                messageText: $messageText,
                selectedFiles: $selectedFiles,
                showingFilePicker: $showingFilePicker,
                onSendMessage: sendMessage,
                onFileUpload: { showingFilePicker = true }
            )
        }
        .frame(minWidth: 1000, minHeight: 700)
        .fileImporter(
            isPresented: $showingFilePicker,
            allowedContentTypes: [.item],
            allowsMultipleSelection: true
        ) { result in
            handleFileSelection(result)
        }
        .sheet(isPresented: $showingSettings) {
            SettingsView()
                .environmentObject(appState)
        }
        .sheet(isPresented: $showingAPIKeySetup) {
            APIKeySetupView()
                .environmentObject(appState)
        }
    }
    
    private func sendMessage() {
        guard !messageText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { return }
        
        let message = messageText
        let files = selectedFiles
        
        messageText = ""
        selectedFiles = []
        
        Task {
            await appState.sendMessage(message, attachments: files)
        }
    }
    
    private func handleFileSelection(_ result: Result<[URL], Error>) {
        switch result {
        case .success(let urls):
            selectedFiles.append(contentsOf: urls)
        case .failure(let error):
            print("File selection error: \(error)")
        }
    }
}

struct APIKeySetupBanner: View {
    @EnvironmentObject var appState: AppState
    @State private var apiKey = ""
    @State private var isLoading = false
    @State private var showKey = false
    
    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text("🔑 API Key Required")
                    .font(.headline)
                    .foregroundColor(.orange)
                
                Text("Enter your Anthropic API key to start using THOR")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
            
            HStack(spacing: 8) {
                if showKey {
                    TextField("sk-ant-api03-...", text: $apiKey)
                        .textFieldStyle(.roundedBorder)
                        .font(.system(.body, design: .monospaced))
                        .frame(width: 200)
                } else {
                    SecureField("Enter API key", text: $apiKey)
                        .textFieldStyle(.roundedBorder)
                        .frame(width: 200)
                }
                
                Button(showKey ? "Hide" : "Show") {
                    showKey.toggle()
                }
                .font(.caption)
                
                Button("Save & Connect") {
                    saveAPIKey()
                }
                .disabled(apiKey.isEmpty || isLoading)
                .buttonStyle(.borderedProminent)
                
                if isLoading {
                    ProgressView()
                        .scaleEffect(0.8)
                }
            }
        }
        .padding()
        .background(Color.orange.opacity(0.1))
    }
    
    private func saveAPIKey() {
        isLoading = true
        Task {
            await appState.setAPIKey(apiKey, saveToFile: true)
            isLoading = false
        }
    }
}

struct APIKeySetupView: View {
    @EnvironmentObject var appState: AppState
    @State private var apiKey = ""
    @State private var saveToFile = true
    @State private var showKey = false
    @State private var isLoading = false
    @Environment(\.dismiss) var dismiss
    
    var body: some View {
        VStack(spacing: 20) {
            // Header
            HStack {
                Text("🔑 API Key Setup")
                    .font(.title2)
                    .fontWeight(.semibold)
                
                Spacer()
                
                Button("Cancel") {
                    dismiss()
                }
            }
            
            Divider()
            
            // Content
            VStack(alignment: .leading, spacing: 16) {
                Text("Enter your Anthropic API Key")
                    .font(.headline)
                
                VStack(alignment: .leading, spacing: 8) {
                    HStack {
                        if showKey {
                            TextField("sk-ant-api03-...", text: $apiKey)
                                .textFieldStyle(.roundedBorder)
                                .font(.system(.body, design: .monospaced))
                        } else {
                            SecureField("Enter your API key", text: $apiKey)
                                .textFieldStyle(.roundedBorder)
                        }
                        
                        Button(showKey ? "Hide" : "Show") {
                            showKey.toggle()
                        }
                        .font(.caption)
                    }
                    
                    Toggle("Save to .env file (recommended)", isOn: $saveToFile)
                        .font(.caption)
                }
                
                Text("Get your API key from: https://console.anthropic.com")
                    .font(.caption)
                    .foregroundColor(.blue)
                    .onTapGesture {
                        if let url = URL(string: "https://console.anthropic.com") {
                            NSWorkspace.shared.open(url)
                        }
                    }
                
                if saveToFile {
                    Text("ℹ️ Your API key will be saved to the .env file in your THOR directory for future use.")
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .padding(8)
                        .background(Color.blue.opacity(0.1))
                        .cornerRadius(4)
                }
            }
            
            Spacer()
            
            // Buttons
            HStack {
                Spacer()
                
                Button("Cancel") {
                    dismiss()
                }
                
                Button("Save & Connect") {
                    saveAPIKey()
                }
                .disabled(apiKey.isEmpty || isLoading)
                .buttonStyle(.borderedProminent)
                
                if isLoading {
                    ProgressView()
                        .scaleEffect(0.8)
                }
            }
        }
        .padding()
        .frame(width: 500, height: 350)
    }
    
    private func saveAPIKey() {
        isLoading = true
        Task {
            await appState.setAPIKey(apiKey, saveToFile: saveToFile)
            isLoading = false
            if appState.hasAPIKey {
                dismiss()
            }
        }
    }
}