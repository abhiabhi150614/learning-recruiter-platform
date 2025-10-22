from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, onboarding, youtube_schedule, chatbot, call_bot, voice_webhook, recruiter
from app.routes import learning_plan, subplans
from app.routes import quiz
from app.database.db import create_tables, engine, Base
from sqlalchemy import text

app = FastAPI(title="EduAI Learning Platform", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, tags=["Auth"])
app.include_router(onboarding.router, tags=["Onboarding"])
app.include_router(youtube_schedule.router, tags=["YouTubeSchedule"])
app.include_router(chatbot.router, tags=["Chatbot"])
app.include_router(call_bot.router, prefix="/call", tags=["CallBot"])
app.include_router(voice_webhook.router, tags=["VoiceWebhook"])
app.include_router(learning_plan.router, tags=["LearningPlan"])
app.include_router(subplans.router, tags=["Subplans"])
app.include_router(quiz.router, tags=["Quiz"])
app.include_router(recruiter.router, tags=["Recruiter"])

@app.on_event("startup")
async def startup_event():
    """Fresh database setup: drop and recreate all tables on startup"""
    try:
        print("🔄 Fresh database setup - dropping and recreating all tables...")
        
        # Import all models to ensure they're registered
        from app.models import user, onboarding, learning_plan, job, email_application, candidate_vector, quiz, shortlist
        
        # Drop all tables and recreate them fresh
        print("🗑️ Dropping all existing tables...")
        Base.metadata.drop_all(bind=engine)
        print("✅ All tables dropped")
        
        print("🔨 Creating all tables fresh...")
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created fresh")
        
    except Exception as e:
        print(f"❌ Error during table creation: {e}")



@app.get("/")
def read_root():
    return {"message": "EduAI Learning Platform API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

