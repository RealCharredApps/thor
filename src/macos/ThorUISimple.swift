// src/macos/ThorUISimple.swift
import SwiftUI
import Foundation

struct SimpleThorApp: App {
    var body: some Scene {
        WindowGroup {
            SimpleThorView()
        }
        .windowStyle(.titleBar)
    }
}

struct SimpleThorView: View {
    @State private var inputText = ""
    @State private var messages: [String] = ["Welcome to THOR! Type your message below."]
    @State private var isLoading = false
    
    var body: some View {
        VStack {
            // Header
            HStack {
                Text("🤖 THOR AI Assistant")
                    .font(.title)
                    .bold()
                Spacer()
                Button("Settings") {
                    // Settings action
                }
            }
            .padding()
            
            // Messages
            ScrollView {
                VStack(alignment: .leading, spacing: 10) {
                    ForEach(messages.indices, id: \.self) { index in
                        HStack {
                            if index % 2 == 0 {
                                Text("🤖")
                                Text(messages[index])
                                    .padding(8)
                                    .background(Color.gray.opacity(0.1))
                                    .cornerRadius(8)
                                Spacer()
                            } else {
                                Spacer()
                                Text(messages[index])
                                    .padding(8)
                                    .background(Color.blue.opacity(0.1))
                                    .cornerRadius(8)
                                Text("👤")
                            }
                        }
                    }
                    
                    if isLoading {
                        HStack {
                            Text("🤖")
                            Text("THOR is thinking...")
                                .italic()
                                .foregroundColor(.gray)
                            Spacer()
                        }
                    }
                }
                .padding()
            }
            
            // Input
            HStack {
                TextField("Ask THOR anything...", text: $inputText)
                    .textFieldStyle(.roundedBorder)
                    .onSubmit {
                        sendMessage()
                    }
                
                Button("Send") {
                    sendMessage()
                }
                .disabled(inputText.isEmpty || isLoading)
            }
            .padding()
        }
        .frame(minWidth: 600, minHeight: 400)
    }
    
    private func sendMessage() {
        guard !inputText.isEmpty else { return }
        
        let message = inputText
        inputText = ""
        messages.append(message)
        isLoading = true
        
        // Simulate THOR response
        DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
            messages.append("I received your message: '\(message)'. This is a simplified THOR UI.")
            isLoading = false
        }
    }
}

// Entry point for Swift 6.0
@main
enum ThorUIMain {
    static func main() {
        SimpleThorApp.main()
    }
}