"use client"

import type React from "react"
import { useState } from "react"
import ReactMarkdown from 'react-markdown';

export default function Home() {
  const [question, setQuestion] = useState("")
  const [answer, setAnswer] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [sources, setSources] = useState<Array<{ file: string, page: number }>>([]);
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!question.trim()) return

    setIsLoading(true)

    try {
      const res = await fetch("/api/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      })

      const data = await res.json();
      setAnswer(data.answer);
      setSources(data.sources || []);
    } catch (error) {
      setAnswer("Failed to get answer")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main
      style={{
        minHeight: "100vh",
        background: "linear-gradient(to bottom, #f8fafc, #e2e8f0)",
        padding: "32px 16px",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      {/* Card */}
      <div
        style={{
          width: "100%",
          maxWidth: "768px",
          backgroundColor: "white",
          borderRadius: "8px",
          boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
          border: "1px solid #e2e8f0",
        }}
      >
        {/* Card Header */}
        <div style={{ padding: "24px", paddingBottom: "16px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#2563eb"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
              <line x1="16" y1="13" x2="8" y2="13"></line>
              <line x1="16" y1="17" x2="8" y2="17"></line>
              <polyline points="10 9 9 9 8 9"></polyline>
            </svg>
            <h1
              style={{
                fontSize: "24px",
                fontWeight: "bold",
                color: "#0f172a",
                margin: 0,
              }}
            >
              PDF Chatbot
            </h1>
          </div>
          <p
            style={{
              fontSize: "14px",
              color: "#64748b",
              margin: 0,
            }}
          >
            Ask questions about your uploaded PDF documents and get instant answers
          </p>
        </div>

        {/* Separator */}
        <div style={{ borderTop: "1px solid #e2e8f0" }}></div>

        {/* Card Content */}
        <div style={{ padding: "24px" }}>
          {answer && (
            <div style={{
              marginBottom: "24px",
              padding: "16px",
              backgroundColor: "#f8fafc",
              borderRadius: "8px",
              border: "1px solid #e2e8f0",
            }}>
              <h3 style={{
                fontWeight: "500",
                fontSize: "14px",
                color: "#64748b",
                marginBottom: "8px",
                margin: "0 0 8px 0",
              }}>
                Answer
              </h3>
              <div style={{ lineHeight: "1.6", color: "#1e293b" }}>
                <ReactMarkdown
                  components={{
                    strong: ({ node, ...props }) => (
                      <strong style={{ color: "#2563eb" }} {...props} />
                    ),
                    ol: ({ node, ...props }) => (
                      <ol style={{
                        paddingLeft: "20px",
                        margin: "8px 0",
                        listStyleType: 'decimal'
                      }} {...props} />
                    ),
                    ul: ({ node, ...props }) => (
                      <ul style={{
                        paddingLeft: "20px",
                        margin: "8px 0",
                        listStyleType: 'disc'
                      }} {...props} />
                    ),
                    li: ({ node, ...props }) => (
                      <li style={{
                        marginBottom: "4px",
                        paddingLeft: "4px"
                      }} {...props} />
                    ),
                    p: ({ node, ...props }) => (
                      <p style={{ marginBottom: "12px" }} {...props} />
                    ),
                  }}
                >
                  {answer}
                </ReactMarkdown>

                {/* Updated Sources Section */}
                {sources.length > 0 && (
                  <div style={{
                    marginTop: "16px",
                    paddingTop: "16px",
                    borderTop: "1px solid #e2e8f0"
                  }}>
                    <div style={{
                      fontSize: "12px",
                      color: "#64748b",
                      marginBottom: "8px",
                      fontWeight: "500"
                    }}>
                      Sources:
                    </div>
                    <div style={{
                      fontSize: "11px",
                      color: "#475569",
                      fontFamily: "monospace",
                      backgroundColor: "#f1f5f9",
                      padding: "8px",
                      borderRadius: "4px"
                    }}>
                      {sources.map((src, index) => (
                        <div key={index} style={{
                          marginBottom: "4px",
                          display: "flex",
                          alignItems: "flex-start"
                        }}>
                          <span style={{
                            display: "inline-block",
                            marginRight: "8px",
                            color: "#94a3b8"
                          }}>•</span>
                          {`${src.file} (Page ${src.page})`}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div style={{ position: "relative" }}>
              {/* Input */}
              <input
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask a question about your PDFs..."
                style={{
                  width: "100%",
                  height: "48px",
                  padding: "12px 96px 12px 12px",
                  border: "1px solid #cbd5e1",
                  borderRadius: "6px",
                  fontSize: "16px",
                  outline: "none",
                  transition: "all 0.2s",
                  boxSizing: "border-box",
                }}
                onFocus={(e) => {
                  e.target.style.borderColor = "#2563eb"
                  e.target.style.boxShadow = "0 0 0 2px rgba(37, 99, 235, 0.2)"
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = "#cbd5e1"
                  e.target.style.boxShadow = "none"
                }}
                disabled={isLoading}
              />
              {/* Button */}
              <button
                type="submit"
                style={{
                  position: "absolute",
                  right: "4px",
                  top: "4px",
                  height: "40px",
                  padding: "0 16px",
                  backgroundColor: isLoading || !question.trim() ? "#cbd5e1" : "#2563eb",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  fontSize: "14px",
                  fontWeight: "500",
                  cursor: isLoading || !question.trim() ? "not-allowed" : "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                  transition: "background-color 0.2s",
                }}
                onMouseEnter={(e) => {
                  if (!isLoading && question.trim()) {
                    e.currentTarget.style.backgroundColor = "#1d4ed8"
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isLoading && question.trim()) {
                    e.currentTarget.style.backgroundColor = "#2563eb"
                  }
                }}
                disabled={isLoading || !question.trim()}
              >
                {isLoading ? (
                  <>
                    <svg
                      width="16"
                      height="16"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      style={{
                        animation: "spin 1s linear infinite",
                      }}
                    >
                      <path d="M21 12a9 9 0 11-6.219-8.56"></path>
                    </svg>
                    Thinking
                  </>
                ) : (
                  <>
                    <svg
                      width="16"
                      height="16"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <line x1="22" y1="2" x2="11" y2="13"></line>
                      <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                    </svg>
                    Ask
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>

      <style jsx>{`
        @keyframes spin {
          from {
            transform: rotate(0deg);
          }
          to {
            transform: rotate(360deg);
          }
        }
      `}</style>
    </main>
  )
}
