// src/macos/ThorUI-SwiftUI/Sources/ThorUI/ContentView.swift
import SwiftUI
import UniformTypeIdentifiers

struct ContentView: View {
    @EnvironmentObject var appState: AppState
    @State private var messageText = ""
    @State private var selectedFiles: [URL] = []
    @State private var showingFilePicker = false
    @State private var showingSettings = false
    
    var body: some View {
        VStack(spacing: 0) {
            // Header Bar
            HeaderView()
            
            Divider()
            
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