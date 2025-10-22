import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import OnboardingFlow from './components/OnboardingFlow';
import Login from './components/Login';
import Register from './components/Register'
import Dashboard from './components/Dashboard';
import LearningPlans from './components/LearningPlans';
import Subplans from './components/Subplans';
import Quizzes from './components/Quizzes';
import Notes from './components/Notes';
import Calendar from './components/Calendar';
import VoiceTutor from './components/VoiceTutor';
import Resume from './components/Resume';
import Community from './components/Community';
import Progress from './components/Progress';
import Settings from './components/Settings';
import YouTubeLearning from './components/YouTubeLearning';
import GoogleCallback from './components/GoogleCallback';
import Profile from './components/Profile';
import Chatbot from './components/Chatbot';
import LandingPage from './components/LandingPage'; // or wherever your file is located // Update this import to point to your new LandingPage component
import RecruiterDashboard from './components/RecruiterDashboard';
import RecruiterLogin from './components/RecruiterLogin';
import RecruiterAuthCheck from './components/RecruiterAuthCheck';
import RecruiterJobPosting from './components/RecruiterJobPosting';
import RecruiterCandidates from './components/RecruiterCandidates';
import RecruiterProfile from './components/RecruiterProfile';
import CandidateDetail from './components/CandidateDetail';
import RecruiterEmailAnalysis from './components/RecruiterEmailAnalysis';
import RecruiterOAuthCallback from './components/RecruiterOAuthCallback';
import RecruiterJobPost from './components/RecruiterJobPost';
import RecruiterJobs from './components/RecruiterJobs';
import RecruiterChatbot from './components/RecruiterChatbot';
import RecruiterStudentProfile from './components/RecruiterStudentProfile';
import JobListings from './components/JobListings';
import JobDetailsPage from './components/JobDetailsPage';
import RecruiterInterviews from './components/RecruiterInterviews';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/auth/google/callback" element={<GoogleCallback />} />
        <Route path="/onboarding" element={<OnboardingFlow />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/learning-plans" element={<LearningPlans />} />
        <Route path="/learning-plans/:planId" element={<LearningPlans />} />
        <Route path="/learning-plans/:planId/month/:monthIndex" element={<LearningPlans />} />
        <Route path="/learning-plans/:planId/month/:monthIndex/day/:day" element={<LearningPlans />} />
        <Route path="/subplans" element={<Subplans />} />
        <Route path="/quizzes" element={<Quizzes />} />
        <Route path="/notes" element={<Notes />} />
        <Route path="/calendar" element={<Calendar />} />
        <Route path="/voice-tutor" element={<VoiceTutor />} />
        <Route path="/resume" element={<Resume />} />
        <Route path="/community" element={<Community />} />
        <Route path="/progress" element={<Progress />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/youtube-learning" element={<YouTubeLearning />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/recruiter/login" element={<RecruiterLogin />} />
        <Route path="/recruiter" element={<RecruiterAuthCheck><RecruiterDashboard /></RecruiterAuthCheck>} />
        <Route path="/recruiter/post-job" element={<RecruiterAuthCheck><RecruiterJobPost /></RecruiterAuthCheck>} />
        <Route path="/recruiter/jobs" element={<RecruiterAuthCheck><JobListings /></RecruiterAuthCheck>} />
        <Route path="/recruiter/job/:jobId" element={<RecruiterAuthCheck><JobDetailsPage /></RecruiterAuthCheck>} />
        <Route path="/recruiter/candidates" element={<RecruiterAuthCheck><RecruiterCandidates /></RecruiterAuthCheck>} />
        <Route path="/recruiter/interviews" element={<RecruiterAuthCheck><RecruiterInterviews /></RecruiterAuthCheck>} />
        <Route path="/recruiter/profile" element={<RecruiterAuthCheck><RecruiterProfile /></RecruiterAuthCheck>} />
        <Route path="/recruiter/candidate/:userId" element={<RecruiterAuthCheck><CandidateDetail /></RecruiterAuthCheck>} />
        <Route path="/recruiter/student-profile/:studentId" element={<RecruiterAuthCheck><RecruiterStudentProfile /></RecruiterAuthCheck>} />
        <Route path="/recruiter/emails" element={<RecruiterAuthCheck><RecruiterEmailAnalysis /></RecruiterAuthCheck>} />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
      
      {/* Conditional Chatbots */}
      {window.location.pathname.startsWith('/recruiter') ? <RecruiterChatbot /> : <Chatbot />}
    </Router>
  );
}

export default App;