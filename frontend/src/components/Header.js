import React from 'react';
import styled from 'styled-components';
import { Home, Search, Calendar, MessageCircle } from 'lucide-react';

// Base URL for API requests (works in both dev and prod)
const API_BASE = (process.env.REACT_APP_API_BASE || '').replace(/\/$/, '');

const HeaderContainer = styled.header`
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 1rem 2rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
`;

const HeaderContent = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Logo = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.5rem;
  font-weight: bold;
  color: #333;
`;

const StatusIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: ${props => props.connected ? '#10b981' : '#ef4444'};
  color: white;
  border-radius: 20px;
  font-size: 0.875rem;
`;

const StatusDot = styled.div`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: white;
  animation: ${props => props.connected ? 'pulse 2s infinite' : 'none'};
  
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }
`;

const Header = () => {
  const [isConnected, setIsConnected] = React.useState(false);

  React.useEffect(() => {
    // Check API connection
    const checkConnection = async () => {
      try {
        const response = await fetch(`${API_BASE}/health`);
        setIsConnected(response.ok);
      } catch (error) {
        setIsConnected(false);
      }
    };

    checkConnection();
    const interval = setInterval(checkConnection, 30000); // Check every 30 seconds

    return () => clearInterval(interval);
  }, []);

  return (
    <HeaderContainer>
      <HeaderContent>
        <Logo>
          <Home size={24} />
          PropertyTek AI Assistant
        </Logo>
        
        <StatusIndicator connected={isConnected}>
          <StatusDot connected={isConnected} />
          {isConnected ? 'Connected' : 'Disconnected'}
        </StatusIndicator>
      </HeaderContent>
    </HeaderContainer>
  );
};

export default Header;