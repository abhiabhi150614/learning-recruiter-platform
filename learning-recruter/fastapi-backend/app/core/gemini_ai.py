import google.generativeai as genai
from app.core.config import settings
import uuid
from datetime import datetime
from typing import Dict, List, Optional
import json
from composio import Composio
import os

# Configure Gemini AI
genai.configure(api_key=settings.GEMINI_API_KEY)

# Initialize Composio for real-time responses
COMPOSIO_API_KEY = os.getenv("COMPOSIO_API_KEY", "ak_nsf-0GU62pD5RCWVXyRN")
composio = Composio(api_key=COMPOSIO_API_KEY)

class GeminiChatbot:
    def __init__(self):
        # Try different model options in order of preference
        self.model_options = [
            'gemini-2.0-flash-exp',  # Latest Gemini 2.0
            'gemini-2.5-flash',      # Gemini 1.5 Flash
            'gemini-1.5-pro',        # Gemini 1.5 Pro
            'gemini-pro'             # Fallback
        ]
        
        self.model = self._initialize_model()
        self.chat_sessions: Dict[str, genai.ChatSession] = {}
    
    def _initialize_model(self):
        """Initialize the model by trying different options"""
        for model_name in self.model_options:
            try:
                print(f"🔄 Trying model: {model_name}")
                model = genai.GenerativeModel(model_name)
                # Test the model with a simple request
                response = model.generate_content("Hello")
                print(f"✅ Successfully initialized model: {model_name}")
                return model
            except Exception as e:
                print(f"❌ Failed to initialize {model_name}: {str(e)}")
                continue
        
        # If all models fail, raise an error
        raise Exception("Failed to initialize any Gemini model. Please check your API key and model availability.")
        
    def get_or_create_session(self, user_id: int) -> genai.ChatSession:
        """Get existing chat session or create new one for user"""
        session_key = f"user_{user_id}"
        
        if session_key not in self.chat_sessions:
            # Create new chat session
            self.chat_sessions[session_key] = self.model.start_chat(history=[])
            
            # Send initial context message with formatting instructions
            context_message = """
            You are EduAI, an intelligent learning assistant for the EduAI learning platform. 
            
            CRITICAL FORMATTING RULES - FOLLOW THESE EXACTLY:
            
            **TEXT FORMATTING:**
            - Use **bold** for important concepts, headings, and key terms
            - Use *italic* for emphasis and definitions
            - Use `inline code` for code snippets, variables, and technical terms
            - Use bullet points (•) for lists and key points
            - Use numbered lists (1., 2., 3.) for step-by-step instructions
            - Break up long responses into clear paragraphs
            
            **CODE BLOCKS:**
            - Always use proper code blocks with language specification
            - Format: ```language\ncode\n```
            - Examples: ```python\nprint("Hello")\n``` or ```javascript\nconsole.log("Hello")\n```
            - Include comments in code to explain what it does
            - Keep code examples simple and educational
            
            **STRUCTURE:**
            - Start with a clear introduction
            - Use headings with **bold** formatting
            - Provide practical examples with code blocks
            - End with a summary or next steps
            - Keep responses comprehensive but well-organized (3-5 paragraphs max)
            
            **YOUR ROLE:**
            You help students with:
            • Learning strategies and study tips
            • Understanding complex topics (especially programming)
            • Creating study schedules
            • Motivation and productivity advice
            • Academic guidance and career advice
            • Tracking their learning progress
            • Accessing their notes stored in Google Drive
            • Creating and posting content on LinkedIn
            • Managing social media connections
            
            **AVAILABLE TOOLS - USE IMMEDIATELY:**
            • get_drive_notes: Get notes (when user asks about notes)
            • update_drive_notes: Add to notes (when user wants to save something)
            • search_youtube_videos: Find videos (when user asks for videos)
            • create_youtube_playlist: New playlist (when user wants playlist)
            • add_video_to_playlist: Add video (when user wants to add)
            • initiate_call: Phone call (when user asks to call)
            • create_linkedin_post: Create LinkedIn posts (when user wants to post on LinkedIn)
            
            **TOOL USAGE:**
            - Use tools IMMEDIATELY when users request related actions
            - Be FAST in tool selection - don't overthink
            - Always use tools instead of just describing what you would do
            - Provide clear feedback about tool results
            
            **SPECIAL FEATURES:**
            • Use get_drive_notes tool when users ask about their notes
            • Use update_drive_notes tool when users want to add content to notes
            • Use search_youtube_videos tool when users want to find videos
            • Use create_youtube_playlist tool when users want new playlists
            • Use add_video_to_playlist tool when users want to add videos
            • Use initiate_call tool when users want phone calls
            • Use create_linkedin_post tool when users want to post on LinkedIn
            • Always use tools instead of just providing information
            • Combine tools for complex requests (e.g., search videos then add to playlist)
            • When users ask to create LinkedIn posts, generate professional content about their learning topics
            
            **BEHAVIOR:**
            - Be friendly, encouraging, and educational
            - Provide specific, actionable advice
            - Use a warm, supportive tone
            - Format responses for easy reading on mobile devices
            - ALWAYS use clean markdown links: [text](url)
            - Never mix HTML with markdown
            - Keep link text concise and clear
            - When providing links, use format: [Access your playlist](url)
            - For notes: [View your notes](url)
            - For videos: [Watch video](url)
            - Separate links from other text with line breaks
            - When YouTube operations succeed, provide clean success message with proper link
            - When operations fail, provide clear error messages
            - Adapt responses based on user's learning progress
            
            **LINK FORMAT EXAMPLES:**
            ✅ CORRECT: Great! Your playlist 'Learning' has been created.
            
            [Access your playlist](https://youtube.com/playlist?list=123)
            
            ❌ WRONG: Never mix HTML attributes with markdown
            
            **RESPONSE STRUCTURE:**
            1. Clear success/status message
            2. Blank line
            3. Clean markdown link on separate line
            4. Blank line
            5. Next steps or additional info
            """
            
            # Send the context as the first message
            try:
                self.chat_sessions[session_key].send_message(context_message)
            except Exception as e:
                print(f"Error sending context message: {str(e)}")
        
        return self.chat_sessions[session_key]
    
    def _format_response(self, response_text: str) -> str:
        """Format the response for better readability and fix markdown links"""
        import re
        
        # Clean up any extra whitespace
        response_text = response_text.strip()
        
        # Fix malformed HTML/markdown links
        # Remove any stray HTML attributes that got mixed with markdown
        response_text = re.sub(r'" target="_blank" rel="noopener noreferrer" style="[^"]*">', '', response_text)
        
        # Ensure proper markdown link format [text](url)
        response_text = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)([^\[]*?)\[', r'[\1](\2)\n\n[', response_text)
        
        # Clean up any duplicate or malformed link text
        response_text = re.sub(r'(https://[^\s]+)"[^"]*"[^"]*"[^"]*>', r'\1', response_text)
        
        # Ensure proper paragraph spacing
        paragraphs = response_text.split('\n\n')
        formatted_paragraphs = []
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if paragraph:
                # Clean up any remaining HTML artifacts
                paragraph = re.sub(r'<[^>]+>', '', paragraph)
                
                # Ensure bullet points are properly formatted
                if paragraph.startswith('•') or paragraph.startswith('-'):
                    formatted_paragraphs.append(paragraph)
                elif paragraph.startswith(('1.', '2.', '3.', '4.', '5.')):
                    formatted_paragraphs.append(paragraph)
                else:
                    formatted_paragraphs.append(paragraph)
        
        return '\n\n'.join(formatted_paragraphs)
    
    async def get_response(self, message: str, user_id: int, tools=None, db=None) -> Dict:
        """Get response from Gemini AI with function calling support"""
        try:
            if not settings.GEMINI_API_KEY:
                return {
                    "response": "I'm sorry, but the AI assistant is not configured. Please contact support.",
                    "timestamp": datetime.now().isoformat(),
                    "message_id": str(uuid.uuid4())
                }
            
            # Get or create chat session
            chat_session = self.get_or_create_session(user_id)
            
            # If tools are provided, use function calling
            if tools and db:
                from app.core.chatbot_tools import ChatbotTools
                chatbot_tools = ChatbotTools(db, user_id)
                
                # Create function declarations for Gemini
                function_declarations = chatbot_tools.get_tools_schema()
                
                # Generate response with function calling - optimized for speed
                response = chat_session.send_message(
                    message,
                    tools=[{"function_declarations": function_declarations}],
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.1,
                        max_output_tokens=500
                    )
                )
                
                # Check if AI wants to call functions
                if response.candidates[0].content.parts:
                    final_response = ""
                    
                    for part in response.candidates[0].content.parts:
                        if hasattr(part, 'function_call') and part.function_call:
                            # Execute the function call
                            function_name = part.function_call.name
                            function_args = dict(part.function_call.args)
                            
                            print(f"🔧 AI calling tool: {function_name} with args: {function_args}")
                            
                            # Execute the tool
                            tool_result = chatbot_tools.execute_tool(function_name, function_args)
                            
                            # Send function result back to AI
                            function_response = chat_session.send_message(
                                genai.protos.Content(
                                    parts=[genai.protos.Part(
                                        function_response=genai.protos.FunctionResponse(
                                            name=function_name,
                                            response={"result": tool_result}
                                        )
                                    )]
                                )
                            )
                            
                            final_response = function_response.text
                        elif part.text:
                            final_response += part.text
                    
                    formatted_response = self._format_response(final_response)
                else:
                    formatted_response = self._format_response(response.text)
            else:
                # Regular response without function calling
                response = chat_session.send_message(message)
                formatted_response = self._format_response(response.text)
            
            return {
                "response": formatted_response,
                "timestamp": datetime.now().isoformat(),
                "message_id": str(uuid.uuid4())
            }
            
        except Exception as e:
            print(f"Gemini AI Error: {str(e)}")
            # For safety filter errors, still return success since backend operations work
            if "finish_reason: 12" in str(e):
                return {
                    "response": "I've processed your request! The operation should complete successfully.",
                    "timestamp": datetime.now().isoformat(),
                    "message_id": str(uuid.uuid4())
                }
            return {
                "response": "I'm sorry, I'm having trouble processing your request right now. Please try again later.",
                "timestamp": datetime.now().isoformat(),
                "message_id": str(uuid.uuid4())
            }
    
    def clear_session(self, user_id: int) -> bool:
        """Clear chat session for user"""
        session_key = f"user_{user_id}"
        if session_key in self.chat_sessions:
            del self.chat_sessions[session_key]
            return True
        return False
    
    def get_composio_response(self, message: str, user_email: str, tools=None, db=None) -> Dict:
        """Get response using Composio for real-time Gemini AI responses"""
        try:
            if not user_email:
                return {
                    "response": "I'm sorry, but user email is required for Composio integration.",
                    "timestamp": datetime.now().isoformat(),
                    "message_id": str(uuid.uuid4())
                }
            
            # Generate unique user ID for Composio
            user_id = user_email.replace('@', '_').replace('.', '_')
            
            # Use Composio to get Gemini response
            result = composio.tools.execute(
                "GOOGLE_GEMINI_GENERATE_CONTENT",
                user_id=user_id,
                arguments={
                    "prompt": message,
                    "model": "gemini-pro",
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
            )
            
            if result.get('successful'):
                content_data = result.get('data', {})
                response_text = content_data.get('text', '')
                
                # If tools are provided, check if we need to execute them
                if tools and db:
                    # Check if the response indicates tool usage
                    if any(keyword in response_text.lower() for keyword in ['search', 'create', 'add', 'send', 'post', 'call']):
                        # Execute tools through Composio
                        tool_result = self._execute_composio_tools(user_id, message, tools, db)
                        if tool_result:
                            response_text += f"\n\n{tool_result}"
                
                return {
                    "response": response_text,
                    "timestamp": datetime.now().isoformat(),
                    "message_id": str(uuid.uuid4()),
                    "composio_used": True
                }
            else:
                # Fallback to regular Gemini if Composio fails
                return self.get_response(message, 0, tools, db)
                
        except Exception as e:
            print(f"Composio Gemini Error: {str(e)}")
            # Fallback to regular Gemini
            return self.get_response(message, 0, tools, db)
    
    def _execute_composio_tools(self, user_id: str, message: str, tools, db) -> str:
        """Execute tools through Composio"""
        try:
            # Check for YouTube operations
            if 'youtube' in message.lower() or 'video' in message.lower():
                if 'search' in message.lower():
                    # Extract search query
                    query = message.replace('search', '').replace('youtube', '').replace('video', '').strip()
                    result = composio.tools.execute(
                        "YOUTUBE_SEARCH",
                        user_id=user_id,
                        arguments={
                            "query": query,
                            "max_results": 5
                        }
                    )
                    if result.get('successful'):
                        return f"Found YouTube videos for '{query}'"
            
            # Check for Gmail operations
            if 'email' in message.lower() or 'send' in message.lower():
                result = composio.tools.execute(
                    "GMAIL_SEND_EMAIL",
                    user_id=user_id,
                    arguments={
                        "to": "example@email.com",
                        "subject": "AI Generated Email",
                        "body": "This is an AI-generated email from EduAI"
                    }
                )
                if result.get('successful'):
                    return "Email sent successfully through Gmail"
            
            # Check for Calendar operations
            if 'calendar' in message.lower() or 'event' in message.lower():
                result = composio.tools.execute(
                    "GOOGLE_CALENDAR_CREATE_EVENT",
                    user_id=user_id,
                    arguments={
                        "summary": "AI Generated Event",
                        "start_time": datetime.now().isoformat(),
                        "end_time": (datetime.now() + timedelta(hours=1)).isoformat()
                    }
                )
                if result.get('successful'):
                    return "Calendar event created successfully"
            
            return ""
            
        except Exception as e:
            print(f"Composio tools execution error: {str(e)}")
            return ""

# Global chatbot instance
chatbot = GeminiChatbot()
