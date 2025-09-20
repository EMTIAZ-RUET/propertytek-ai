import React from 'react';
import styled from 'styled-components';
import ChatInterface from './components/ChatInterface';
import Header from './components/Header';

const AppContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
`;

const MainContent = styled.div`
  display: flex;
  flex-direction: column;
`;

const ContentArea = styled.div`
  flex: 1;
  padding: 20px;
  overflow-y: auto;
`;

function App() {
  return (
    <AppContainer>
      <MainContent>
        <Header />
        <ContentArea>
          <ChatInterface />
        </ContentArea>
      </MainContent>
    </AppContainer>
  );
}

export default App;