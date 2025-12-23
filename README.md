# DeepSeek Reverse Client

**ANYTHING HAPPENING TO YOUR ACCOUNT ISN'T MY LIABILITY, ALSO PLS CONTRIBUTE LIKE I M SO LAZY SKIPPED MULTIPLE STUFF.**


A reverse-engineered Python client for DeepSeek AI that bypasses the web interface and provides direct API access with advanced features like deep thinking and web search capabilities.

## Features

### Current Features
- **Direct API Access**: Bypass the web interface and communicate directly with DeepSeek's backend
- **Authentication Management**: Automated login with session persistence and token management
- **Interactive Chat Mode**: Real-time conversation with streaming responses
- **Single Prompt Mode**: Execute one-off queries from command line
- **Deep Thinking**: Enable DeepSeek's advanced reasoning mode for complex problems
- **Web Search Integration**: Allow the AI to search the web for current information
- **Session Persistence**: Maintain conversation context across multiple interactions
- **Proof of Work Solving**: Automatically handle DeepSeek's anti-bot challenges using WebAssembly
- **Rich Console Output**: Beautiful terminal interface with colored status messages
- **Headless Browser Automation**: Seamless credential extraction without GUI interference

### Planned Features (Goals)
- **Enhanced CLI Interface**: Improved command-line experience with better argument parsing and help system
- **FastAPI Web Server**: RESTful API server for integrating DeepSeek into other applications
- **File Upload Support**: Upload and analyze documents, images, and other files
- **Conversation History**: Save and load previous chat sessions
- **Multiple Model Support**: Access different DeepSeek model variants
- **Batch Processing**: Process multiple prompts in sequence
- **Configuration Management**: Advanced settings and preferences system

## Demo








https://github.com/user-attachments/assets/80a8038a-cdec-4c2c-822e-25dc70c8047f

## Installation

1. Clone the repository:
```bash
git clone https://github.com/aryaniiil/deepseek-reverse-api.git
cd deepseek-reverse-api
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your credentials:
   - Copy your DeepSeek email and password to `data/.env`:
```env
DEEPSEEK_EMAIL=your_email@example.com
DEEPSEEK_PASSWORD=your_password
```

## How to Use

### Interactive Mode
Start an interactive chat session:
```bash
python main.py
```

Available commands during chat:
- `/think` - Toggle deep thinking mode on/off
- `/search` - Toggle web search on/off  
- `/exit`, `/quit`, `/q` - Exit the program

### Single Prompt Mode
Execute a single query and exit:
```bash
python main.py "What is the capital of France?"
```

### Advanced Usage Examples

**Enable deep thinking for complex problems:**
```bash
python main.py
> /think
> Explain quantum computing in simple terms
```

**Use web search for current information:**
```bash
python main.py
> /search
> What are the latest developments in AI this week?
```

**Combine features:**
```bash
python main.py
> /think
> /search
> Analyze the current state of renewable energy technology
```

## Project Structure

```
reverse/
├── data/                    # Data storage directory
│   ├── .env                # Environment variables (credentials)
│   ├── auth_token.txt      # Stored authentication token
│   ├── deepseek_cookies.json # Browser cookies
│   ├── last_login.txt      # Last login timestamp
│   └── sha3_wasm_bg.wasm   # WebAssembly module for PoW solving
├── src/                    # Source code
│   ├── __init__.py
│   ├── auth.py            # Authentication and credential extraction
│   ├── client.py          # Main DeepSeek API client
│   ├── config.py          # Configuration management
│   └── display.py         # Terminal UI and formatting
├── main.py                # Entry point
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Technical Details

### Authentication Flow
1. Checks for existing valid session
2. If expired, launches headless browser
3. Automatically fills login form
4. Extracts cookies and auth token
5. Stores credentials for future use

### Proof of Work System
DeepSeek uses a WebAssembly-based proof of work system to prevent abuse. This client:
- Automatically requests PoW challenges
- Solves them using the included WASM module
- Includes solutions in API requests

### Session Management
- Sessions expire after 1 hour
- Automatic re-authentication when needed
- Conversation context maintained within sessions
- Graceful handling of network interruptions

## Video Guides

### Getting Started
- **Setup and Installation** - Step-by-step guide to get the client running
- **Basic Usage Tutorial** - Learn interactive and single prompt modes
- **Authentication Troubleshooting** - Fix common login issues

### Advanced Features
- **Deep Thinking Mode** - When and how to use advanced reasoning
- **Web Search Integration** - Leveraging real-time information
- **Session Management** - Understanding conversation persistence

### Development
- **Code Architecture Overview** - Understanding the codebase structure
- **Adding New Features** - Contributing to the project
- **Debugging Common Issues** - Troubleshooting guide for developers

*Note: Video guides will be added as the project develops and reaches stable milestones.*

## Requirements

- Python 3.8+
- Valid DeepSeek account
- Chrome/Chromium browser (for authentication)
- Internet connection

## Dependencies

- `rich` - Terminal formatting and colors
- `nodriver` - Headless browser automation
- `python-dotenv` - Environment variable management
- `requests` - HTTP client for API calls
- `wasmtime` - WebAssembly runtime for PoW solving

## Troubleshooting

### Common Issues

**Login Failed**
- Verify credentials in `data/.env`
- Check internet connection
- Ensure DeepSeek account is active

**Session Expired**
- Delete `data/last_login.txt` to force re-authentication
- Check if DeepSeek changed their login process

**PoW Challenge Failed**
- Ensure `data/sha3_wasm_bg.wasm` file exists
- Try restarting the client

**Browser Issues**
- Install/update Chrome or Chromium
- Check if browser automation is blocked by antivirus

## Security Notes

- Credentials are stored locally in plain text
- Use environment variables for production deployments
- This tool is for educational and research purposes
- Respect DeepSeek's terms of service

## Contributing

Contributions are welcome! Focus areas:
- CLI improvements and user experience
- FastAPI integration for web services
- File upload functionality
- Bug fixes and performance optimizations

## License

This project is for educational and research purposes. Please respect DeepSeek's terms of service and use responsibly.

## Disclaimer

This is a reverse-engineered client and is not officially supported by DeepSeek. Use at your own risk. The authors are not responsible for any issues that may arise from using this software.
