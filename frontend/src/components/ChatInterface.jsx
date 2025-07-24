import React, { useState, useEffect, useRef } from 'react'
import { Send, Bot, User, Loader, Zap } from 'lucide-react'

const ChatInterface = ({ currentProject }) => {
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isModelLoaded, setIsModelLoaded] = useState(false)
  const [wsConnection, setWsConnection] = useState(null)
  const [streamingResponse, setStreamingResponse] = useState('')
  const [chatConfig, setChatConfig] = useState({
    temperature: 0.7,
    maxTokens: 150
  })
  const [metrics, setMetrics] = useState({})
  
  const messagesEndRef = useRef(null)
  const clientId = useRef(Math.random().toString(36).substr(2, 9))

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, streamingResponse])

  useEffect(() => {
    if (currentProject && !isModelLoaded) {
      loadModel()
    }
  }, [currentProject])

  const loadModel = async () => {
    if (!currentProject) return

    try {
      setIsLoading(true)
      const response = await fetch('/chat-api/load-model', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          project_slug: currentProject
        })
      })

      if (response.ok) {
        setIsModelLoaded(true)
        connectWebSocket()
      } else {
        const error = await response.json()
        console.error('Model loading failed:', error)
        alert('Failed to load model: ' + error.detail)
      }
    } catch (error) {
      console.error('Model loading error:', error)
      alert('Failed to load model: ' + error.message)
    } finally {
      setIsLoading(false)
    }
  }

  const connectWebSocket = () => {
    if (wsConnection) {
      wsConnection.close()
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.hostname}:8001/chat-stream/${currentProject}/${clientId.current}`
    
    const ws = new WebSocket(wsUrl)
    
    ws.onopen = () => {
      console.log('WebSocket connected')
      setWsConnection(ws)
    }
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      
      switch (data.type) {
        case 'message_received':
          setIsLoading(true)
          setStreamingResponse('')
          break
          
        case 'token':
          setStreamingResponse(prev => prev + data.token)
          break
          
        case 'complete':
          const finalResponse = streamingResponse
          setMessages(prev => [...prev, {
            type: 'assistant',
            content: finalResponse,
            timestamp: new Date()
          }])
          setStreamingResponse('')
          setIsLoading(false)
          setMetrics({
            latency: data.latency_ms,
            inputTokens: data.input_tokens,
            outputTokens: data.output_tokens,
            totalTokens: data.total_tokens
          })
          break
          
        case 'error':
          console.error('WebSocket error:', data.error)
          setIsLoading(false)
          setStreamingResponse('')
          break
      }
    }
    
    ws.onclose = () => {
      console.log('WebSocket disconnected')
      setWsConnection(null)
    }
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      setWsConnection(null)
    }
  }

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading || !wsConnection) return

    const userMessage = {
      type: 'user',
      content: inputMessage.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    
    // Send via WebSocket for streaming
    wsConnection.send(JSON.stringify({
      message: inputMessage.trim(),
      temperature: chatConfig.temperature,
      max_tokens: chatConfig.maxTokens
    }))

    setInputMessage('')
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  if (!currentProject) {
    return (
      <div className="bg-white rounded-lg p-6 shadow-sm border">
        <div className="text-center text-gray-500">
          <Bot className="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <p>Please select a project and complete training to start chatting.</p>
        </div>
      </div>
    )
  }

  if (!isModelLoaded && !isLoading) {
    return (
      <div className="bg-white rounded-lg p-6 shadow-sm border">
        <div className="text-center">
          <Bot className="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <p className="mb-4">Model not loaded. Click to load your trained model.</p>
          <button
            onClick={loadModel}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            Load Model
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border h-[600px] flex flex-col">
      {/* Header */}
      <div className="border-b p-4 flex items-center justify-between">
        <div className="flex items-center">
          <Bot className="w-6 h-6 text-blue-600 mr-2" />
          <div>
            <h3 className="font-medium">Chat with {currentProject}</h3>
            <p className="text-xs text-gray-500">
              {isModelLoaded ? 'Model loaded' : 'Loading model...'}
            </p>
          </div>
        </div>
        
        {/* Chat Configuration */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <label className="text-xs text-gray-500">Temp:</label>
            <input
              type="range"
              min="0.1"
              max="1.0"
              step="0.1"
              value={chatConfig.temperature}
              onChange={(e) => setChatConfig(prev => ({ 
                ...prev, 
                temperature: parseFloat(e.target.value) 
              }))}
              className="w-16"
            />
            <span className="text-xs text-gray-500 w-8">
              {chatConfig.temperature}
            </span>
          </div>
          
          {metrics.latency && (
            <div className="text-xs text-gray-500">
              <Zap className="w-3 h-3 inline mr-1" />
              {metrics.latency}ms
            </div>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-8">
            <Bot className="w-12 h-12 mx-auto mb-4 text-gray-300" />
            <p>Start a conversation with your trained model!</p>
            <p className="text-sm mt-2">
              Try asking: "Tell me a bedtime story involving a clockwork kangaroo."
            </p>
          </div>
        )}
        
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`
                max-w-xs lg:max-w-md px-4 py-2 rounded-lg flex items-start space-x-2
                ${message.type === 'user' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-100 text-gray-900'
                }
              `}
            >
              <div className="flex-shrink-0 mt-0.5">
                {message.type === 'user' ? (
                  <User className="w-4 h-4" />
                ) : (
                  <Bot className="w-4 h-4" />
                )}
              </div>
              <div className="flex-1">
                <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                <p className="text-xs opacity-70 mt-1">
                  {message.timestamp.toLocaleTimeString()}
                </p>
              </div>
            </div>
          </div>
        ))}
        
        {/* Streaming Response */}
        {(streamingResponse || isLoading) && (
          <div className="flex justify-start">
            <div className="max-w-xs lg:max-w-md px-4 py-2 rounded-lg bg-gray-100 text-gray-900 flex items-start space-x-2">
              <div className="flex-shrink-0 mt-0.5">
                <Bot className="w-4 h-4" />
              </div>
              <div className="flex-1">
                {streamingResponse ? (
                  <p className="text-sm whitespace-pre-wrap">
                    {streamingResponse}
                    <span className="animate-pulse">|</span>
                  </p>
                ) : (
                  <div className="flex items-center space-x-2">
                    <Loader className="w-4 h-4 animate-spin" />
                    <span className="text-sm">Thinking...</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t p-4">
        <div className="flex space-x-2">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            disabled={isLoading || !isModelLoaded}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          />
          <button
            onClick={sendMessage}
            disabled={!inputMessage.trim() || isLoading || !isModelLoaded}
            className="bg-blue-600 text-white p-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
        
        {/* Token Counter */}
        {metrics.totalTokens && (
          <div className="mt-2 text-xs text-gray-500 flex justify-between">
            <span>
              Tokens: {metrics.inputTokens} in + {metrics.outputTokens} out = {metrics.totalTokens} total
            </span>
            <span>Latency: {metrics.latency}ms</span>
          </div>
        )}
      </div>
    </div>
  )
}

export default ChatInterface