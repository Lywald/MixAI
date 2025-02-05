# MixAI - Multi-Model AI Chat Application

MixAI is a desktop application that enables simultaneous interaction with multiple AI models (Claude, GPT-4, and Gemini) in a unified chat interface. It allows users to communicate with all models at once or target specific AI assistants for specialized responses.

![image](https://github.com/user-attachments/assets/f20b1f1a-0023-4a18-84ed-8c7fba9e0fe6)


![image](https://github.com/user-attachments/assets/08454301-df0a-4fab-b159-e152cfcaf959)


## Features

- **Multi-Model Integration**: Seamlessly interact with Claude (Anthropic), GPT-4 (OpenAI), and Gemini (Google) in a single interface
- **Targeted Interactions**: Use @all, @claude, @gpt, or @gemini to direct questions to specific AI models
- **Concurrent Processing**: Asynchronous message processing for smooth user experience
- **Conversation History**: Full context preservation across all AI models
- **Clean Qt-based GUI**: Modern, responsive desktop interface

## Prerequisites

- Python 3.8 or higher
- PyQt5
- Active API keys for:
  - Anthropic (Claude)
  - OpenAI (GPT-4)
  - Google AI (Gemini)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/mixai.git
cd mixai
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install required packages:
```bash
pip install anthropic openai google-generativeai PyQt5
```

## Configuration

Before running the application, make sure to set up your API keys in the lines 33/34/35 of `mixai.py` file:

```python
self.claude = anthropic.Anthropic(api_key="your-anthropic-api-key")
self.gpt = OpenAI(api_key="your-openai-api-key")
genai.configure(api_key="your-google-api-key")
```

## Usage

1. Start the application:
```bash
python mixai.py
```

2. The chat interface will open automatically.

3. To use the chat:
   - Type a message and press Enter or click Send to get responses from all AIs
   - Use @all, @claude, @gpt, or @gemini followed by your message to target a specific AI
   - Previous conversation context is maintained for all AIs

Example commands:
```
Hello, can you all introduce yourselves?
@claude What do you think about poetry?
@gpt Can you analyze this code snippet?
@gemini Please explain this scientific concept.
```

## Architecture

The application is built with three main components:

1. **MixAI Class**: Core logic for AI model integration and message processing
2. **AIWorker**: Threaded worker for asynchronous message processing
3. **MixAIGUI**: Qt-based graphical user interface

### Key Features Implementation

- **Conversation History**: Maintains context across all AI models
- **Asynchronous Processing**: Prevents UI freezing during API calls
- **Error Handling**: Robust error catching and user feedback
- **Model Targeting**: Flexible message routing system


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Anthropic for Claude API
- OpenAI for GPT-4 API
- Google for Gemini API
- Qt team for PyQt5

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.

## Disclaimer

This project is not officially affiliated with Anthropic, OpenAI, or Google. Please ensure you comply with each AI provider's terms of service and API usage guidelines.
