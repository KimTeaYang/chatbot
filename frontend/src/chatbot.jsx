import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './chatApp.css';

const API_BASE_URL = 'http://localhost:8000';

const ChatApp = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState('default');
  const [isConnected, setIsConnected] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    // 컴포넌트 마운트 시 서버 연결 확인
    checkConnection();
    // 이전 대화 기록 불러오기
    loadChatHistory();
  }, [sessionId]);

  useEffect(() => {
    // 새 메시지가 추가될 때마다 스크롤을 맨 아래로
    scrollToBottom();
  }, [messages]);

  const checkConnection = async () => {
    try {
      await axios.get(`${API_BASE_URL}/`);
      setIsConnected(true);
    } catch (error) {
      setIsConnected(false);
      console.error('서버 연결 실패:', error);
    }
  };

  const loadChatHistory = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/v1/chat/history/${sessionId}`);
      const history = response.data.messages;

      const formattedMessages = history.flatMap(msg => [
        {
          id: `user-${msg.timestamp}`,
          text: msg.user,
          sender: 'user',
          timestamp: msg.timestamp
        },
        {
          id: `bot-${msg.timestamp}`,
          text: msg.bot,
          sender: 'bot',
          timestamp: msg.timestamp
        }
      ]);

      setMessages(formattedMessages);
    } catch (error) {
      console.error('대화 기록 로딩 실패:', error);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: `user-${Date.now()}`,
      text: inputMessage,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/v1/chat`, {
        message: inputMessage,
        session_id: sessionId
      });

      const botMessage = {
        id: `bot-${Date.now()}`,
        text: response.data.response,
        sender: 'bot',
        timestamp: new Date(response.data.timestamp).toLocaleTimeString()
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('메시지 전송 실패:', error);

      const errorMessage = {
        id: `error-${Date.now()}`,
        text: '죄송합니다. 오류가 발생했습니다. 다시 시도해주세요.',
        sender: 'bot',
        timestamp: new Date().toLocaleTimeString(),
        isError: true
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const clearChat = async () => {
    try {
      await axios.delete(`${API_BASE_URL}/api/v1/chat/history/${sessionId}`);
      setMessages([]);
    } catch (error) {
      console.error('대화 기록 삭제 실패:', error);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleNewSession = () => {
    const newSessionId = `session-${Date.now()}`;
    setSessionId(newSessionId);
    setMessages([]);
  };

  return (
    <div className="chat-app">
      <div className="chat-header">
        <h1>🤖 Gemini 챗봇</h1>
        <div className="header-controls">
          <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
            {isConnected ? '🟢 연결됨' : '🔴 연결 안됨'}
          </div>
          <button onClick={handleNewSession} className="new-session-btn">
            새 세션
          </button>
          <button onClick={clearChat} className="clear-btn">
            기록 삭제
          </button>
        </div>
      </div>

      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="welcome-message">
            <h3>안녕하세요! 무엇을 도와드릴까요?</h3>
            <p>궁금한 것이 있으면 언제든 물어보세요.</p>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`message ${message.sender} ${message.isError ? 'error' : ''}`}
            >
              <div className="message-content">
                <div className="message-text">
                  {message.text}
                </div>
                <div className="message-timestamp">
                  {message.timestamp}
                </div>
              </div>
            </div>
          ))
        )}

        {isLoading && (
          <div className="message bot">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input">
        <div className="input-container">
          <textarea
            ref={inputRef}
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="메시지를 입력하세요... (Enter: 전송, Shift+Enter: 줄바꿈)"
            disabled={isLoading || !isConnected}
            rows={1}
          />
          <button
            onClick={sendMessage}
            disabled={isLoading || !inputMessage.trim() || !isConnected}
            className="send-btn"
          >
            {isLoading ? '전송중...' : '전송'}
          </button>
        </div>
      </div>

      <div className="session-info">
        세션 ID: {sessionId}
      </div>
    </div>
  );
};

export default ChatApp;