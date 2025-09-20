import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { Send, Bot, User, Loader, Home, Calendar, Phone, X, Check, Clock, AlertCircle } from 'lucide-react';
import { toast } from 'react-toastify';

// Base URL for API requests (works in both dev and prod)
const API_BASE = (process.env.REACT_APP_API_BASE || '').replace(/\/$/, '');

const ChatContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: calc(100vh - 140px);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.95) 100%);
  border-radius: 24px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1), 0 0 0 1px rgba(255, 255, 255, 0.5);
  overflow: hidden;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(102, 126, 234, 0.1);
`;

const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const Message = styled.div`
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
  ${props => props.isUser && 'flex-direction: row-reverse;'}
`;

const MessageBubble = styled.div`
  max-width: 70%;
  min-width: 120px;
  padding: 1.25rem 1.5rem;
  border-radius: 24px;
  background: ${props => props.isUser
    ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    : '#ffffff'};
  color: ${props => props.isUser ? 'white' : '#333'};
  box-shadow: ${props => props.isUser
    ? '0 8px 32px rgba(102, 126, 234, 0.3)'
    : '0 2px 8px rgba(0, 0, 0, 0.1)'};
  word-break: keep-all;
  overflow-wrap: break-word;
  white-space: pre-wrap;
  line-height: 1.6;
  position: relative;
  border: ${props => props.isUser ? 'none' : '1px solid #e5e7eb'};
  font-size: 1rem;
  transition: all 0.3s ease;
  
  /* Prevent aggressive word breaking */
  hyphens: none;
  -webkit-hyphens: none;
  -moz-hyphens: none;
  -ms-hyphens: none;
  
  /* Add hover effects */
  &:hover {
    transform: translateY(-1px);
    box-shadow: ${props => props.isUser
    ? '0 12px 40px rgba(102, 126, 234, 0.4)'
    : '0 4px 12px rgba(0, 0, 0, 0.15)'};
  }
  
  &::before {
    content: '';
    position: absolute;
    ${props => props.isUser ? 'right: -8px;' : 'left: -8px;'}
    top: 50%;
    transform: translateY(-50%);
    width: 0;
    height: 0;
    border-style: solid;
    ${props => props.isUser
    ? 'border-left: 8px solid #667eea; border-top: 8px solid transparent; border-bottom: 8px solid transparent;'
    : 'border-right: 8px solid #ffffff; border-top: 8px solid transparent; border-bottom: 8px solid transparent;'}
  }
`;

const MessageIcon = styled.div`
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: ${props => props.isUser
    ? 'linear-gradient(135deg, #667eea, #764ba2)'
    : '#10b981'};
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
  box-shadow: 0 4px 16px ${props => props.isUser
    ? 'rgba(102, 126, 234, 0.3)'
    : 'rgba(16, 185, 129, 0.3)'};
  transition: all 0.3s ease;
  
  &:hover {
    transform: scale(1.1);
    box-shadow: 0 6px 20px ${props => props.isUser
    ? 'rgba(102, 126, 234, 0.4)'
    : 'rgba(16, 185, 129, 0.4)'};
  }
`;

const InputContainer = styled.div`
  padding: 1rem;
  border-top: 1px solid #e5e7eb;
  background: white;
`;

const InputWrapper = styled.div`
  display: flex;
  gap: 0.75rem;
  align-items: center;
`;

const MessageInput = styled.input`
  flex: 1;
  padding: 1.2rem 1.5rem;
  border: 2px solid rgba(102, 126, 234, 0.2);
  border-radius: 30px;
  outline: none;
  font-size: 1rem;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
  
  &:focus {
    border-color: #667eea;
    background: white;
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
    transform: translateY(-2px);
  }
  
  &:disabled {
    background: rgba(243, 244, 246, 0.8);
    cursor: not-allowed;
  }
  
  &::placeholder {
    color: #9ca3af;
    font-weight: 500;
  }
