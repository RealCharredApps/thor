// src/macos/ThorUI-SwiftUI/Sources/ThorUI/AppState.swift - FIXED
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
    
    @Published var hasAPIKey: Bool = false

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
    
    // WebSocket connection
    private var webSocketTask: URLSessionWebSocketTask?
    private let webSocketURL = URL(string: "ws://localhost:8765")!
    private var connectionRetryCount = 0
    private let maxRetries = 5
    
    var currentMessages: [ChatMessage] {
        sessions[currentSessionId]?.messages ?? []
    }
    
    init() {
        createDefaultSession()
        loadSettings()
    }
    
    func initializeThor() {
        print("🚀 Initializing THOR connection...")
        connectToBackend()
        loadCostData()
        
        // Check API key status after connection
        Task {
            try? await Task.sleep(nanoseconds: 1_000_000_000) // Wait 1 second
            await checkAPIKeyStatus()
        }
    }

    private func createDefaultSession() {
        sessions["default"] = SessionData(id: "default", name: "Default")
    }
    
    private func connectToBackend() {
        print("🔌 Connecting to WebSocket at \(webSocketURL)")
        
        let session = URLSession.shared
        webSocketTask = session.webSocketTask(with: webSocketURL)
        webSocketTask?.resume()
        
        Task {
            await startListening()
        }
        
        // Send API key if available
        if !settings.apiKey.isEmpty {
            Task {
                await sendAPIKey()
            }
        }
    }
    
    private func startListening() async {
        guard let webSocketTask = webSocketTask else { return }
        
        do {
            let message = try await webSocketTask.receive()
            
            switch message {
            case .string(let text):
                print("📥 Received: \(text)")
                await handleBackendMessage(text)
            case .data(let data):
                if let text = String(data: data, encoding: .utf8) {
                    print("📥 Received data: \(text)")
                    await handleBackendMessage(text)
                }
            @unknown default:
                break
            }
            
            // Continue listening
            await startListening()
            
        } catch {
            print("❌ WebSocket error: \(error)")
            isConnected = false
            
            // Retry connection
            if connectionRetryCount < maxRetries {
                connectionRetryCount += 1
                print("🔄 Retrying connection (\(connectionRetryCount)/\(maxRetries))...")
                
                try? await Task.sleep(nanoseconds: 2_000_000_000) // 2 seconds
                connectToBackend()
            } else {
                print("❌ Max retries reached. Backend not available.")
            }
        }
    }
    
    private func sendAPIKey() async {
        guard !settings.apiKey.isEmpty else { return }
        
        let message = BackendMessage(
            type: "set_api_key",
            api_key: settings.apiKey
        )
        
        await sendToBackend(message)
    }

    func setAPIKey(_ apiKey: String, saveToFile: Bool = true) async {
        let message = BackendMessage(
            type: "set_api_key",
            api_key: apiKey,
            save_to_file: saveToFile
        )
        
        await sendToBackend(message)
    }
    
    func checkAPIKeyStatus() async {
        let message = BackendMessage(type: "get_api_key_status")
        await sendToBackend(message)
    }
    
    private func handleBackendMessage(_ messageText: String) async {
        do {
            let data = messageText.data(using: .utf8)!
            let response = try JSONDecoder().decode(BackendResponse.self, from: data)
            
            print("🔄 Handling response type: \(response.type)")
            
            switch response.type {
            case "connection_status":
                if let status = response.status {
                    isConnected = (status == "connected")
                    connectionRetryCount = 0 // Reset retry count on successful connection
                    print("✅ Connection status: \(status)")
                }
                
            case "api_key_status":
            if let hasKey = response.has_api_key {
                hasAPIKey = hasKey
            }
            
            case "api_key_result":
                if let success = response.success {
                    if success {
                        hasAPIKey = true
                        addSystemMessage("✅ API key saved successfully!")
                    } else {
                        let errorMsg = response.message ?? "API key setup failed"
                        addSystemMessage("❌ \(errorMsg)")
                    }
                }
            case "chat_response":
                if let sessionId = response.session_id,
                   let responseContent = response.response {
                    
                    let assistantMessage = ChatMessage(
                        content: responseContent,
                        isUser: false
                    )
                    
                    sessions[sessionId]?.messages.append(assistantMessage)
                    sessions[sessionId]?.messageCount += 1
                }
                isThinking = false
                
            case "tool_result":
                if let result = response.result {
                    let toolMessage = ChatMessage(
                        content: result,
                        isUser: false
                    )
                    
                    sessions[currentSessionId]?.messages.append(toolMessage)
                    sessions[currentSessionId]?.messageCount += 1
                }
                isThinking = false
                
            case "cost_update":
                if let usage = response.daily_usage {
                    dailyUsage = usage
                }
                if let requests = response.daily_requests {
                    dailyRequests = requests
                }
                if let budget = response.daily_budget {
                    dailyBudget = budget
                }
                
            case "error":
                if let error = response.error {
                    let errorMessage = ChatMessage(
                        content: "❌ Error: \(error)",
                        isUser: false
                    )
                    
                    sessions[currentSessionId]?.messages.append(errorMessage)
                    sessions[currentSessionId]?.messageCount += 1
                }
                isThinking = false
                
            default:
                print("⚠️ Unknown response type: \(response.type)")
            }
            
        } catch {
            print("❌ JSON parsing error: \(error)")
            // Fall back to mock response
            handleMockResponse(messageText)
        }
    }
    
    private func addSystemMessage(_ content: String) {
        let systemMessage = ChatMessage(
            content: content,
            isUser: false
        )
        sessions[currentSessionId]?.messages.append(systemMessage)
        sessions[currentSessionId]?.messageCount += 1
    }
    
    private func handleMockResponse(_ originalMessage: String) {
        let mockMessage = ChatMessage(
            content: "🤖 Backend not connected - using mock response",
            isUser: false
        )
        sessions[currentSessionId]?.messages.append(mockMessage)
        sessions[currentSessionId]?.messageCount += 1
        isThinking = false
    }
    
    func sendMessage(_ content: String, attachments: [URL] = []) async {
        guard !content.isEmpty else { return }
        
        isThinking = true
        
        // Add user message immediately
        let userMessage = ChatMessage(
            content: content,
            isUser: true,
            attachments: attachments.map { MessageAttachment(url: $0) }
        )
        
        sessions[currentSessionId]?.messages.append(userMessage)
        sessions[currentSessionId]?.messageCount += 1
        
        // Send to backend or mock
        if isConnected {
            let message = BackendMessage(
                type: "chat",
                session_id: currentSessionId,
                message: content,
                attachments: attachments.map { ["path": $0.path] }
            )
            
            await sendToBackend(message)
        } else {
            // Mock response
            DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
                let mockResponse = ChatMessage(
                    content: "THOR response to: \(content)",
                    isUser: false
                )
                self.sessions[self.currentSessionId]?.messages.append(mockResponse)
                self.sessions[self.currentSessionId]?.messageCount += 1
                self.isThinking = false
            }
        }
        
        // Update recent files
        recentFiles.append(contentsOf: attachments)
        recentFiles = Array(Set(recentFiles)).sorted { $0.lastPathComponent < $1.lastPathComponent }
    }
    
    private func sendToBackend(_ message: BackendMessage) async {
        do {
            let data = try JSONEncoder().encode(message)
            let string = String(data: data, encoding: .utf8)!
            
            print("📤 Sending: \(message.type)")
            
            webSocketTask?.send(.string(string)) { error in
                if let error = error {
                    print("❌ Send failed: \(error)")
                    Task { @MainActor in
                        self.isThinking = false
                    }
                }
            }
        } catch {
            print("❌ Encoding failed: \(error)")
            isThinking = false
        }
    }
    
    func updateAPIKey(_ newKey: String) {
        settings.apiKey = newKey
        saveSettings()
        
        if isConnected {
            Task {
                await sendAPIKey()
            }
        }
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
    
    func runTool(_ toolName: String) {
        Task {
            if isConnected {
                let message = BackendMessage(
                    type: "tool",
                    tool_name: toolName,
                    args: [:]
                )
                await sendToBackend(message)
            } else {
                let mockResponse = ChatMessage(
                    content: "🔧 \(toolName): Mock tool result (backend not connected)",
                    isUser: false
                )
                sessions[currentSessionId]?.messages.append(mockResponse)
                sessions[currentSessionId]?.messageCount += 1
            }
        }
    }
    
    func openFile(_ url: URL) {
        Task {
            await sendMessage("read \(url.path)")
        }
    }
    
    func checkCost() {
        Task {
            if isConnected {
                let message = BackendMessage(type: "cost_check")
                await sendToBackend(message)
            }
        }
    }
    
    private func loadSettings() {
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
        dailyUsage = UserDefaults.standard.double(forKey: "DailyUsage")
        dailyRequests = UserDefaults.standard.integer(forKey: "DailyRequests")
    }
    
    func clearAllMemory() {
        for sessionId in sessions.keys {
            sessions[sessionId]?.messages.removeAll()
        }
    }
    
    func exportLogs() {}
    func exportAllData() {}
    func importData() {}
    func resetToDefaults() {
        settings = ThorSettings()
        saveSettings()
    }
}

