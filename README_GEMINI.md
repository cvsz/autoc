# 🚀 Gemini CLI

A powerful command-line interface for Google Gemini AI with conversation history and interactive features.

## Features

- 💬 Interactive chat with Google Gemini AI
- 📜 Persistent conversation history
- ⌨️ Command-line auto-suggestions
- 🔐 Secure API key management via `.env` file
- 🧹 Clear conversation history command
- ✨ Clean, user-friendly interface

## Prerequisites

- Python 3.8+
- Google Gemini API Key

## Installation

All dependencies are already installed:
- `google-generativeai` - Google's official Gemini SDK
- `prompt_toolkit` - Enhanced CLI experience
- `python-dotenv` - Environment variable management

## Setup

### 1. Get Your API Key

Visit [Google AI Studio](https://aistudio.google.com/app/apikey) to get your free API key.

### 2. Configure API Key

**Option A: Using .env file (Recommended)**
```bash
# Edit the .env file in this directory
GEMINI_API_KEY=your_actual_api_key_here
```

**Option B: Environment Variable**
```bash
export GEMINI_API_KEY='your_actual_api_key_here'
```

## Usage

### Start the CLI
```bash
python gemini_cli.py
```

Or make it executable and run directly:
```bash
./gemini_cli.py
```

### Commands

| Command | Description |
|---------|-------------|
| `quit` or `exit` | Exit the CLI |
| `clear` | Clear conversation history |
| Any other text | Chat with Gemini |

### Example Session

```
🚀 Gemini CLI - Powered by Google Gemini AI
==================================================
Type 'quit' or 'exit' to end the session
Type 'clear' to clear the conversation history
==================================================

👤 You: What is quantum computing?

🤖 Gemini: Quantum computing is a type of computation that harnesses quantum mechanical phenomena...

👤 You: Thanks!

🤖 Gemini: You're welcome! Feel free to ask more questions.

👤 You: exit

👋 Goodbye! Thanks for using Gemini CLI.
```

## File Structure

```
/workspace/
├── gemini_cli.py      # Main CLI script
├── .env               # API key configuration (create this)
├── .env.example       # Example configuration
└── README_GEMINI.md   # This file
```

## Troubleshooting

### "GEMINI_API_KEY not found"
- Ensure you've created a `.env` file with your API key
- Or export the environment variable before running

### API Errors
- Check your internet connection
- Verify your API key is valid at https://aistudio.google.com/
- Check your API quota limits

## Notes

- Conversation history is stored in `~/.gemini_cli_history`
- The CLI uses `gemini-1.5-flash` model for fast responses
- Your API key is never logged or shared

## License

MIT License - Feel free to use and modify!