`;

const SendButton = styled.button`
  width: 54px;
  height: 54px;
  border-radius: 50%;
  border: none;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
  position: relative;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 0;
    height: 0;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 50%;
    transform: translate(-50%, -50%);
    transition: width 0.3s, height 0.3s;
  }
  
  &:hover:not(:disabled) {
    background: linear-gradient(135deg, #5a67d8, #6b46c1);
    transform: scale(1.1) rotate(15deg);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    
    &::before {
      width: 100%;
      height: 100%;
    }
  }
  
  &:disabled {
    background: linear-gradient(135deg, #9ca3af, #6b7280);
    cursor: not-allowed;
    transform: none;
    box-shadow: 0 2px 8px rgba(156, 163, 175, 0.3);
  }
`;

const SuggestionsDisplay = styled.div`
  margin-top: 0.75rem;
  padding: 0.75rem;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
  border-radius: 12px;
  border-left: 4px solid #667eea;
`;

const SuggestionsTitle = styled.div`
  font-size: 0.8rem;
  font-weight: 600;
  color: #667eea;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const SuggestionsList = styled.ul`
  margin: 0;
  padding: 0;
  list-style: none;
`;

const SuggestionItem = styled.li`
  font-size: 0.875rem;
  color: #64748b;
  margin-bottom: 0.25rem;
  padding-left: 1rem;
  position: relative;
  
  &::before {
    content: '•';
    color: #667eea;
    font-weight: bold;
    position: absolute;
    left: 0;
  }
  
  &:last-child {
    margin-bottom: 0;
  }
`;

const PropertyCard = styled.div`
  border: none;
  border-radius: 12px;
  padding: 1rem;
  margin-top: 0.75rem;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  cursor: default;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  max-width: 400px;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
    transform: scaleX(0);
    transition: transform 0.3s ease;
  }
  
  &:hover {
    transform: none;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
    &::before { transform: scaleX(0); }
  }
`;

const PropertyHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
  position: relative;
`;

const PropertyAddress = styled.h4`
  color: #1a202c;
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1.3;
`;

const PropertyPrice = styled.div`
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  font-weight: 700;
  font-size: 0.9rem;
  padding: 0.4rem 0.8rem;
  border-radius: 16px;
  box-shadow: 0 3px 8px rgba(16, 185, 129, 0.25);
  position: relative;
  
  &::after {
    content: '💰';
    position: absolute;
    right: -8px;
    top: -8px;
    font-size: 1.2rem;
  }
`;

const PropertyDetails = styled.div`
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
`;

const DetailItem = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(102, 126, 234, 0.1);
  padding: 0.5rem 1rem;
  border-radius: 12px;
  color: #4c51bf;
  font-weight: 600;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(102, 126, 234, 0.2);
    transform: scale(1.05);
  }
  
  &::before {
    content: '🏠';
    font-size: 1rem;
  }
  
  &:nth-child(2)::before {
    content: '🛏️';
  }
  
  &:nth-child(3)::before {
    content: '🚿';
  }
  
  &:nth-child(4)::before {
    content: '📐';
  }
`;

// Removed unused styled components PropertyAmenities and AmenityTag to fix linter warnings

const InquiryPrompt = styled.div`
  margin-top: 1.25rem;
  padding: 1rem;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
  border-radius: 12px;
  font-size: 0.9rem;
  color: #667eea;
  text-align: center;
  font-weight: 600;
  border: 2px dashed rgba(102, 126, 234, 0.3);
  transition: all 0.3s ease;
  
  &:hover { transform: none; }
`;

const CardActions = styled.div`
  display: flex;
  gap: 0.5rem;
  margin-top: 0.75rem;
