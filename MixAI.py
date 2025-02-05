import sys
import anthropic
import google.generativeai as genai
from openai import OpenAI
import os
from typing import List, Dict
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class AIWorker(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, mix_ai, user_input):
        super().__init__()
        self.mix_ai = mix_ai
        self.user_input = user_input

    def run(self):
        try:
            result = self.mix_ai.process_message(self.user_input)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class MixAI:
    def __init__(self):
        """Initialize the MixAI class with hardcoded API keys."""
        self.conversation_history = []
        # Initialize with your API keys
        self.claude = anthropic.Anthropic(api_key="ADD YOUR KEY HERE")  # Get from: https://console.anthropic.com/
        self.gpt = OpenAI(api_key="ADD YOUR KEY HERE")  # Get from: https://platform.openai.com/api-keys
        genai.configure(api_key="ADD YOUR KEY HHERE")  # Get from: https://makersuite.google.com/app/apikey
        self.gemini = genai

    def process_message(self, user_input: str) -> Dict:
        """Process a user message through all AI models in sequence."""
        # Determine target based on prefix
        target = "all"  # default
        if user_input.startswith("@"):
            parts = user_input.split(" ", 1)
            if len(parts) > 1:
                target = parts[0].lower()
                user_input = parts[1]  # Remove the prefix from the message

        conversation_entry = {'user_input': user_input, 'target': target}
        
        try:
            # Build conversation history for context
            context = ""
            for entry in self.conversation_history[-3:]:  # Get last 3 entries
                context += f"User: {entry['user_input']}\n"
                if entry.get('claude_response'):
                    context += f"Claude: {entry['claude_response']}\n"
                if entry.get('gpt_response'):
                    context += f"GPT: {entry['gpt_response']}\n"
                if entry.get('gemini_response'):
                    context += f"Gemini: {entry['gemini_response']}\n"

            # 1. Get Claude's response (if targeted or @all)
            if target in ["@claude", "@all"]:
                claude_prompt = f"""Previous conversation:
{context}
Current message: {user_input}

Please provide your response to this conversation:"""
                
                claude_message = self.claude.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1024,
                    system="You are Claude, participating in a conversation with two other AI assistants (GPT and Gemini) and a human user. Provide direct, natural responses without any XML or formatting tags.",
                    messages=[
                        {"role": "user", "content": claude_prompt}
                    ]
                )
                # Extract just the text content from Claude's response
                if hasattr(claude_message.content, 'replace'):
                    claude_response = claude_message.content
                elif isinstance(claude_message.content, list):
                    claude_response = claude_message.content[0].text if claude_message.content else ""
                else:
                    claude_response = str(claude_message.content)
                conversation_entry['claude_response'] = claude_response
            else:
                conversation_entry['claude_response'] = "[No response required.]"

            # 2. Get GPT's response (if targeted or @all)
            if target in ["@gpt", "@all"]:
                # Include the last few conversation entries for context
                context = ""
                for entry in self.conversation_history[-3:]:  # Get last 3 entries
                    context += f"User: {entry['user_input']}\n"
                    if entry.get('claude_response'):
                        context += f"Claude: {entry['claude_response']}\n"
                    if entry.get('gpt_response'):
                        context += f"GPT: {entry['gpt_response']}\n"
                    if entry.get('gemini_response'):
                        context += f"Gemini: {entry['gemini_response']}\n"
                
                gpt_prompt = f"""Previous conversation:
{context}
Current message:
User: {user_input}
Claude: {conversation_entry.get('claude_response', '')}

You are GPT-4. Remember to respond as yourself, not as Claude or Gemini. Please provide your response to this conversation:"""
                
                gpt_completion = self.gpt.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are GPT-4. Never impersonate Claude or Gemini. Always maintain your own identity when responding. You are participating in a conversation with two other AI assistants (Claude and Gemini) and a human user."},
                        {"role": "user", "content": gpt_prompt}
                    ]
                )
                conversation_entry['gpt_response'] = gpt_completion.choices[0].message.content
            else:
                conversation_entry['gpt_response'] = "[No response required.]"

            # 3. Get Gemini's response (if targeted or @all)
            if target in ["@gemini", "@all"]:
                system_prompt = """You are Gemini, participating in a conversation with two other AI assistants (Claude and GPT) and a human user."""
                
                gemini_prompt = f"""Previous conversation:
{context}
Current message:
User: {user_input}
Claude: {conversation_entry.get('claude_response', '')}
GPT: {conversation_entry.get('gpt_response', '')}

Please provide your response to this conversation:"""
                
                full_prompt = system_prompt + "\n\n" + gemini_prompt
                
                model = self.gemini.GenerativeModel('gemini-pro')
                gemini_response = model.generate_content(full_prompt)
                conversation_entry['gemini_response'] = gemini_response.text
            else:
                conversation_entry['gemini_response'] = "[No response required.]"

            self.conversation_history.append(conversation_entry)
            return conversation_entry

        except Exception as e:
            raise Exception(f"Error processing message: {str(e)}")

class MixAIGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.mix_ai = MixAI()  # Initialize with hardcoded keys
        self.worker = None  # Initialize worker as None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('MixAI - Multi-Model AI Chat')
        self.setGeometry(100, 100, 800, 600)

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: white;
                font-family: monospace;
                font-size: 10pt;
            }
        """)
        layout.addWidget(self.chat_display)

        # User input
        input_layout = QHBoxLayout()
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Type your message here... (Use @claude, @gpt, or @gemini to target specific AI)")
        self.user_input.returnPressed.connect(self.send_message)
        self.send_button = QPushButton('Send')
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.user_input)
        input_layout.addWidget(self.send_button)
        layout.addLayout(input_layout)

        # Status bar
        self.statusBar().showMessage('Ready to chat!')

    def send_message(self):
        if self.worker is not None and self.worker.isRunning():
            return  # Prevent multiple simultaneous requests
            
        user_input = self.user_input.text()
        if not user_input:
            return

        # Add user message in black with proper formatting
        html_content = self.chat_display.toHtml()
        html_content += f'<br><div style="color: black; white-space: pre-wrap;">You: {user_input}</div><br>'
        self.chat_display.setHtml(html_content)
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )  # Scroll to bottom
        
        self.user_input.clear()
        self.statusBar().showMessage('Processing message...')
        self.send_button.setEnabled(False)
        self.user_input.setEnabled(False)  # Disable input while processing

        # Create and start worker thread
        self.worker = AIWorker(self.mix_ai, user_input)
        self.worker.finished.connect(self.handle_response)
        self.worker.error.connect(self.handle_error)
        self.worker.start()

    def handle_response(self, response):
        try:
            def format_message(text):
                text = text.replace('\n', '<br>')
                text = text.replace(' ', '&nbsp;')
                text = text.replace('&nbsp;&nbsp;&nbsp;', '   ')  # Fix triple spaces
                return text

            # Add responses with colors and proper formatting
            html_content = self.chat_display.toHtml()
            html_content += f'<div style="color: #2E8B57; white-space: pre-wrap;">{format_message(response["claude_response"])}</div><br>'
            html_content += f'<div style="color: #FF4500; white-space: pre-wrap;">{format_message(response["gpt_response"])}</div><br>'
            html_content += f'<div style="color: #4169E1; white-space: pre-wrap;">{format_message(response["gemini_response"])}</div><br>'
            
            self.chat_display.setHtml(html_content)
            self.chat_display.verticalScrollBar().setValue(
                self.chat_display.verticalScrollBar().maximum()
            )  # Scroll to bottom
        except Exception as e:
            print(f"Error in handle_response: {str(e)}")
        finally:
            self.statusBar().showMessage('Ready')
            self.send_button.setEnabled(True)
            self.user_input.setEnabled(True)
            self.worker = None  # Clear the worker reference

    def handle_error(self, error_message):
        try:
            html_content = self.chat_display.toHtml()
            html_content += f'<br><div style="color: #FF0000; white-space: pre-wrap;">Error: {error_message}</div><br>'
            self.chat_display.setHtml(html_content)
            self.chat_display.verticalScrollBar().setValue(
                self.chat_display.verticalScrollBar().maximum()
            )  # Scroll to bottom
        except Exception as e:
            print(f"Error in handle_error: {str(e)}")
        finally:
            self.statusBar().showMessage('Error occurred')
            self.send_button.setEnabled(True)
            self.user_input.setEnabled(True)
            self.worker = None  # Clear the worker reference

def main():
    app = QApplication(sys.argv)
    ex = MixAIGUI()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
