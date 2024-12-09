# Deepgram Agent

A voice assistant powered by Deepgram's speech services and Groq's LLM.

## Features
- Real-time speech-to-text using Deepgram
- Natural language responses using Groq LLM
- Text-to-speech synthesis using Deepgram
- Voice interrupt capability

## Prerequisites
- Python 3.8 or higher
- Deepgram API key
- Groq API key

## Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/deepgram-agent.git
cd deepgram-agent
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Set up environment variables
```bash
cp .env.example .env
```
Edit `.env` and add your API keys:
```
DEEPGRAM_API_KEY=your_deepgram_api_key
GROQ_API_KEY=your_groq_api_key
```

## Usage

Run the voice assistant:
```bash
python src/main.py
```

- Speak into your microphone to interact
- Press Enter to exit
- You can interrupt the assistant's response by speaking

## Troubleshooting

If you encounter audio device issues:
1. Check your default microphone settings
2. Ensure you have proper permissions
3. Try running with sudo if on Linux

For API errors:
1. Verify your API keys in `.env`
2. Check your internet connection
3. Ensure you have remaining API credits

## License

MIT

## Acknowledgments
- [Deepgram](https://deepgram.com/) for speech-to-text and text-to-speech
- [Groq](https://groq.com/) for LLM backend
