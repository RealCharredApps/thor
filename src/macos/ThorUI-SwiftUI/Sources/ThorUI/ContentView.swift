// src/macos/ThorUI-SwiftUI/Sources/ThorUI/ContentView.swift - ADD THIS BANNER
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
                        .frame(width: 300)
                } else {
                    SecureField("Enter API key", text: $apiKey)
                        .textFieldStyle(.roundedBorder)
                        .frame(width: 300)
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
        guard !apiKey.isEmpty else { return }
        
        print("🔑 Saving API key from banner...")
        isLoading = true
        
        Task {
            await appState.setAPIKey(apiKey, saveToFile: true)
            
            // Wait a moment for backend response
            try? await Task.sleep(nanoseconds: 1_000_000_000)
            
            await MainActor.run {
                isLoading = false
                if appState.hasAPIKey {
                    apiKey = "" // Clear the field on success
                }
            }
        }
    }
}