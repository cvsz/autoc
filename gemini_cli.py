#!/usr/bin/env python3
"""
Gemini CLI - A command-line interface for Google Gemini AI
Usage: 
    python gemini_cli.py
    Or set GEMINI_API_KEY in .env file or environment variable
"""

import os
import sys
from google import genai
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from dotenv import load_dotenv
import time
import argparse

# Load environment variables from .env file
load_dotenv()

def setup_gemini():
    """Initialize Gemini API with the provided key."""
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found!")
        print("\n📝 Setup Instructions:")
        print("1. Get your API key from: https://aistudio.google.com/app/apikey")
        print("2. Create a .env file in this directory with:")
        print("   GEMINI_API_KEY=your_api_key_here")
        print("3. Or export it: export GEMINI_API_KEY='your_api_key_here'")
        sys.exit(1)
    
    try:
        client = genai.Client(api_key=api_key)
        return client
    except Exception as e:
        print(f"❌ Error initializing Gemini: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Gemini CLI")
    parser.add_argument("--model", default="gemini-2.0-flash-exp", help="Model to use (gemini-2.0-flash-exp, gemini-pro, gemini-ultra)")
    parser.add_argument("--rpm", type=int, default=15, help="Requests per minute limit")
    args = parser.parse_args()
    
    current_model = args.model
    rpm_limit = args.rpm
    request_timestamps = []

    print("🚀 Gemini CLI - Powered by Google Gemini AI")
    print("=" * 50)
    print(f"Model: {current_model} | Rate limit: {rpm_limit} RPM")
    print("Type 'quit' or 'exit' to end the session")
    print("Type 'clear' to clear the conversation history")
    print("Type '/model <name>' to switch models")
    print("=" * 50 + "\n")
    
    # Initialize Gemini
    client = setup_gemini()
    
    # Conversation history for context
    conversation_history = []
    
    # Create prompt session with history
    history_file = os.path.expanduser("~/.gemini_cli_history")
    session = PromptSession(
        history=FileHistory(history_file),
        auto_suggest=AutoSuggestFromHistory(),
        multiline=False
    )
    
    while True:
        try:
            # Get user input
            user_input = session.prompt("👤 You: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() in ['quit', 'exit']:
                print("\n👋 Goodbye! Thanks for using Gemini CLI.")
                break
            
            if user_input.lower() == 'clear':
                conversation_history = []
                print("\n🧹 Conversation history cleared.\n")
                continue
            
            if user_input.startswith('/model '):
                new_model = user_input.split(' ', 1)[1].strip()
                if new_model:
                    current_model = new_model
                    print(f"\n🔄 Switched to model: {current_model}\n")
                continue

            # Rate Limiting
            now = time.time()
            request_timestamps = [ts for ts in request_timestamps if now - ts < 60]
            if len(request_timestamps) >= rpm_limit:
                sleep_time = 60 - (now - request_timestamps[0])
                print(f"\n⚠️  Rate limit reached ({rpm_limit} RPM). Waiting {sleep_time:.1f}s...\n")
                time.sleep(sleep_time)
                now = time.time()
            request_timestamps.append(now)
            
            # Send message to Gemini
            print("\n🤖 Gemini: ", end="", flush=True)
            
            try:
                # Generate content with conversation history
                response = client.models.generate_content(
                    model=current_model,
                    contents=user_input
                )
                print(response.text)
                print()  # Add empty line for readability
                
            except Exception as e:
                print(f"\n❌ Error: {e}\n")
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user.")
            print("Type 'exit' to quit or continue chatting.\n")
            continue
        except EOFError:
            print("\n\n👋 Goodbye!")
            break

if __name__ == "__main__":
    main()
