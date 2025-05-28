"use client"

import type React from "react"
import { useState, useRef, useEffect } from "react"
import ReactMarkdown from "react-markdown"
import { ArrowUp, FileText, Upload } from "lucide-react"

interface ChatMessage {
  id: string
  type: "user" | "assistant"
  content: string
  sources?: Array<{ file: string; page: number }>
  timestamp: Date
}

const suggestionCards = [
  {
    title: "What information is in this PDF?",
    subtitle: "Get a summary",
  },
  {
    title: "Explain the key concepts in this document",
    subtitle: "Understand main ideas",
  },
  {
    title: "Find specific information about...",
    subtitle: "Search for details",
  },
  {
    title: "Compare different sections of the document",
    subtitle: "Analyze content",
  },
]

export default function Home() {
  const [question, setQuestion] = useState("")
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [chatHistory])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!question.trim()) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: "user",
      content: question.trim(),
      timestamp: new Date(),
    }

    setChatHistory((prev) => [...prev, userMessage])
    setQuestion("")
    setIsLoading(true)

    try {
      const res = await fetch("/api/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: question.trim() }),
      })

      const data = await res.json()

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: "assistant",
        content: data.answer || "Failed to get answer",
        sources: data.sources || [],
        timestamp: new Date(),
      }

      setChatHistory((prev) => [...prev, assistantMessage])
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: "assistant",
        content: "Failed to get answer",
        timestamp: new Date(),
      }
      setChatHistory((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleSuggestionClick = (suggestion: string) => {
    setQuestion(suggestion)
  }

// ... existing code ...

const handleFileUpload = async (file: File) => {
    if (!file.type.includes("pdf")) {
        alert("Please upload only PDF files")
        return
    }

    setIsUploading(true)

    try {
        const formData = new FormData()
        formData.append("file", file)

        const response = await fetch("/api/ask", {
            method: "POST",
            body: formData,
        })

        const result = await response.json()

        if (response.ok) {
            const successMessage: ChatMessage = {
                id: Date.now().toString(),
                type: "assistant",
                content: `✅ **PDF processed successfully!** 

File: ${result.filename} is now ready for questions.`,
                timestamp: new Date(),
            }
            setChatHistory((prev) => [...prev, successMessage])
        } else {
            alert(`Upload failed: ${result.error}`)
        }
    } catch (error) {
        alert("Upload failed. Please try again.")
    } finally {
        setIsUploading(false)
    }
}

  return (
    <div className="flex flex-col h-screen bg-white">
      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf"
        onChange={(e) => {
          const file = e.target.files?.[0]
          if (file) handleFileUpload(file)
        }}
        className="hidden"
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {chatHistory.length === 0 ? (
          /* Welcome Screen */
          <div className="flex-1 flex flex-col items-center justify-center p-8">
            <div className="flex items-center gap-3 mb-6">
              <img src="/favicon.ico" alt="PDF Genius" className="w-25 h-25" />
              <h1 className="text-3xl font-bold text-gray-900">PDF Genius</h1>
            </div>
            <div className="text-center mb-12">
              <h2 className="text-2xl font-semibold text-gray-900 mb-2">Your PDF Assistant</h2>
              <p className="text-lg text-gray-500">Ask questions about your PDF documents and get instant answers</p>
            </div>

            {/* Suggestion Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl w-full mb-8">
              {suggestionCards.map((card, index) => (
                <button
                  key={index}
                  onClick={() => handleSuggestionClick(card.title)}
                  className="p-4 text-left border border-gray-200 rounded-xl hover:border-blue-300 hover:bg-blue-50 transition-all duration-200 group"
                >
                  <div className="font-medium text-gray-900 mb-1 group-hover:text-blue-700">{card.title}</div>
                  <div className="text-sm text-gray-500 group-hover:text-blue-600">{card.subtitle}</div>
                </button>
              ))}
            </div>
          </div>
        ) : (
          /* Chat Messages */
          <div className="flex-1 overflow-y-auto p-4 pb-32">
            {/* Chat Header */}
            <div className="sticky top-0 bg-white py-3 px-4 border-b border-gray-200 flex items-center gap-3 mb-4">
              <FileText className="w-6 h-6 text-blue-600" />
              <h1 className="text-xl font-bold text-gray-900">PDF Genius</h1>
            </div>

            <div className="max-w-3xl mx-auto space-y-6">
              {chatHistory.map((message) => (
                <div key={message.id} className="space-y-4">
                  {message.type === "user" ? (
                    <div className="flex justify-end">
                      <div className="bg-blue-600 text-white rounded-2xl px-4 py-3 max-w-[80%]">{message.content}</div>
                    </div>
                  ) : (
                    <div className="flex justify-start">
                      <div className="bg-gray-100 rounded-2xl px-4 py-3 max-w-[80%]">
                        <ReactMarkdown
                          components={{
                            strong: ({ node, ...props }) => <strong style={{ color: "#2563eb" }} {...props} />,
                            ol: ({ node, ...props }) => (
                              <ol
                                style={{
                                  paddingLeft: "20px",
                                  margin: "8px 0",
                                  listStyleType: "decimal",
                                }}
                                {...props}
                              />
                            ),
                            ul: ({ node, ...props }) => (
                              <ul
                                style={{
                                  paddingLeft: "20px",
                                  margin: "8px 0",
                                  listStyleType: "disc",
                                }}
                                {...props}
                              />
                            ),
                            li: ({ node, ...props }) => (
                              <li
                                style={{
                                  marginBottom: "4px",
                                  paddingLeft: "4px",
                                }}
                                {...props}
                              />
                            ),
                            p: ({ node, ...props }) => <p style={{ marginBottom: "12px" }} {...props} />,
                          }}
                        >
                          {message.content}
                        </ReactMarkdown>

                        {/* Sources Section */}
                        {message.sources && message.sources.length > 0 && (
                          <div
                            style={{
                              marginTop: "16px",
                              paddingTop: "16px",
                              borderTop: "1px solid #e2e8f0",
                            }}
                          >
                            <div
                              style={{
                                fontSize: "12px",
                                color: "#64748b",
                                marginBottom: "8px",
                                fontWeight: "500",
                              }}
                            >
                              Sources:
                            </div>
                            <div
                              style={{
                                fontSize: "11px",
                                color: "#475569",
                                fontFamily: "monospace",
                                backgroundColor: "#f1f5f9",
                                padding: "8px",
                                borderRadius: "4px",
                              }}
                            >
                              {message.sources.map((src, index) => (
                                <div
                                  key={index}
                                  style={{
                                    marginBottom: "4px",
                                    display: "flex",
                                    alignItems: "flex-start",
                                  }}
                                >
                                  <span
                                    style={{
                                      display: "inline-block",
                                      marginRight: "8px",
                                      color: "#94a3b8",
                                    }}
                                  >
                                    •
                                  </span>
                                  {`${src.file} (Page ${src.page})`}
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 rounded-2xl px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div
                        className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                        style={{ animationDelay: "0.1s" }}
                      ></div>
                      <div
                        className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                        style={{ animationDelay: "0.2s" }}
                      ></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          </div>
        )}

        {/* Fixed Input Area */}
        <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 p-4 z-20">
          <div className="max-w-3xl mx-auto">
            <form onSubmit={handleSubmit} className="relative">
              <div className="flex items-end gap-3 bg-gray-100 rounded-2xl p-3">
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isUploading}
                  className={`p-2 rounded-lg transition-colors ${
                    isUploading
                      ? "text-gray-400 cursor-not-allowed"
                      : "text-gray-600 hover:text-blue-600 hover:bg-blue-50"
                  }`}
                  title="Upload PDF"
                >
                  <Upload className="w-5 h-5" />
                </button>
                <textarea
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="Ask a question about your PDFs..."
                  className="flex-1 bg-transparent border-none outline-none resize-none text-gray-900 placeholder-gray-500 min-h-[24px] max-h-32"
                  rows={1}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault()
                      handleSubmit(e)
                    }
                  }}
                  disabled={isLoading}
                />
                <button
                  type="submit"
                  disabled={isLoading || !question.trim()}
                  className={`p-2 rounded-lg transition-colors ${
                    isLoading || !question.trim()
                      ? "text-gray-400 cursor-not-allowed"
                      : "text-white bg-blue-600 hover:bg-blue-700"
                  }`}
                >
                  <ArrowUp className="w-5 h-5" />
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}
