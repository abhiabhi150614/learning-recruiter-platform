from fastapi import APIRouter, Request, Query
from fastapi.responses import Response
import urllib.parse
import xml.sax.saxutils as xml_escape
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

router = APIRouter()

@router.post("/voice")
@router.get("/voice")
async def voice_webhook(request: Request, context: str = Query("")):
    """Twilio voice webhook handler - matches your existing setup"""
    
    # Decode the context
    decoded_context = urllib.parse.unquote(context) if context else "Hello! This is your AI learning assistant."
    
    # Create TwiML response with your context
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">{decoded_context}</Say>
    <Gather input="speech" action="/voice/process" method="POST" speechTimeout="3">
        <Say voice="alice">How can I help you with your learning today?</Say>
    </Gather>
    <Say voice="alice">I didn't hear anything. Have a great day with your studies!</Say>
</Response>"""
    
    return Response(content=twiml, media_type="application/xml")

@router.post("/voice/process")
async def process_speech(request: Request, context: str = Query("")):
    """Process speech input with AI response"""
    try:
        form_data = await request.form()
        speech_result = form_data.get("SpeechResult", "")
        decoded_context = urllib.parse.unquote(context) if context else ""
        
        if speech_result:
            ai_prompt = f"""
            CONTEXT: {decoded_context}
            
            USER SPEECH: "{speech_result}"
            
            INSTRUCTIONS:
            - You are Abhishek's personal AI learning assistant
            - Reference his specific learning plan, current topic, goals, and skills
            - If asked what to study, mention today's specific topic and objectives
            - Connect today's learning to his career goals
            - Be encouraging but give actionable study advice
            - For voice: Keep under 30 words but be specific and helpful
            - Always reference his actual learning context, not generic advice
            
            RESPOND WITH SPECIFIC STUDY GUIDANCE:
            """
            
            try:
                ai_response = model.generate_content(ai_prompt)
                response_text = ai_response.text.strip()
            except:
                response_text = "I understand. Keep up the great work with your learning!"
        else:
            response_text = "I didn't catch that. Could you repeat your question?"
        
        safe_response = xml_escape.escape(response_text[:200])
        
        twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">{safe_response}</Say>
    <Gather input="speech" action="/voice/process?context={urllib.parse.quote(decoded_context)}" method="POST" speechTimeout="3">
        <Say voice="alice">Anything else I can help with?</Say>
    </Gather>
    <Say voice="alice">Have a productive learning session!</Say>
</Response>'''
        
        return Response(content=twiml, media_type="application/xml")
        
    except Exception as e:
        fallback_twiml = '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">Thank you for calling. Have a great day!</Say>
</Response>'''
        return Response(content=fallback_twiml, media_type="application/xml")