`;

const PrimaryButton = styled.button`
  flex: 1;
  padding: 0.6rem 1rem;
  border-radius: 10px;
  border: none;
  color: white;
  background: linear-gradient(135deg, #667eea, #764ba2);
  cursor: pointer;
  font-weight: 700;
  transition: transform 0.15s ease;
  &:hover { transform: translateY(-1px); }
`;

const SecondaryButton = styled.button`
  flex: 1;
  padding: 0.6rem 1rem;
  border-radius: 10px;
  border: 2px solid #667eea;
  color: #667eea;
  background: white;
  cursor: pointer;
  font-weight: 700;
  transition: transform 0.15s ease;
  &:hover { transform: translateY(-1px); }
`;

const DetailsSection = styled.div`
  margin-bottom: 12px;
`;
const SectionTitle = styled.h4`
  margin: 0 0 8px 0;
  color: #374151;
`;
const Tag = styled.span`
  display: inline-block;
  background: #eef2ff;
  color: #4f46e5;
  padding: 4px 8px;
  border-radius: 9999px;
  font-size: 12px;
  margin: 0 6px 6px 0;
`;
const Bullet = styled.li`
  margin-left: 16px;
  color: #4b5563;
`;

const WelcomeMessage = styled.div`
  text-align: center;
  padding: 2rem;
  color: #666;
`;

const WelcomeTitle = styled.h2`
  color: #333;
  margin-bottom: 1rem;
`;

const QuickActions = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: center;
  margin-top: 1.5rem;
`;

const QuickActionButton = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 1.5rem;
  border: 2px solid #667eea;
  background: transparent;
  color: #667eea;
  border-radius: 12px;
  cursor: default;
  transition: all 0.3s ease;
  opacity: 0.8;
`;

const SuggestedActions = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 1rem;
`;

const ActionButton = styled.button`
  padding: 0.5rem 1rem;
  background: #f0f4ff;
  color: #667eea;
  border: 1px solid #667eea;
  border-radius: 20px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
  opacity: 0.8;
  &:hover { opacity: 1; }
`;

// Enhanced Time Selection Modal Components
const ModalOverlay = styled.div`
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(8px);
`;

const ModalContainer = styled.div`
  background: white;
  border-radius: 20px;
  padding: 2rem;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
  position: relative;
`;

const ModalHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #f1f5f9;
`;

const ModalTitle = styled.h3`
  margin: 0;
  color: #1e293b;
  font-size: 1.5rem;
  font-weight: 700;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  
  &:hover {
    background: #f1f5f9;
  }
`;

const TimeSlotGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
`;

const TimeSlotCard = styled.div`
  border: 2px solid ${props => props.selected ? '#667eea' : '#e2e8f0'};
  border-radius: 12px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  background: ${props => props.selected ? 'linear-gradient(135deg, #667eea, #764ba2)' : 'white'};
  color: ${props => props.selected ? 'white' : '#334155'};
  
  &:hover {
    border-color: #667eea;
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
  }
`;

const TimeSlotHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  font-weight: 600;
`;

const TimeSlotDate = styled.div`
  font-size: 0.9rem;
  opacity: 0.8;
`;

const ValidationError = styled.div`
  background: #fee2e2;
  border: 1px solid #fecaca;
  color: #dc2626;
  padding: 0.75rem;
  border-radius: 8px;
  margin: 0.5rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
`;

const SuccessMessage = styled.div`
  background: #dcfce7;
  border: 1px solid #bbf7d0;
  color: #16a34a;
  padding: 0.75rem;
  border-radius: 8px;
  margin: 0.5rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
`;

const ModalActions = styled.div`
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #f1f5f9;
`;

const ConfirmButton = styled.button`
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  
  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const CancelButton = styled.button`
  background: white;
  color: #64748b;
  border: 2px solid #e2e8f0;
  padding: 0.75rem 1.5rem;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: #cbd5e1;
    background: #f8fafc;
  }
`;

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => Math.random().toString(36).substr(2, 9));
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  
  // UI state for modals and forms
  const [detailsModal, setDetailsModal] = useState({ open: false, details: null });
  const [slotsModal, setSlotsModal] = useState({ open: false, propertyId: null, slots: [], selected: null, selectedDates: new Set() });
  // Chat-based iterative info state with validation
  const [infoState, setInfoState] = useState({ 
    active: false, 
    nextField: null, 
    userInfo: { name: '', email: '', phone: '', pets: '' }, 
    propertyId: null, 
    selectedSlot: null,
    validationErrors: {},
    retryCount: 0,
    maxRetries: 3
  });

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Auto-focus the input on mount
    inputRef.current?.focus();
  }, []);

  const sendMessage = async (message) => {
    if (!message.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      text: message,
      isUser: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Create AbortController for timeout handling
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 120000); // 2 minute timeout

      const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: message,
          user_id: sessionId,
          conversation_history: messages.length > 0 ?
            messages.map(m => `${m.isUser ? 'User' : 'Assistant'}: ${m.text}`).join('\n') :
            null
        }),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      const botMessage = {
        id: Date.now() + 1,
        text: data.response,
        isUser: false,
        timestamp: new Date(),
        intent: data.intent,
        suggestedActions: data.suggested_actions || [],
        properties: data.properties || []
      };

      setMessages(prev => [...prev, botMessage]);

    } catch (error) {
      console.error('Error sending message:', error);
      
      let errorMessage = 'Sorry, I encountered an error. Please try again or check if the server is running.';
      
      if (error.name === 'AbortError') {
        errorMessage = 'Request timed out. The server is taking too long to respond. Please try again with a simpler query.';
      } else if (error.message.includes('timeout')) {
        errorMessage = 'Request timed out. Please try again or contact support if the issue persists.';
      }

      toast.error(errorMessage);

      const errorMsg = {
        id: Date.now() + 1,
        text: errorMessage,
        isUser: false,
        timestamp: new Date(),
        isError: true
      };

      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
      // Ensure input regains focus after send completes
      setTimeout(() => inputRef.current?.focus(), 0);
    }
  };

  // Validation functions
  const validateField = (fieldName, value) => {
    const errors = {};
    
    switch (fieldName) {
      case 'name':
        if (!value || value.trim().length < 2) {
          errors.name = 'Please enter a valid full name (at least 2 characters)';
        } else if (!/^[a-zA-Z\s'-]+$/.test(value.trim())) {
          errors.name = 'Name can only contain letters, spaces, hyphens, and apostrophes';
        }
        break;
      
      case 'email':
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!value || !emailRegex.test(value.trim())) {
          errors.email = 'Please enter a valid email address (e.g., john@example.com)';
        }
        break;
      
      case 'phone':
        const cleanPhone = value.replace(/[\s\-\(\)\.]/g, '');
        // Accept either:
        // - International format: +[country code][number], 10–15 digits total, country code cannot start with 0
        // - Local format: starts with 0, 10–15 digits total
        const intlPattern = /^\+[1-9]\d{9,14}$/;      // + followed by 10–15 digits
        const localPattern = /^0\d{9,14}$/;            // 0 followed by 9–14 digits (10–15 total)
        const plainDigitsPattern = /^[1-9]\d{9,14}$/;  // Optional: numbers without + or leading 0
        const isValidPhone = intlPattern.test(cleanPhone)
          || localPattern.test(cleanPhone)
          || plainDigitsPattern.test(cleanPhone);
        if (!value || !isValidPhone) {
          errors.phone = 'Please enter a valid phone number (10–15 digits). Examples: 01765786548 or +441234567890';
        }
        break;
      
      case 'pets':
        if (!value || value.trim().length === 0) {
          errors.pets = 'Please specify if you have pets or enter "None"';
        }
        break;
      
      default:
        break;
    }
    
    return errors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const message = inputValue;
    if (!message.trim() || isLoading) return;

    // If we're in iterative info collection mode, treat user input as value for next field
    if (infoState.active && infoState.nextField) {
      const fieldName = infoState.nextField;
      const fieldValue = message.trim();
      
      // Validate the field
      const validationErrors = validateField(fieldName, fieldValue);
      
      if (Object.keys(validationErrors).length > 0) {
        // Validation failed
        const newRetryCount = infoState.retryCount + 1;
        
        if (newRetryCount >= infoState.maxRetries) {
          // Max retries reached, offer to cancel or restart
          setMessages(prev => [...prev, 
            { id: Date.now(), text: message, isUser: true, timestamp: new Date() },
            { 
              id: Date.now() + 1, 
              text: `I notice you're having trouble with this information. Would you like to:\n1. Cancel this booking\n2. Start over\n3. Get help with the format\n\nPlease type "cancel", "restart", or "help".`, 
              isUser: false, 
              timestamp: new Date() 
            }
          ]);
          setInfoState(prev => ({ 
            ...prev, 
            validationErrors, 
            retryCount: newRetryCount,
            nextField: 'help_or_cancel'
          }));
        } else {
          // Show validation error and ask again
          const errorMessage = validationErrors[fieldName];
          setMessages(prev => [...prev, 
            { id: Date.now(), text: message, isUser: true, timestamp: new Date() },
            { 
              id: Date.now() + 1, 
              text: `${errorMessage}\n\nPlease try again (attempt ${newRetryCount}/${infoState.maxRetries}):`, 
              isUser: false, 
              timestamp: new Date() 
            }
          ]);
          setInfoState(prev => ({ 
            ...prev, 
            validationErrors, 
            retryCount: newRetryCount 
          }));
        }
        setInputValue('');
        return;
      }
      
      // Handle special help/cancel commands
      if (infoState.nextField === 'help_or_cancel') {
        const command = fieldValue.toLowerCase();
        if (command === 'cancel') {
          setInfoState({ 
            active: false, 
            nextField: null, 
            userInfo: { name: '', email: '', phone: '', pets: '' }, 
            propertyId: null, 
            selectedSlot: null,
            validationErrors: {},
            retryCount: 0,
            maxRetries: 3
          });
          setMessages(prev => [...prev, 
            { id: Date.now(), text: message, isUser: true, timestamp: new Date() },
            { 
              id: Date.now() + 1, 
              text: 'Booking cancelled. You can start a new booking anytime!', 
              isUser: false, 
              timestamp: new Date() 
            }
          ]);
          setInputValue('');
          return;
        } else if (command === 'restart') {
          setInfoState(prev => ({ 
            ...prev, 
            nextField: 'name',
            userInfo: { name: '', email: '', phone: '', pets: '' },
            validationErrors: {},
            retryCount: 0
          }));
          setMessages(prev => [...prev, 
            { id: Date.now(), text: message, isUser: true, timestamp: new Date() },
            { 
              id: Date.now() + 1, 
              text: 'Let\'s start over. What\'s your full name?', 
              isUser: false, 
              timestamp: new Date() 
            }
          ]);
          setInputValue('');
          return;
        } else if (command === 'help') {
          const helpMessages = {
            name: 'Please enter your full name using only letters, spaces, hyphens, and apostrophes. Example: "John Smith" or "Mary-Jane O\'Connor"',
            email: 'Please enter a valid email address. Example: "john.smith@email.com"',
            phone: 'Please enter your phone number with 10–15 digits. Local examples: "01765786548", "07123 456789". International examples: "+44 7123 456789"',
            pets: 'Please specify your pet situation. Examples: "1 dog", "2 cats", "No pets", or "None"'
          };
          
          // Find the original field that was causing trouble
          const originalField = Object.keys(infoState.validationErrors)[0] || 'name';
          setMessages(prev => [...prev, 
            { id: Date.now(), text: message, isUser: true, timestamp: new Date() },
            { 
              id: Date.now() + 1, 
              text: `${helpMessages[originalField]}\n\nNow please try again:`, 
              isUser: false, 
              timestamp: new Date() 
            }
          ]);
          setInfoState(prev => ({ 
            ...prev, 
            nextField: originalField,
            validationErrors: {},
            retryCount: 0
          }));
          setInputValue('');
          return;
        }
      }
      
      // Validation passed, proceed with the field
      const updatedUserInfo = { ...infoState.userInfo, [fieldName]: fieldValue };
      setMessages(prev => [...prev, { id: Date.now(), text: message, isUser: true, timestamp: new Date() }]);
      setInputValue('');
      setIsLoading(true);
      
      try {
        const resp = await fetch(`${API_BASE}/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            query: 'Provide user info',
            user_id: sessionId,
            action_type: 'provide_info',
            property_id: infoState.propertyId,
            selected_slot: infoState.selectedSlot?.datetime || infoState.selectedSlot,
            user_info: updatedUserInfo
          })
        });
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const data = await resp.json();
        
        // If booking completes
        if (data.current_step === 'booking_complete') {
          setInfoState({ 
            active: false, 
            nextField: null, 
            userInfo: { name: '', email: '', phone: '', pets: '' }, 
            propertyId: null, 
            selectedSlot: null,
            validationErrors: {},
            retryCount: 0,
            maxRetries: 3
          });
          setMessages(prev => [...prev, { 
            id: Date.now() + 1, 
            text: data.response || 'Booking complete! You will receive a confirmation SMS and calendar invitation shortly.', 
            isUser: false, 
            timestamp: new Date() 
          }]);
        } else if (data.requires_user_info) {
          // Continue prompting for next field, reset retry count for new field
          setInfoState(prev => ({ 
            ...prev, 
            nextField: data.next_field, 
            userInfo: updatedUserInfo,
            validationErrors: {},
            retryCount: 0
          }));
          setMessages(prev => [...prev, { 
            id: Date.now() + 2, 
            text: data.info_prompt || 'Please provide the next detail.', 
            isUser: false, 
            timestamp: new Date() 
          }]);
        } else {
          setInfoState(prev => ({ ...prev, active: false }));
        }
      } catch (err) {
        toast.error('Failed to submit info. Please try again.');
      } finally {
        setIsLoading(false);
        setTimeout(() => inputRef.current?.focus(), 0);
      }
      return;
    }

    // Normal chat message
    setInputValue('');
    setIsLoading(true);
    const userMessage = { id: Date.now(), text: message, isUser: true, timestamp: new Date() };
    setMessages(prev => [...prev, userMessage]);
    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: message,
          user_id: sessionId,
          conversation_history: messages.length > 0 ?
            messages.map(m => `${m.isUser ? 'User' : 'Assistant'}: ${m.text}`).join('\n') :
            null
        }),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      const botMessage = {
        id: Date.now() + 1,
        text: data.response,
        isUser: false,
        timestamp: new Date(),
        intent: data.intent,
        suggestedActions: data.suggested_actions || [],
        properties: data.properties || []
      };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      toast.error('Failed to send message. Please check your connection.');
      const errorMessage = {
        id: Date.now() + 1,
        text: 'Sorry, I encountered an error. Please try again or check if the server is running.',
        isUser: false,
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setTimeout(() => inputRef.current?.focus(), 0);
    }
  };


  const inquireProperty = async (property) => {
    try {
      const resp = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: `Show details for property ${property.id}`,
          user_id: sessionId,
          action_type: 'inquire',
          property_id: String(property.id)
        })
      });
      const data = await resp.json();
      if (data.property_details) {
        setDetailsModal({ open: true, details: data.property_details });
      }
    } catch (e) {
      toast.error('Failed to load property details');
    }
  };

  const bookProperty = async (property) => {
    try {
      const resp = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: `Book schedule for property ${property.id}`,
          user_id: sessionId,
          action_type: 'book_schedule',
          property_id: String(property.id)
        })
      });
      const data = await resp.json();
      setSlotsModal({ 
        open: true, 
        propertyId: String(property.id), 
        slots: data.available_slots || [], 
        selected: null, 
        selectedDates: new Set() 
      });
    } catch (e) {
      toast.error('Failed to load available slots');
    }
  };

  // Enhanced slot selection with date toggle
  const toggleSlotSelection = (slot) => {
    setSlotsModal(prev => {
      const currentSelectedDates = prev.selectedDates || new Set();
      const newSelectedDates = new Set(currentSelectedDates);
      const slotId = slot.id || slot.datetime || slot;
      
      if (newSelectedDates.has(slotId)) {
        newSelectedDates.delete(slotId);
      } else {
        newSelectedDates.add(slotId);
      }
      
      return {
        ...prev,
        selectedDates: newSelectedDates,
        selected: newSelectedDates.size > 0 ? Array.from(newSelectedDates)[0] : null
      };
    });
  };

  const confirmSlotSelection = async () => {
    const selectedSlotIds = Array.from(slotsModal.selectedDates || new Set());
    if (selectedSlotIds.length === 0) {
      toast.error('Please select at least one time slot');
      return;
    }

    // For now, use the first selected slot (can be enhanced for multiple slots later)
    const selectedSlot = slotsModal.slots.find(slot => 
      selectedSlotIds.includes(slot.id || slot.datetime || slot)
    );

    if (!selectedSlot) {
      toast.error('Selected slot not found');
      return;
    }

    try {
      const resp = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: `Select slot ${selectedSlot.datetime || selectedSlot}`,
          user_id: sessionId,
          action_type: 'select_slot',
          property_id: slotsModal.propertyId,
          selected_slot: selectedSlot.datetime || selectedSlot
        })
      });
      const data = await resp.json();
      
      // Close the slots modal
      setSlotsModal({ open: false, propertyId: null, slots: [], selected: null, selectedDates: new Set() });
      
      if (data.requires_user_info) {
        // Start chat-based iterative collection with validation
        setInfoState({ 
          active: true, 
          nextField: data.next_field, 
          userInfo: { name: '', email: '', phone: '', pets: '' }, 
          propertyId: String(slotsModal.propertyId), 
          selectedSlot: selectedSlot,
          validationErrors: {},
          retryCount: 0,
          maxRetries: 3
        });
        setMessages(prev => [...prev, { 
          id: Date.now() + Math.random(), 
          text: data.info_prompt || 'Please provide your details to complete the booking.', 
          isUser: false, 
          timestamp: new Date() 
        }]);
      } else if (data.current_step === 'booking_complete') {
        setInfoState({ 
          active: false, 
          nextField: null, 
          userInfo: { name: '', email: '', phone: '', pets: '' }, 
          propertyId: null, 
          selectedSlot: null,
          validationErrors: {},
          retryCount: 0,
          maxRetries: 3
        });
        setMessages(prev => [...prev, { 
          id: Date.now() + Math.random(), 
          text: data.response || 'Booking complete!', 
          isUser: false, 
          timestamp: new Date() 
        }]);
      }
    } catch (e) {
      toast.error('Failed to process slot selection');
    }
  };

  const cancelBooking = () => {
    setSlotsModal({ open: false, propertyId: null, slots: [], selected: null, selectedDates: new Set() });
    setInfoState({ 
      active: false, 
      nextField: null, 
      userInfo: { name: '', email: '', phone: '', pets: '' }, 
      propertyId: null, 
      selectedSlot: null,
      validationErrors: {},
      retryCount: 0,
      maxRetries: 3
    });
    
    // Notify backend about cancellation
    fetch(`${API_BASE}/chat`, {
      method: 'POST', 
      headers: { 'Content-Type': 'application/json' }, 
      body: JSON.stringify({
        query: 'Cancel booking', 
        user_id: sessionId, 
        action_type: 'cancel_booking', 
        property_id: slotsModal.propertyId
      })
    });
    
    toast.success('Booking cancelled successfully');
  };

  const renderProperty = (property) => {
    if (property && property._no_exact_match) {
      return (
        <PropertyCard key={`suggestion-${Math.random()}`}>
          <PropertyHeader>
            <div>
              <PropertyAddress>Suggestion</PropertyAddress>
            </div>
          </PropertyHeader>
          <div style={{ color: '#475569' }}>
            {property._suggestion_message || 'No exact matches. Try adjusting your filters.'}
          </div>
        </PropertyCard>
      );
    }

    return (
      <PropertyCard key={property.id}>
        <PropertyHeader>
          <div>
            <PropertyAddress>{property.address}</PropertyAddress>
          </div>
          <PropertyPrice>${property.rent}/month</PropertyPrice>
        </PropertyHeader>

        <PropertyDetails>
          <DetailItem>🛏️ {property.bedrooms} bed</DetailItem>
          <DetailItem>🐾 {property.pets || 'Pet policy not specified'}</DetailItem>
        </PropertyDetails>

        <InquiryPrompt>
          Choose an action below
        </InquiryPrompt>
        <CardActions>
          <SecondaryButton onClick={() => inquireProperty(property)}>Click to Inquire</SecondaryButton>
          <PrimaryButton onClick={() => bookProperty(property)}>Book Schedule</PrimaryButton>
        </CardActions>
      </PropertyCard>
    );
  };

  return (
    <ChatContainer>
      <MessagesContainer>
        {messages.length === 0 ? (
          <WelcomeMessage>
            <WelcomeTitle>Welcome to PropertyTek AI Assistant! 🏠</WelcomeTitle>
            <p>I'm here to help you find properties, schedule tours, and answer your questions.</p>

            <QuickActions>
              <QuickActionButton>
                <Home size={16} />
                Find Properties
              </QuickActionButton>
              <QuickActionButton>
                <Calendar size={16} />
                Schedule Tour
              </QuickActionButton>
              <QuickActionButton>
                <Phone size={16} />
                Get Help
              </QuickActionButton>
            </QuickActions>
          </WelcomeMessage>
        ) : (
          messages.map((message) => (
            <Message key={message.id} isUser={message.isUser}>
              <MessageIcon isUser={message.isUser}>
                {message.isUser ? <User size={20} /> : <Bot size={20} />}
              </MessageIcon>
              <div>
                <MessageBubble isUser={message.isUser}>
                  {message.text.split('\n').map((line, index) => (
                    <div key={index}>
                      {line}
                      {index < message.text.split('\n').length - 1 && <br />}
                    </div>
                  ))}
                </MessageBubble>

                {message.properties && Array.isArray(message.properties) && message.properties.length > 0 && (
                  <div>
                    {message.properties.map(renderProperty)}
                  </div>
                )}

                {message.suggestedActions && message.suggestedActions.length > 0 && (
                  <SuggestedActions>
                    {message.suggestedActions.map((action, index) => (
                      <ActionButton key={index} onClick={() => sendMessage(action)}>
                        {action}
                      </ActionButton>
                    ))}
                  </SuggestedActions>
                )}
              </div>
            </Message>
          ))
        )}

        {isLoading && (
          <Message isUser={false}>
            <MessageIcon isUser={false}>
              <Loader size={20} className="animate-spin" />
            </MessageIcon>
            <MessageBubble isUser={false}>
              Thinking...
            </MessageBubble>
          </Message>
        )}

        <div ref={messagesEndRef} />
      </MessagesContainer>

      <InputContainer>
        <form onSubmit={handleSubmit}>
          <InputWrapper>
            <MessageInput
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Ask me about properties, schedule tours, or get help..."
              readOnly={isLoading}
              ref={inputRef}
              autoFocus
            />
            <SendButton 
              type="submit" 
              disabled={isLoading || !inputValue.trim()}
              onMouseDown={(e) => {
                // Prevent button from stealing focus from the input
                e.preventDefault();
              }}
            >
              {isLoading ? <Loader size={20} className="animate-spin" /> : <Send size={20} />}
            </SendButton>
          </InputWrapper>
        </form>
      </InputContainer>

      {detailsModal.open && (
        <div style={{position:'fixed', inset:0, background:'rgba(0,0,0,0.4)', display:'flex', alignItems:'center', justifyContent:'center'}}>
          <div style={{background:'#fff', borderRadius:12, padding:20, maxWidth:720, width:'92%', maxHeight:'80vh', overflow:'hidden', display:'flex', flexDirection:'column'}}>
            <h3 style={{marginTop:0, marginBottom:16, flexShrink:0}}>Property Details</h3>
            <div style={{overflowY:'auto', flex:1, paddingRight:8}}>
              {(() => {
                const d = detailsModal.details || {};
                const basic = d.basic_info || {};
                const amenities = d.amenities || [];
                const loc = d.location_info || {};
                const lease = d.lease_terms || {};
                const contact = d.contact_info || {};
                return (
                  <div>
                    <DetailsSection>
                      <SectionTitle>Address</SectionTitle>
                      <div>{basic.address || 'N/A'}</div>
                    </DetailsSection>
                    <DetailsSection>
                      <SectionTitle>Basic Info</SectionTitle>
                      <div style={{display:'grid', gridTemplateColumns:'repeat(auto-fit, minmax(180px, 1fr))', gap:8}}>
                        <div><strong>Bedrooms:</strong> {basic.bedrooms ?? 'N/A'}</div>
                        <div><strong>Bathrooms:</strong> {basic.bathrooms ?? 'N/A'}</div>
                        <div><strong>Rent:</strong> {basic.rent ? `$${basic.rent}` : 'N/A'}</div>
                        <div><strong>Available:</strong> {basic.available_date || 'N/A'}</div>
                        <div><strong>Pet policy:</strong> {basic.pet_policy || 'N/A'}</div>
                      </div>
                    </DetailsSection>
                    {d.description && (
                      <DetailsSection>
                        <SectionTitle>Description</SectionTitle>
                        <div style={{color:'#4b5563'}}>{d.description}</div>
                      </DetailsSection>
                    )}
                    {amenities.length > 0 && (
                      <DetailsSection>
                        <SectionTitle>Amenities</SectionTitle>
                        <div>
                          {amenities.map((a, i) => (<Tag key={i}>{a}</Tag>))}
                        </div>
                      </DetailsSection>
                    )}
                    {Object.keys(loc).length > 0 && (
                      <DetailsSection>
                        <SectionTitle>Location</SectionTitle>
                        <ul style={{padding:0, margin:0, listStyle:'disc'}}>
                          {loc.neighborhood && (<Bullet>Neighborhood: {loc.neighborhood}</Bullet>)}
                          {Array.isArray(loc.nearby_amenities) && loc.nearby_amenities.map((x, i)=>(<Bullet key={i}>{x}</Bullet>))}
                          {loc.school_district && (<Bullet>School District: {loc.school_district}</Bullet>)}
                          {loc.walkability_score && (<Bullet>Walkability: {loc.walkability_score}</Bullet>)}
                        </ul>
                      </DetailsSection>
                    )}
                    {Object.keys(lease).length > 0 && (
                      <DetailsSection>
                        <SectionTitle>Lease Terms</SectionTitle>
                        <ul style={{padding:0, margin:0, listStyle:'disc'}}>
                          {lease.lease_length && (<Bullet>Lease Length: {lease.lease_length}</Bullet>)}
                          {lease.security_deposit && (<Bullet>Security Deposit: {lease.security_deposit}</Bullet>)}
                          {lease.application_fee && (<Bullet>Application Fee: {lease.application_fee}</Bullet>)}
                          {lease.utilities_included && (<Bullet>Utilities Included: {lease.utilities_included}</Bullet>)}
                          {lease.utilities_tenant_pays && (<Bullet>Tenant Pays: {lease.utilities_tenant_pays}</Bullet>)}
                          {Array.isArray(lease.move_in_requirements) && lease.move_in_requirements.map((x, i)=>(<Bullet key={i}>{x}</Bullet>))}
                        </ul>
                      </DetailsSection>
                    )}
                    {Object.keys(contact).length > 0 && (
                      <DetailsSection>
                        <SectionTitle>Contact</SectionTitle>
                        <div style={{display:'grid', gridTemplateColumns:'repeat(auto-fit, minmax(220px, 1fr))', gap:8}}>
                          {contact.leasing_office && (<div><strong>Phone:</strong> {contact.leasing_office}</div>)}
                          {contact.email && (<div><strong>Email:</strong> {contact.email}</div>)}
                          {contact.office_hours && (<div><strong>Office Hours:</strong> {contact.office_hours}</div>)}
                        </div>
                      </DetailsSection>
                    )}
                  </div>
                );
              })()}
            </div>
            <div style={{display:'flex', justifyContent:'flex-end', gap:8, marginTop:16, flexShrink:0}}>
              <SecondaryButton onClick={()=>setDetailsModal({open:false, details:null})}>Close</SecondaryButton>
            </div>
          </div>
        </div>
      )}

      {slotsModal.open && (
        <ModalOverlay>
          <ModalContainer>
            <ModalHeader>
              <ModalTitle>
                <Clock size={24} style={{ marginRight: '0.5rem' }} />
                Select Available Times
              </ModalTitle>
              <CloseButton onClick={cancelBooking}>
                <X size={20} />
              </CloseButton>
            </ModalHeader>

            <div style={{ marginBottom: '1rem', color: '#64748b', fontSize: '0.9rem' }}>
              Click on time slots to select/deselect them. Selected slots will be highlighted.
            </div>

            <TimeSlotGrid>
              {(slotsModal.slots || []).map((slot, idx) => {
                const slotId = slot.id || slot.datetime || slot;
                const isSelected = slotsModal.selectedDates ? slotsModal.selectedDates.has(slotId) : false;
                
                return (
                  <TimeSlotCard 
                    key={idx} 
                    selected={isSelected}
                    onClick={() => toggleSlotSelection(slot)}
                  >
                    <TimeSlotHeader>
                      {isSelected ? <Check size={16} /> : <Clock size={16} />}
                      {slot.display || slot.formatted_time || 'Available Slot'}
                    </TimeSlotHeader>
                    <TimeSlotDate>
                      {slot.datetime || slot}
                    </TimeSlotDate>
                  </TimeSlotCard>
                );
              })}
            </TimeSlotGrid>

            {slotsModal.selectedDates && slotsModal.selectedDates.size > 0 && (
              <SuccessMessage>
                <Check size={16} />
                {slotsModal.selectedDates.size} time slot{slotsModal.selectedDates.size > 1 ? 's' : ''} selected
              </SuccessMessage>
            )}

            <ModalActions>
              <CancelButton onClick={cancelBooking}>
                Cancel Booking
              </CancelButton>
              <ConfirmButton 
                onClick={confirmSlotSelection}
                disabled={!slotsModal.selectedDates || slotsModal.selectedDates.size === 0}
              >
                Confirm Selection
              </ConfirmButton>
            </ModalActions>
          </ModalContainer>
        </ModalOverlay>
      )}

      {/* Removed the user details modal; iterative collection now happens in chat only */}
    </ChatContainer>
  );
};

export default ChatInterface;