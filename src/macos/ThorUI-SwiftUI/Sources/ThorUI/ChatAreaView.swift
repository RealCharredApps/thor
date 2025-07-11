// src/macos/ThorUI-SwiftUI/Sources/ThorUI/ChatAreaView.swift
import SwiftUI

struct ChatAreaView: View {
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        VStack(spacing: 0) {
            // Chat Messages
            ScrollViewReader { proxy in
                ScrollView {
                    LazyVStack(spacing: 12) {
                        ForEach(appState.currentMessages) { message in
                            MessageBubbleView(message: message)
                                .id(message.id)
                        }
                        
                        if appState.isThinking {
                            ThinkingIndicatorView()
                        }
                    }
                    .padding()
                }
                .onChange(of: appState.currentMessages.count) { // Swift 6.0 compatible
                    if let lastMessage = appState.currentMessages.last {
                        withAnimation(.easeInOut(duration: 0.3)) {
                            proxy.scrollTo(lastMessage.id, anchor: .bottom)
                        }
                    }
                }
            }
        }
        .background(Color(NSColor.textBackgroundColor))
    }
}

struct MessageBubbleView: View {
    let message: ChatMessage
    @State private var isHovered = false
    
    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            if !message.isUser {
                Spacer()
                    .frame(width: 50)
            }
            
            VStack(alignment: message.isUser ? .trailing : .leading, spacing: 4) {
                // Message Content
                VStack(alignment: .leading, spacing: 8) {
                    if !message.attachments.isEmpty {
                        AttachmentsView(attachments: message.attachments)
                    }
                    
                    Text(message.content)
                        .textSelection(.enabled)
                        .padding(.horizontal, 16)
                        .padding(.vertical, 12)
                        .background(
                            RoundedRectangle(cornerRadius: 16)
                                .fill(message.isUser ? Color.blue : Color.gray.opacity(0.1))
                        )
                        .foregroundColor(message.isUser ? .white : .primary)
                }
                
                // Timestamp and Actions
                HStack {
                    Text(message.timestamp.formatted(.dateTime.hour().minute()))
                        .font(.caption2)
                        .foregroundColor(.secondary)
                    
                    if isHovered {
                        Button(action: { copyToClipboard(message.content) }) {
                            Image(systemName: "doc.on.doc")
                                .font(.caption)
                        }
                        .buttonStyle(.plain)
                        .help("Copy")
                    }
                }
            }
            
            if message.isUser {
                Spacer()
                    .frame(width: 50)
            }
        }
        .onHover { hovering in
            isHovered = hovering
        }
    }
    
    private func copyToClipboard(_ text: String) {
        let pasteboard = NSPasteboard.general
        pasteboard.clearContents()
        pasteboard.setString(text, forType: .string)
    }
}

struct AttachmentsView: View {
    let attachments: [MessageAttachment]
    
    var body: some View {
        LazyVGrid(columns: [GridItem(.adaptive(minimum: 60))], spacing: 4) {
            ForEach(attachments) { attachment in
                VStack(spacing: 4) {
                    Image(systemName: attachment.icon)
                        .font(.system(size: 20))
                        .foregroundColor(.blue)
                    
                    Text(attachment.name)
                        .font(.caption2)
                        .lineLimit(1)
                }
                .padding(8)
                .background(
                    RoundedRectangle(cornerRadius: 8)
                        .fill(Color.gray.opacity(0.1))
                )
            }
        }
        .padding(.horizontal, 16)
    }
}

struct ThinkingIndicatorView: View {
    @State private var animationPhase = 0
    @State private var timer: Timer?
    
    var body: some View {
        HStack(spacing: 12) {
            Spacer()
                .frame(width: 50)
            
            VStack(alignment: .leading, spacing: 4) {
                HStack {
                    Image(systemName: "brain.head.profile")
                        .font(.system(size: 16))
                        .foregroundColor(.blue)
                    
                    Text("THOR is thinking")
                        .font(.system(size: 14))
                        .foregroundColor(.secondary)
                    
                    HStack(spacing: 4) {
                        ForEach(0..<3) { index in
                            Circle()
                                .fill(Color.blue)
                                .frame(width: 6, height: 6)
                                .opacity(animationPhase == index ? 1.0 : 0.3)
                        }
                    }
                }
                .padding(.horizontal, 16)
                .padding(.vertical, 12)
                .background(
                    RoundedRectangle(cornerRadius: 16)
                        .fill(Color.gray.opacity(0.1))
                )
            }
            
            Spacer()
                .frame(width: 50)
        }
        .onAppear {
            startAnimation()
        }
        .onDisappear {
            stopAnimation()
        }
    }
    
    @MainActor
    private func startAnimation() {
        timer = Timer.scheduledTimer(withTimeInterval: 0.5, repeats: true) { _ in
            Task { @MainActor in
                withAnimation(.easeInOut(duration: 0.3)) {
                    animationPhase = (animationPhase + 1) % 3
                }
            }
        }
    }
    
    private func stopAnimation() {
        timer?.invalidate()
        timer = nil
    }
}