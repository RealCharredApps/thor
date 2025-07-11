// src/macos/ThorUI-SwiftUI/Sources/ThorUI/AppState.swift
import SwiftUI
import Foundation

@MainActor
class AppState: ObservableObject {
    @Published var sessions: [String: SessionData] = [:]
    @Published var currentSessionId: String = "default"
    @Published var isThinking: Bool = false
    @Published var isConnected: Bool = false
    @Published var showingSettings: Bool = false
    @Published var settings: ThorSettings = ThorSettings()
    
    // Cost tracking
    @Published var dailyUsage: Double = 0.0
    @Published var dailyRequests: Int = 0
    @Published var dailyBudget: Double = 0.17
    
    // File management
    @Published var recentFiles: [URL] = []
    
    // Tool dialogs
    @Published var showCommandDialog: Bool = false
    @Published var showSearchDialog: Bool = false
    @Published var showAnalyzeDialog: Bool = false
    
    private var thorProcess: Process?
    private var thorPipe: Pipe?
    
    var currentMessages: [ChatMessage] {
        sessions[currentSessionId]?.messages ?? []
    }
    
    init() {
        createDefaultSession()
        loadSettings()
    }
    
    func initializeThor() {
        // Initialize connection to Python THOR backend
        startThorBackend()
        loadCostData()
    }
    
    private func createDefaultSession() {
        sessions["default"] = SessionData(id: "default", name: "Default")
    }
    
    func createNewSession() {
        let sessionId = "session_\(Int.random(in: 1000...9999))"
        sessions[sessionId] = SessionData(id: sessionId, name: "Session \(sessions.count + 1)")
        currentSessionId = sessionId
    }
    
    func switchToSession(_ sessionId: String) {
        currentSessionId = sessionId
    }
    
    func deleteSession(_ sessionId: String) {
        guard sessionId != "default" else { return }
        sessions.removeValue(forKey: sessionId)
        if currentSessionId == sessionId {
            currentSessionId = "default"
        }
    }
    
    func sendMessage(_ content: String, attachments: [URL] = []) async {
        guard !content.isEmpty else { return }
        
        isThinking = true
        
        // Add user message
        let userMessage = ChatMessage(
            content: content,
            isUser: true,
            attachments: attachments.map { MessageAttachment(url: $0) }
        )
        
        sessions[currentSessionId]?.messages.append(userMessage)
        sessions[currentSessionId]?.messageCount += 1
        
        // Process attachments
        let processedContent = await processAttachments(content, attachments)
        
        // Send to THOR backend
        let response = await sendToThorBackend(processedContent)
        
        // Add assistant response
        let assistantMessage = ChatMessage(
            content: response,
            isUser: false
        )
        
        sessions[currentSessionId]?.messages.append(assistantMessage)
        sessions[currentSessionId]?.messageCount += 1
        
        // Update recent files
        recentFiles.append(contentsOf: attachments)
        recentFiles = Array(Set(recentFiles)).sorted { $0.lastPathComponent < $1.lastPathComponent }
        
        isThinking = false
    }
    
    private func processAttachments(_ content: String, _ attachments: [URL]) async -> String {
        var processedContent = content
        
        for attachment in attachments {
            if attachment.startAccessingSecurityScopedResource() {
                defer { attachment.stopAccessingSecurityScopedResource() }
                
                do {
                    let fileContent = try String(contentsOf: attachment)
                    processedContent += "\n\nFile: \(attachment.lastPathComponent)\n```\n\(fileContent)\n```"
                } catch {
                    processedContent += "\n\nError reading file: \(attachment.lastPathComponent)"
                }
            }
        }
        
        return processedContent
    }
    
    private func sendToThorBackend(_ content: String) async -> String {
        // Simulate THOR backend call
        // In real implementation, this would communicate with the Python THOR process
        
        return await withCheckedContinuation { continuation in
            DispatchQueue.global().asyncAfter(deadline: .now() + 2) {
                continuation.resume(returning: "THOR response to: \(content)")
            }
        }
    }
    