// Backend communication models
struct BackendMessage: Codable {
    let type: String
    let session_id: String?
    let message: String?
    let attachments: [[String: String]]?
    let tool_name: String?
    let args: [String: String]?
    let api_key: String?
    let save_to_file: Bool?
    
    init(type: String, session_id: String? = nil, message: String? = nil, attachments: [[String: String]]? = nil, tool_name: String? = nil, args: [String: String]? = nil, api_key: String? = nil, save_to_file: Bool? = nil) {
        self.type = type
        self.session_id = session_id
        self.message = message
        self.attachments = attachments
        self.tool_name = tool_name
        self.args = args
        self.api_key = api_key
        self.save_to_file = save_to_file
    }
}

struct BackendResponse: Codable {
    let type: String
    let session_id: String?
    let response: String?
    let result: String?
    let tool_name: String?
    let error: String?
    let status: String?
    let success: Bool?
    let message: String?
    let daily_usage: Double?
    let daily_requests: Int?
    let daily_budget: Double?
    let timestamp: String?
    let has_api_key: Bool?
    let saved_to_file: Bool?
    let api_key_source: String?
}

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
    var argusPath: String = ""
    var enableSwarm: Bool = false
    
    // UI Settings
    var showCostWarnings: Bool = true
    var theme: String = "system"
    var fontSize: Int = 14
    var showTimestamps: Bool = true
    var autoScroll: Bool = true
    var chatMemoryLimit: Int = 50
    var artifactMemoryLimit: Int = 100
    
    // Model Settings
    var defaultModel: String = "sonnet-4"
    var smartModelSelection: Bool = true
    var temperature: Double = 0.7
    var maxTokens: Int = 4000
    var useSystemPrompt: Bool = true
    var budgetAlertPercentage: Int = 80
    var autoSwitchToCheap: Bool = true
    
    // MCP Settings
    var autoStartMCPs: Bool = false
    var enableBusinessMCP: Bool = true
    var enableLegalMCP: Bool = true
    var enableFinancialMCP: Bool = true
    var enableScienceMCP: Bool = true
    var enableHealthcareMCP: Bool = true
    var coordinationMode: String = "collaborative"
    var maxConcurrentAgents: Int = 3
    
    // Advanced Settings
    var debugMode: Bool = false
    var verboseLogging: Bool = false
    var logLevel: String = "INFO"
    var useStreaming: Bool = false
    var requestTimeout: Int = 30
    var cacheResponses: Bool = true
}