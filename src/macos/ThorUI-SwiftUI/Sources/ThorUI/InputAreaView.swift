// src/macos/ThorUI-SwiftUI/Sources/ThorUI/InputAreaView.swift
import SwiftUI

struct InputAreaView: View {
    @Binding var messageText: String
    @Binding var selectedFiles: [URL]
    @Binding var showingFilePicker: Bool
    
    let onSendMessage: () -> Void
    let onFileUpload: () -> Void
    
    @EnvironmentObject var appState: AppState
    @FocusState private var isTextFieldFocused: Bool
    
    var body: some View {
        VStack(spacing: 8) {
            // File Attachments
            if !selectedFiles.isEmpty {
                AttachmentsPreview(files: $selectedFiles)
            }
            
            // Input Row
            HStack(spacing: 12) {
                // File Upload Button
                Button(action: onFileUpload) {
                    Image(systemName: "paperclip")
                        .font(.system(size: 16))
                }
                .buttonStyle(.plain)
                .help("Attach Files")
                
                // Text Input
                ZStack(alignment: .topLeading) {
                    if messageText.isEmpty {
                        Text("Ask THOR anything... (⌘+Enter to send)")
                            .foregroundColor(.secondary)
                            .padding(.horizontal, 12)
                            .padding(.vertical, 8)
                    }
                    
                    TextEditor(text: $messageText)
                        .focused($isTextFieldFocused)
                        .font(.system(size: 14))
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color.clear)
                        .onKeyPress(.return) { // Swift 6.0 compatible - no parameters
                            onSendMessage()
                            return .handled
                        }
                }
                .background(
                    RoundedRectangle(cornerRadius: 12)
                        .fill(Color(NSColor.textBackgroundColor))
                        .stroke(Color.gray.opacity(0.3), lineWidth: 1)
                )
                .frame(minHeight: 40, maxHeight: 120)
                
                // Send Button
                Button(action: onSendMessage) {
                    Image(systemName: "arrow.up.circle.fill")
                        .font(.system(size: 24))
                        .foregroundColor(messageText.isEmpty ? .gray : .blue)
                }
                .buttonStyle(.plain)
                .disabled(messageText.isEmpty || appState.isThinking)
                .help("Send Message (⌘+Enter)")
            }
            
            // Quick Actions
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 8) {
                    QuickActionButton(
                        title: "List Files",
                        icon: "folder",
                        action: { messageText = "list files in current directory" }
                    )
                    
                    QuickActionButton(
                        title: "Check Cost",
                        icon: "dollarsign.circle",
                        action: { messageText = "check my API usage and costs" }
                    )
                    
                    QuickActionButton(
                        title: "Code Review",
                        icon: "checkmark.seal",
                        action: { messageText = "review my code for security issues and best practices" }
                    )
                    
                    QuickActionButton(
                        title: "Swarm Status",
                        icon: "network",
                        action: { messageText = "check argus swarm connection status" }
                    )
                }
                .padding(.horizontal, 4)
            }
        }
        .padding()
        .background(Color(NSColor.controlBackgroundColor))
        .onAppear {
            isTextFieldFocused = true
        }
    }
}

struct AttachmentsPreview: View {
    @Binding var files: [URL]
    
    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                ForEach(files, id: \.self) { file in
                    HStack(spacing: 6) {
                        Image(systemName: fileIcon(for: file))
                            .font(.system(size: 12))
                            .foregroundColor(.blue)
                        
                        Text(file.lastPathComponent)
                            .font(.caption)
                            .lineLimit(1)
                        
                        Button(action: { removeFile(file) }) {
                            Image(systemName: "xmark.circle.fill")
                                .font(.system(size: 12))
                                .foregroundColor(.gray)
                        }
                        .buttonStyle(.plain)
                    }
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(
                        RoundedRectangle(cornerRadius: 8)
                            .fill(Color.blue.opacity(0.1))
                    )
                }
            }
            .padding(.horizontal)
        }
        .frame(height: 30)
    }
    
    private func removeFile(_ file: URL) {
        files.removeAll { $0 == file }
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

struct QuickActionButton: View {
    let title: String
    let icon: String
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack(spacing: 6) {
                Image(systemName: icon)
                    .font(.system(size: 12))
                
                Text(title)
                    .font(.caption)
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 6)
            .background(
                RoundedRectangle(cornerRadius: 8)
                    .fill(Color.gray.opacity(0.1))
            )
        }
        .buttonStyle(.plain)
    }
}