    private func startThorBackend() {
        // Start Python THOR as subprocess
        thorProcess = Process()
        thorPipe = Pipe()
        
        // Configure process to run THOR
        thorProcess?.executableURL = URL(fileURLWithPath: "/usr/bin/python3")
        thorProcess?.arguments = ["-m", "thor_main", "--session", currentSessionId]
        thorProcess?.standardOutput = thorPipe
        thorProcess?.standardError = thorPipe
        
        // Set working directory to THOR project
        let thorPath = FileManager.default.homeDirectoryForCurrentUser
            .appendingPathComponent("Documents/GitHub/RealCharredApps/thor")
        thorProcess?.currentDirectoryURL = thorPath
        
        do {
            try thorProcess?.run()
            isConnected = true
        } catch {
            print("Failed to start THOR backend: \(error)")
            isConnected = false
        }
    }
    
    func runTool(_ toolName: String) {
        Task {
            await sendMessage(toolName)
        }
    }
    
    func openFile(_ url: URL) {
        Task {
            await sendMessage("read \(url.path)")
        }
    }
    
    private func loadSettings() {
        // Load settings from UserDefaults
        if let data = UserDefaults.standard.data(forKey: "ThorSettings"),
           let decoded = try? JSONDecoder().decode(ThorSettings.self, from: data) {
            settings = decoded
        }
    }
    
    func saveSettings() {
        if let encoded = try? JSONEncoder().encode(settings) {
            UserDefaults.standard.set(encoded, forKey: "ThorSettings")
        }
    }
    
    private func loadCostData() {
        // Load cost data from file or backend
        dailyUsage = UserDefaults.standard.double(forKey: "DailyUsage")
        dailyRequests = UserDefaults.standard.integer(forKey: "DailyRequests")
    }
    
    func clearAllMemory() {
        for sessionId in sessions.keys {
            sessions[sessionId]?.messages.removeAll()
        }
    }
    
    func exportLogs() {
        // Export log files
    }
    
    func exportAllData() {
        // Export all user data
    }
    
    func importData() {
        // Import user data
    }
    
    func resetToDefaults() {
        settings = ThorSettings()
        saveSettings()
    }
}

// Data Models
struct SessionData {
    let id: String
    let name: String
    var messages: [ChatMessage] = []
    var messageCount: Int = 0
    let createdAt: Date = Date()
    var lastActive: Date = Date()
}

struct ChatMessage: Identifiable {
    let id = UUID()
    let content: String
    let isUser: Bool
    let timestamp: Date = Date()
    let attachments: [MessageAttachment]
    
    init(content: String, isUser: Bool, attachments: [MessageAttachment] = []) {
        self.content = content
        self.isUser = isUser
        self.attachments = attachments
    }
}

struct MessageAttachment: Identifiable {
    let id = UUID()
    let url: URL
    let name: String
    let icon: String
    
    init(url: URL) {
        self.url = url
        self.name = url.lastPathComponent
        
        let ext = url.pathExtension.lowercased()
        switch ext {
        case "py": self.icon = "doc.text"
        case "js", "ts": self.icon = "curlybraces"
        case "json": self.icon = "doc.badge.gearshape"
        case "md": self.icon = "doc.richtext"
        case "txt": self.icon = "doc.plaintext"
        default: self.icon = "doc"
        }
    }
}

struct ThorSettings: Codable {
    var apiKey: String = ""
    var dailyBudget: Double = 0.17
    var showCostWarnings: Bool = true
    var theme: String = "system"
    var fontSize: Int = 14
    var showTimestamps: Bool = true
    var autoScroll: Bool = true
    var chatMemoryLimit: Int = 50
    var artifactMemoryLimit: Int = 100
    var defaultModel: String = "sonnet-4"
    var smartModelSelection: Bool = true
    var temperature: Double = 0.7
    var maxTokens: Int = 4000
    var useSystemPrompt: Bool = true
    var budgetAlertPercentage: Int = 80
    var autoSwitchToCheap: Bool = true
    var argusPath: String = ""
    var enableSwarm: Bool = false
    var autoStartMCPs: Bool = false
    var enableBusinessMCP: Bool = true
    var enableLegalMCP: Bool = true
    var enableFinancialMCP: Bool = true
    var enableScienceMCP: Bool = true
    var enableHealthcareMCP: Bool = true
    var coordinationMode: String = "collaborative"
    var maxConcurrentAgents: Int = 3
    var debugMode: Bool = false
    var verboseLogging: Bool = false
    var logLevel: String = "INFO"
    var useStreaming: Bool = false
    var requestTimeout: Int = 30
    var cacheResponses: Bool = true
}