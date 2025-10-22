# 🎓 EduAI - AI-Powered Learning & Recruitment Platform

<div align="center">

![EduAI Platform](https://img.shields.io/badge/EduAI-Learning%20Platform-blue?style=for-the-badge&logo=graduation-cap)
![Hackathon Winner](https://img.shields.io/badge/6%20Day-Hackathon%20Sprint-gold?style=for-the-badge&logo=trophy)
![AI Powered](https://img.shields.io/badge/AI-Powered-green?style=for-the-badge&logo=robot)

**🚀 Dual-user platform combining AI education with intelligent recruitment**

</div>

---

## 📈 Platform Overview

```mermaid
graph TB
    A[EduAI Platform] --> B[👨🎓 Student Portal]
    A --> C[🏢 Recruiter Portal]
    
    B --> D[AI Learning Plans]
    B --> E[Interactive Chatbot]
    B --> F[Quiz System]
    B --> G[Voice Tutoring]
    B --> H[Social Integration]
    
    C --> I[Candidate Matching]
    C --> J[Email Analysis]
    C --> K[Interview Management]
    C --> L[AI Assistant]
    
    D --> M[📊 Progress Analytics]
    E --> N[🤖 Gemini AI]
    F --> O[📧 Gmail Notifications]
    G --> P[📞 Twilio Voice]
    H --> Q[🔗 LinkedIn/GitHub/Twitter]
    
    I --> R[🎯 AI Scoring]
    J --> S[📄 Resume Parsing]
    K --> T[📅 Google Meet]
    L --> U[💬 Recruitment Insights]
```

### 🏆 Key Achievements

<table>
<tr>
<td align="center"><strong>🔐 Hybrid OAuth</strong><br/>Google + Composio<br/>Individual Services</td>
<td align="center"><strong>🤖 AI Function Calling</strong><br/>8+ Tool<br/>Integration</td>
<td align="center"><strong>📱 45+ Components</strong><br/>Comprehensive<br/>UI Library</td>
<td align="center"><strong>🗄️ 15+ Models</strong><br/>Complex Database<br/>Architecture</td>
</tr>
<tr>
<td align="center"><strong>🔌 10+ APIs</strong><br/>Multi-Service<br/>Integration</td>
<td align="center"><strong>📞 Voice AI</strong><br/>Twilio-Powered<br/>Tutoring</td>
<td align="center"><strong>⚡ 6-Day Sprint</strong><br/>Rapid Development<br/>Cycle</td>
<td align="center"><strong>🎯 Dual Architecture</strong><br/>Student + Recruiter<br/>Platforms</td>
</tr>
</table>

---

## 🎯 Core Features

### 👨🎓 Student Features

<details>
<summary><strong>🧠 AI-Powered Learning Plans</strong></summary>

```mermaid
flowchart LR
    A[User Goals] --> B[AI Analysis]
    B --> C[Custom Curriculum]
    C --> D[Monthly Structure]
    D --> E[Daily Content]
    E --> F[Progress Tracking]
    
    G[Skills Assessment] --> B
    H[Time Availability] --> B
    I[Learning Style] --> B
```

**Features:**
- 🎯 **Personalized Paths**: AI-generated curricula based on goals, skills, and availability
- 📅 **Monthly Structure**: Organized 30-day learning cycles with clear milestones
- 📊 **Real-time Analytics**: Progress monitoring with detailed performance insights
- 🔄 **Adaptive Content**: Dynamic content generation based on learning progress

</details>

<details>
<summary><strong>🤖 Interactive AI Chatbot with Function Calling</strong></summary>

```mermaid
graph TD
    A[Student Query] --> B[Context Analysis]
    B --> C{Query Type}
    
    C -->|Learning Help| D[Access Current Progress]
    C -->|Notes Request| E[Google Drive Integration]
    C -->|Video Search| F[YouTube API]
    C -->|Voice Call| G[Twilio Integration]
    C -->|LinkedIn Post| H[Composio LinkedIn]
    
    D --> I[Personalized Response]
    E --> I
    F --> I
    G --> J[Voice Session]
    H --> I
```

**Capabilities:**
- 🧠 **Context Awareness**: Knows current learning position and progress
- 🛠️ **8+ Tool Integration**: Google Drive, YouTube, Twilio, LinkedIn, GitHub, Twitter
- ⚡ **Real-time Responses**: Powered by Gemini AI with function calling
- 📚 **Learning Support**: Specific guidance based on current topics
- 🔗 **Social Actions**: Create LinkedIn posts, manage GitHub repos

</details>

<details>
<summary><strong>📝 Comprehensive Quiz System</strong></summary>

```mermaid
sequenceDiagram
    participant S as Student
    participant AI as Gemini AI
    participant Q as Quiz System
    participant E as Email Service
    
    S->>AI: Complete Daily Learning
    AI->>Q: Generate Adaptive Quiz
    Q->>S: Present Questions
    S->>Q: Submit Answers
    Q->>AI: Analyze Performance
    AI->>E: Send Results Email
    E->>S: Performance Notification
```

**Features:**
- 🎯 **Adaptive Quizzes**: AI-generated based on daily learning content
- 🚪 **Progress Gating**: Must pass quizzes to unlock next learning day
- 📊 **Performance Analytics**: Detailed scoring and improvement tracking
- 📧 **Email Notifications**: Automated quiz result notifications via Gmail

</details>

<details>
<summary><strong>🌐 Google Services Integration (Individual OAuth)</strong></summary>

```mermaid
graph LR
    A[EduAI Platform] --> B[Google OAuth]
    B --> C[Gmail API]
    B --> D[Google Drive API]
    B --> E[Calendar API]
    B --> F[YouTube API]
    B --> G[Google Meet API]
    
    C --> H[📧 Notifications]
    D --> I[📁 Note Storage]
    E --> J[📅 Scheduling]
    F --> K[🎥 Video Content]
    G --> L[📹 Video Calls]
```

**Note**: Google services are implemented using **individual Composio OAuth connections** rather than unified Google OAuth, providing AI-enhanced operations with consistent API responses.

**Integrations:**
- 📧 **Gmail**: Automated notifications and communication via Composio
- 📁 **Google Drive**: Automatic note storage and retrieval via Composio
- 📅 **Calendar**: Learning schedule and reminder management via Composio
- 🎥 **YouTube**: Video search, playlist creation, content curation via Composio
- 📹 **Meet**: Video calling capabilities for tutoring sessions via Composio

</details>

<details>
<summary><strong>🔗 Social Media Integration (Composio OAuth)</strong></summary>

```mermaid
graph TB
    A[Composio OAuth] --> B[LinkedIn API]
    A --> C[GitHub API]
    A --> D[Twitter API]
    
    B --> E[Profile Connection]
    B --> F[Professional Posts]
    C --> G[Repository Management]
    C --> H[Project Tracking]
    D --> I[Profile Integration]
    D --> J[Content Sharing]
    
    K[AI Content Generator] --> F
    K --> J
```

**Platforms:**
- 💼 **LinkedIn**: Individual OAuth connection and AI-generated professional posts
- 🐙 **GitHub**: Individual OAuth connection, repository management and project tracking
- 🐦 **Twitter**: Individual OAuth connection, profile integration and content sharing
- 🤖 **AI Content**: Automatic post creation about learning progress

</details>

<details>
<summary><strong>📞 Voice Tutoring System</strong></summary>

```mermaid
sequenceDiagram
    participant S as Student
    participant T as Twilio
    participant AI as Voice AI
    participant C as Context Engine
    
    S->>T: Initiate Voice Call
    T->>C: Get Learning Context
    C->>AI: Current Progress Data
    AI->>T: Context-Aware Response
    T->>S: Personalized Voice Tutoring
```

**Features:**
- 📞 **Twilio Integration**: Voice calling with AI-powered tutoring
- 🧠 **Context-Aware**: Voice assistant knows current learning status
- ⚡ **Real-time Interaction**: Live voice conversations with AI tutor
- 📊 **Session Tracking**: Call recording and analysis capabilities

</details>

### 🏢 Recruiter Features

<details>
<summary><strong>🎯 AI-Powered Candidate Matching</strong></summary>

```mermaid
graph TD
    A[Job Requirements] --> B[AI Analysis Engine]
    C[Student Profiles] --> B
    D[Learning Progress] --> B
    E[Quiz Performance] --> B
    F[Social Connections] --> B
    
    B --> G[Compatibility Scoring]
    G --> H[Match Explanations]
    H --> I[Recommendations]
    
    J[Bulk Processing] --> B
    K[Multi-factor Algorithm] --> G
```

**Capabilities:**
- 🧠 **Intelligent Matching**: AI analyzes job requirements against student profiles
- 📊 **Comprehensive Scoring**: Multi-factor algorithm considering skills, goals, performance
- 💡 **Detailed Explanations**: AI provides reasoning for each match score
- ⚡ **Bulk Analysis**: Process multiple candidates simultaneously

</details>

<details>
<summary><strong>📧 Advanced Email Application Management</strong></summary>

```mermaid
sequenceDiagram
    participant E as Gmail API
    participant AI as Gemini AI
    participant P as PDF Parser
    participant D as Database
    participant R as Recruiter
    
    E->>AI: Fetch Job Applications
    AI->>P: Extract Resume Data
    P->>AI: Parsed Skills & Info
    AI->>D: Create Candidate Profile
    D->>R: Enhanced Profile Summary
```

**Features:**
- 📧 **Gmail Integration**: Automatic job application email fetching with enhanced filtering
- 🤖 **AI Summarization**: Intelligent email content analysis and candidate profiling
- 📄 **Resume Processing**: PDF attachment parsing and skill extraction
- 👤 **Candidate Creation**: Automatic profile creation from email applications
- 🔍 **Smart Filtering**: Job-related email detection with priority scoring

</details>

<details>
<summary><strong>📅 Interview Management System</strong></summary>

```mermaid
graph TB
    A[Interview Request] --> B[Calendar Check]
    B --> C[Availability Verification]
    C --> D[Google Meet Creation]
    D --> E[Calendar Invite]
    E --> F[Email Notifications]
    
    G[Interview Tracking] --> H[Lifecycle Management]
    I[Automated Reminders] --> F
```

**System:**
- 📹 **Google Meet Integration**: Automated interview scheduling with calendar invites
- ⏰ **Availability Checking**: Real-time calendar availability verification
- 📋 **Interview Tracking**: Complete interview lifecycle management
- 📧 **Automated Notifications**: Email confirmations and reminders
- 🔄 **Reschedule/Cancel**: Full interview management capabilities

</details>

<details>
<summary><strong>🤖 Advanced Recruiter AI Assistant</strong></summary>

```mermaid
graph TD
    A[Recruiter Query] --> B[AI Assistant]
    B --> C{Query Type}
    
    C -->|Candidate Search| D[Database Query]
    C -->|Email Analysis| E[Gmail Integration]
    C -->|Insights Request| F[Analytics Engine]
    C -->|Strategy Help| G[Recommendation Engine]
    
    D --> H[Intelligent Response]
    E --> H
    F --> H
    G --> H
```

**Assistant:**
- 🧠 **Intelligent Chatbot**: AI assistant with access to all candidate data
- 🔍 **Email Search**: Natural language search through job applications
- 💡 **Candidate Insights**: AI-powered candidate analysis and recommendations
- 📈 **Recruitment Strategy**: Data-driven hiring insights and suggestions
- 📊 **Real-time Analytics**: Access to comprehensive recruitment metrics

</details>

---

## 🏗️ System Architecture

### 🔄 Application Flow Visualization

```mermaid
graph TB
    subgraph "Student Journey"
        A1[Registration] --> A2[Onboarding]
        A2 --> A3[Learning Plan Generation]
        A3 --> A4[Daily Learning]
        A4 --> A5[Quiz System]
        A5 --> A6[Progress Tracking]
        A6 --> A7[Social Integration]
    end
    
    subgraph "Recruiter Journey"
        B1[Recruiter Registration] --> B2[Dashboard Access]
        B2 --> B3[Job Posting]
        B3 --> B4[AI Matching]
        B4 --> B5[Email Processing]
        B5 --> B6[Interview Scheduling]
        B6 --> B7[Candidate Management]
    end
    
    subgraph "AI Integration Layer"
        C1[Gemini AI Engine]
        C2[Function Calling]
        C3[Context Management]
        C4[Response Processing]
    end
    
    A4 --> C1
    A5 --> C1
    B4 --> C1
    B5 --> C1
```

### 🔐 Individual OAuth Architecture (Composio-Based)

```mermaid
graph TB
    subgraph "Authentication Layer"
        A[User Login] --> B{Service Type}
        B -->|Google Services| C[Composio OAuth]
        B -->|Social Media| D[Composio OAuth]
        
        C --> E[Individual Connections]
        D --> F[Individual Connections]
        
        E --> G[Gmail OAuth]
        E --> H[Drive OAuth]
        E --> I[Calendar OAuth]
        E --> J[YouTube OAuth]
        E --> K[Meet OAuth]
        
        F --> L[LinkedIn OAuth]
        F --> M[GitHub OAuth]
        F --> N[Twitter OAuth]
        
        G --> O[Platform Access]
        H --> O
        I --> O
        J --> O
        K --> O
        L --> O
        M --> O
        N --> O
    end
    
    subgraph "Security Features"
        P[JWT Tokens]
        Q[Token Refresh]
        R[Scope Management]
        S[Encrypted Storage]
    end
    
    O --> P
    O --> Q
    O --> R
    O --> S
```

---

## 🔧 Technology Stack

### 🎨 Frontend (React 19.1.0)
- **45+ Components**: Dashboard, LearningPlans, Chatbot, RecruiterDashboard, etc.
- **Modern UI**: Styled-components, Framer Motion, React Icons
- **Routing**: React Router DOM with protected routes
- **State Management**: React Hooks and Context API

### ⚙️ Backend (FastAPI)
- **Core Services**: Gemini AI, Composio OAuth, Twilio integration
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens with individual OAuth services
- **API Routes**: Auth, Chatbot, Learning Plans, Quiz, Recruiter

### 🤖 AI Integration
- **Gemini AI**: 2.0 Flash, 1.5 Pro with fallback system
- **Function Calling**: 8+ integrated tools
- **Context Awareness**: Real-time learning progress tracking
- **Content Generation**: Learning materials and quiz creation

### 🔗 External Integrations
- **Google Services**: Gmail, Drive, Calendar, YouTube, Meet (via Composio individual OAuth)
- **Social Media**: LinkedIn, GitHub, Twitter (via Composio individual OAuth)
- **Twilio**: Voice calling and SMS
- **Database**: PostgreSQL with complex relationships

---

## 📊 Technical Metrics

<table>
<tr>
<th>Category</th>
<th>Metric</th>
<th>Value</th>
</tr>
<tr>
<td rowspan="4"><strong>🏗️ Architecture</strong></td>
<td>React Components</td>
<td>45+</td>
</tr>
<tr>
<td>Backend Routes</td>
<td>10+ modules</td>
</tr>
<tr>
<td>Database Models</td>
<td>15+</td>
</tr>
<tr>
<td>API Integrations</td>
<td>10+</td>
</tr>
<tr>
<td rowspan="3"><strong>🤖 AI Features</strong></td>
<td>AI Models</td>
<td>4 (Fallback)</td>
</tr>
<tr>
<td>Function Tools</td>
<td>8+</td>
</tr>
<tr>
<td>Context Awareness</td>
<td>Real-time</td>
</tr>
<tr>
<td rowspan="3"><strong>🔗 Integrations</strong></td>
<td>Google Services</td>
<td>5 APIs (Individual OAuth)</td>
</tr>
<tr>
<td>Social Platforms</td>
<td>3 (Individual OAuth)</td>
</tr>
<tr>
<td>Communication</td>
<td>Voice + Email</td>
</tr>
</table>

---

## 🚀 Quick Start

### 📋 Prerequisites
```bash
# Required Software
- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Git

# API Keys Required
- Gemini AI API Key
- Composio API Key (for all OAuth services)
- Twilio Account (optional)
```

### ⚡ Installation

**Backend Setup:**
```bash
cd learning/fastapi-backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

**Frontend Setup:**
```bash
cd learning/learning-ui
npm install
npm start
```

### 🔑 Environment Variables
```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/eduaidb

# AI Services
GEMINI_API_KEY=your_gemini_api_key
COMPOSIO_API_KEY=your_composio_api_key

# Communication (Optional)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
```

---

## 📚 API Documentation

### 🎓 Student APIs
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/google/callback` | JWT authentication |
| `GET` | `/learning-plan` | Get user's learning plan |
| `POST` | `/learning-plan/generate` | AI-generated learning plan |
| `POST` | `/chat` | AI chatbot with 8+ tool integration |
| `GET` | `/quiz/{month}/{day}` | Get daily quiz |
| `POST` | `/quiz/submit` | Submit quiz answers |
| `POST` | `/call/initiate` | Twilio voice calling |
| `POST` | `/auth/linkedin/connect` | LinkedIn OAuth via Composio |
| `POST` | `/auth/github/connect` | GitHub OAuth via Composio |
| `POST` | `/auth/twitter/connect` | Twitter OAuth via Composio |

### 🏢 Recruiter APIs
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/recruiter/dashboard` | Comprehensive recruiter dashboard |
| `POST` | `/recruiter/match` | AI-powered candidate matching |
| `GET` | `/recruiter/students` | All student profiles with analytics |
| `POST` | `/recruiter/jobs` | Create job postings |
| `GET` | `/recruiter/emails/recent` | Job application emails with AI analysis |
| `POST` | `/recruiter/chat` | Advanced recruiter AI assistant |
| `POST` | `/recruiter/interviews/schedule` | Google Meet interview scheduling |
| `GET` | `/recruiter/analytics` | Comprehensive recruitment analytics |

---

## 🏆 Innovation Highlights

### 🔐 Individual OAuth Strategy (Composio-Based)
**Revolutionary Approach**: Uses Composio for individual OAuth connections to each service (Gmail, Drive, Calendar, YouTube, Meet, LinkedIn, GitHub, Twitter) rather than unified packages, providing AI-enhanced operations with consistent API responses.

### 🤖 Context-Aware AI Integration
**Advanced Implementation**: AI assistant with deep platform integration, knowing user's exact learning position and providing contextual responses with 8+ tool integrations.

### 📞 Voice-Enabled Learning
**Unique Feature**: AI-powered voice tutoring system with context awareness and real-time conversation capabilities via Twilio integration.

### 📧 Intelligent Email Processing
**Advanced Feature**: AI-powered job application email analysis with resume parsing, candidate profiling, and automatic shortlisting capabilities.

---

## 📄 License & Acknowledgments

### 🙏 Acknowledgments

<table>
<tr>
<td align="center">
<img src="https://img.shields.io/badge/Google-AI-blue?style=for-the-badge&logo=google" alt="Google AI"/>
<br/><strong>Gemini AI Platform</strong><br/>Advanced language processing
</td>
<td align="center">
<img src="https://img.shields.io/badge/Composio-Integration-green?style=for-the-badge&logo=api" alt="Composio"/>
<br/><strong>Composio Platform</strong><br/>Individual OAuth integrations
</td>
<td align="center">
<img src="https://img.shields.io/badge/Twilio-Communication-red?style=for-the-badge&logo=twilio" alt="Twilio"/>
<br/><strong>Twilio Services</strong><br/>Voice and SMS communication
</td>
</tr>
<tr>
<td align="center">
<img src="https://img.shields.io/badge/FastAPI-Backend-teal?style=for-the-badge&logo=fastapi" alt="FastAPI"/>
<br/><strong>FastAPI Framework</strong><br/>Modern Python web framework
</td>
<td align="center">
<img src="https://img.shields.io/badge/React-Frontend-blue?style=for-the-badge&logo=react" alt="React"/>
<br/><strong>React Library</strong><br/>Frontend user interfaces
</td>
<td align="center">
<img src="https://img.shields.io/badge/PostgreSQL-Database-blue?style=for-the-badge&logo=postgresql" alt="PostgreSQL"/>
<br/><strong>PostgreSQL</strong><br/>Robust database system
</td>
</tr>
</table>

---

## 📸 Platform Screenshots

![Screenshot 1](Images/Screenshot%202025-10-22%20095357.png)

![Screenshot 2](Images/Screenshot%202025-10-22%20095408.png)

![Screenshot 3](Images/Screenshot%202025-10-22%20095510.png)

![Screenshot 4](Images/Screenshot%202025-10-22%20095520.png)

![Screenshot 5](Images/Screenshot%202025-10-22%20095531.png)

![Screenshot 6](Images/Screenshot%202025-10-22%20095543.png)

![Screenshot 7](Images/Screenshot%202025-10-22%20095554.png)

![Screenshot 8](Images/Screenshot%202025-10-22%20095600.png)

![Screenshot 9](Images/Screenshot%202025-10-22%20095821.png)

![Screenshot 10](Images/Screenshot%202025-10-22%20095839.png)

![Screenshot 11](Images/Screenshot%202025-10-22%20095906.png)

![Screenshot 12](Images/Screenshot%202025-10-22%20100000.png)

![Screenshot 13](Images/Screenshot%202025-10-22%20100008.png)

![Screenshot 14](Images/Screenshot%202025-10-22%20100019.png)

![Screenshot 15](Images/Screenshot%202025-10-22%20100127.png)

![Screenshot 16](Images/Screenshot%202025-10-22%20100137.png)

![Screenshot 17](Images/Screenshot%202025-10-22%20110119.png)

![Screenshot 18](Images/Screenshot%202025-10-22%20110246.png)

![Screenshot 19](Images/Screenshot%202025-10-22%20110251.png)

![Screenshot 20](Images/Screenshot%202025-10-22%20110257.png)

![Screenshot 21](Images/Screenshot%202025-10-22%20100352.png)

![Screenshot 22](Images/Screenshot%202025-10-22%20100410.png)

![Screenshot 23](Images/Screenshot%202025-10-22%20100513.png)

![Screenshot 24](Images/Screenshot%202025-10-22%20100813.png)

![Screenshot 25](Images/Screenshot%202025-10-22%20100919.png)

![Screenshot 26](Images/Screenshot%202025-10-22%20100936.png)

![Screenshot 27](Images/Screenshot%202025-10-22%20101036.png)

![Screenshot 28](Images/Screenshot%202025-10-22%20101046.png)

![Screenshot 29](Images/Screenshot%202025-10-22%20101150.png)

![Screenshot 30](Images/Screenshot%202025-10-22%20101201.png)

![Screenshot 31](Images/Screenshot%202025-10-22%20101226.png)

![Screenshot 32](Images/Screenshot%202025-10-22%20101244.png)

![Screenshot 33](Images/Screenshot%202025-10-22%20101442.png)

![Screenshot 34](Images/Screenshot%202025-10-22%20101502.png)

![Screenshot 35](Images/Screenshot%202025-10-22%20101512.png)

![Screenshot 36](Images/Screenshot%202025-10-22%20101519.png)

![Screenshot 37](Images/Screenshot%202025-10-22%20101640.png)

![Screenshot 38](Images/Screenshot%202025-10-22%20101646.png)

![Screenshot 39](Images/Screenshot%202025-10-22%20101705.png)

![Screenshot 40](Images/Screenshot%202025-10-22%20101759.png)

![Screenshot 41](Images/Screenshot%202025-10-22%20101827.png)

![Screenshot 42](Images/Screenshot%202025-10-22%20103526.png)

![Screenshot 43](Images/Screenshot%202025-10-22%20103544.png)

![Screenshot 44](Images/Screenshot%202025-10-22%20103625.png)

![Screenshot 45](Images/Screenshot%202025-10-22%20103633.png)

![Screenshot 46](Images/Screenshot%202025-10-22%20104818.png)

![Screenshot 47](Images/Screenshot%202025-10-22%20105102.png)

![Screenshot 48](Images/Screenshot%202025-10-22%20105109.png)

![Screenshot 49](Images/Screenshot%202025-10-22%20105236.png)

![Screenshot 50](Images/Screenshot%202025-10-22%20105257.png)

![Screenshot 51](Images/Screenshot%202025-10-22%20105322.png)

![Screenshot 52](Images/Screenshot%202025-10-22%20105330.png)

![Screenshot 53](Images/Screenshot%202025-10-22%20105416.png)

![Screenshot 54](Images/Screenshot%202025-10-22%20105424.png)

---

<div align="center">

## 🎉 Built with ❤️ during a 6-day intensive hackathon sprint

**EduAI represents the future of personalized learning and intelligent recruitment, combining cutting-edge AI with practical educational tools through individual OAuth service integrations.**

</div>
