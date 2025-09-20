#!/usr/bin/env python3
"""
PropertyTek LangGraph Chatbot System
Clean, minimal entry point for LangGraph-powered application
"""

import uvicorn
import logging
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Main entry point for LangGraph PropertyTek"""
    print("Starting PropertyTek LangGraph Chatbot System...")
    print(f"Server: http://{settings.HOST}:{settings.PORT}")
    print(f"API Docs: http://{settings.HOST}:{settings.PORT}/docs")
    print(f"Health: http://{settings.HOST}:{settings.PORT}/health")
    print("Powered by: LangGraph Workflow Orchestration")
    print("Features: Google Calendar + Twilio SMS + Property Search")
    
    print("\nSystem ready! Starting LangGraph server...")
    
    # Start the LangGraph-powered FastAPI server
    uvicorn.run(
        "src.chatbot.langgraph_api:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )

if __name__ == "__main__":
    main()