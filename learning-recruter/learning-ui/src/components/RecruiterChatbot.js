import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiMessageCircle, FiX, FiSend, FiUsers, FiBriefcase, FiTrendingUp, FiList, FiTrash2 } from 'react-icons/fi';
import { recruiterAuthenticatedFetch } from '../api';

const RecruiterChatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hi! I'm your AI recruiting assistant. I can help you with candidate insights, student progress analysis, and recruitment strategies. What would you like to know?",
      sender: 'bot',
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [waitlistedCandidates, setWaitlistedCandidates] = useState([]);
  const [showWaitlist, setShowWaitlist] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize chatbot data after component mounts
  useEffect(() => {
    const initializeChatbot = async () => {
      const token = localStorage.getItem('recruiter_token');
      if (token && !isInitialized) {
        try {
          // Pre-load insights to ensure chatbot has data ready
          const insightsData = await recruiterAuthenticatedFetch('/recruiter/chatbot/insights');
          
          // Add a welcome message with current stats
          const analytics = insightsData.analytics || {};
          const welcomeMessage = {
            id: Date.now(),
            text: `🚀 **System Ready!** I have access to:\n\n📊 ${analytics.total_students || 0} students, ${analytics.active_students || 0} active learners\n📧 ${analytics.total_emails || 0} emails processed\n🔥 Top skill: ${analytics.top_skills?.[0]?.skill || 'Various skills'}\n\n💡 **Try asking:** "Analyze Abhishek Shetty profile" or "Show top candidates"`,
            sender: 'bot',
            timestamp: new Date()
          };
          
          setMessages(prev => [...prev, welcomeMessage]);
          setIsInitialized(true);
        } catch (error) {
          console.error('Chatbot initialization error:', error);
          // Still mark as initialized to prevent infinite retries
          setIsInitialized(true);
        }
      }
    };

    // Delay initialization slightly to ensure the layout is ready
    const timer = setTimeout(initializeChatbot, 1000);
    return () => clearTimeout(timer);
  }, [isInitialized]);

  const quickActions = [
    { icon: FiUsers, text: "Show top candidates", action: "top_candidates" },
    { icon: FiBriefcase, text: "Job matching insights", action: "job_insights" },
    { icon: FiTrendingUp, text: "Student progress analysis", action: "progress_analysis" },
    { icon: FiMessageCircle, text: "Recent emails", action: "recent_emails" },
    { icon: FiList, text: "Waitlisted candidates", action: "show_waitlist" }
  ];

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    try {
      const emailData = JSON.parse(e.dataTransfer.getData('text/plain'));
      
      // Check if already in waitlist
      if (!waitlistedCandidates.find(c => c.id === emailData.id)) {
        setWaitlistedCandidates(prev => [...prev, {
          id: emailData.id,
          name: emailData.sender_name,
          email: emailData.sender_email,
          subject: emailData.subject,
          content: emailData.content,
          attachments: emailData.attachments || [],
          addedAt: new Date().toISOString()
        }]);
        
        // Add confirmation message
        const confirmMessage = {
          id: Date.now(),
          text: `✅ ${emailData.sender_name} added to waitlist! You can now ask me about this candidate.`,
          sender: 'bot',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, confirmMessage]);
      }
    } catch (error) {
      console.error('Drop error:', error);
    }
  };

  const removeFromWaitlist = (candidateId) => {
    setWaitlistedCandidates(prev => prev.filter(c => c.id !== candidateId));
  };

  const askAboutCandidate = (candidate) => {
    setInputMessage(`Tell me about ${candidate.name} from the waitlist`);
    setTimeout(() => handleSendMessage(), 100);
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: Date.now(),
      text: inputMessage,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsTyping(true);

    try {
      const response = await getAIResponse(inputMessage);
      
      setTimeout(() => {
        const botMessage = {
          id: Date.now() + 1,
          text: response,
          sender: 'bot',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, botMessage]);
        setIsTyping(false);
      }, 1000);
    } catch (error) {
      setTimeout(() => {
        const errorMessage = {
          id: Date.now() + 1,
          text: "I'm having trouble accessing the data right now. Please try again later.",
          sender: 'bot',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, errorMessage]);
        setIsTyping(false);
      }, 1000);
    }
  };

  const getAIResponse = async (message) => {
    try {
      // Get comprehensive student insights and emails for chatbot
      const insightsData = await recruiterAuthenticatedFetch('/recruiter/chatbot/insights');
      
      const students = insightsData.students || [];
      const emails = insightsData.emails || [];
      const analytics = insightsData.analytics || {};

      // Analyze the message and provide contextual responses
      const lowerMessage = message.toLowerCase();

      if (lowerMessage.includes('top') && lowerMessage.includes('candidate')) {
        const topStudents = students
          .filter(s => s.learning_progress > 70)
          .slice(0, 3)
          .map(s => `• ${s.name}: ${Math.round(s.learning_progress)}% learning progress, Skills: ${(s.skills || []).slice(0, 2).join(', ')}`)
          .join('\n');
        
        return `Here are your top candidates based on learning progress:\n\n${topStudents || 'No high-progress candidates found yet.'}\n\nWould you like me to analyze specific skills or create a job posting to match these candidates?`;
      }

      if (lowerMessage.includes('recent') && lowerMessage.includes('email')) {
        const recentEmails = emails.slice(0, 5);
        if (recentEmails.length > 0) {
          const emailList = recentEmails.map(email => {
            const hasResume = email.attachments?.some(att => att.type === 'pdf');
            return `• **${email.sender_name}**: ${email.subject}\n  📧 ${email.sender_email}\n  ${hasResume ? '📄 Resume attached' : '📎 Has attachments'}`;
          }).join('\n\n');
          
          return `📧 **Recent Applications:**\n\n${emailList}\n\n💡 **Commands:**\n• "Find email from [name]" - View full details\n• "Analyze [name] resume" - Get AI assessment\n• "Show top candidates" - See best matches`;
        } else {
          return `No recent emails found. Job applications will appear here when candidates reach out.`;
        }
      }

      // Check if asking about waitlisted candidate
      if (lowerMessage.includes('waitlist') || lowerMessage.includes('from the waitlist')) {
        const nameQuery = message.replace(/.*(?:tell me about|about)\s+([^\s]+(?:\s+[^\s]+)*)\s+from the waitlist.*/i, '$1').trim();
        
        if (nameQuery) {
          const waitlistedCandidate = waitlistedCandidates.find(c => 
            c.name.toLowerCase().includes(nameQuery.toLowerCase())
          );
          
          if (waitlistedCandidate) {
            // Search for detailed analysis
            try {
              const searchResults = await recruiterAuthenticatedFetch('/recruiter/chatbot/search-emails', {
                method: 'POST',
                body: JSON.stringify({ query: waitlistedCandidate.name })
              });
              
              if (searchResults.emails && searchResults.emails.length > 0) {
                const email = searchResults.emails[0];
                let response = `🎯 **WAITLISTED CANDIDATE: ${email.sender_name.toUpperCase()}**\n\n📋 **Email Details:**\n• Subject: ${email.subject}\n• From: ${email.sender_email}\n• Added to waitlist: ${new Date(waitlistedCandidate.addedAt).toLocaleDateString()}`;
                
                if (email.pdf_analysis) {
                  response += `\n\n${email.pdf_analysis}`;
                } else {
                  response += `\n\n📎 **Content:** ${email.content.substring(0, 200)}...`;
                }
                
                return response + `\n\n🚀 **ACTIONS:** "add ${email.sender_name} to watchlist" or "schedule interview"`;
              }
            } catch (error) {
              return `📋 **WAITLISTED: ${waitlistedCandidate.name}**\n\n• Email: ${waitlistedCandidate.email}\n• Subject: ${waitlistedCandidate.subject}\n• Added: ${new Date(waitlistedCandidate.addedAt).toLocaleDateString()}\n\n📄 Content: ${waitlistedCandidate.content.substring(0, 200)}...\n\nDrag more emails to analyze candidates!`;
            }
          }
        }
        
        // Show waitlist summary
        if (waitlistedCandidates.length > 0) {
          const candidateList = waitlistedCandidates.map(c => 
            `• **${c.name}**: ${c.subject}\n  📧 ${c.email} | Added: ${new Date(c.addedAt).toLocaleDateString()}`
          ).join('\n\n');
          
          return `📋 **WAITLISTED CANDIDATES (${waitlistedCandidates.length})**\n\n${candidateList}\n\n💡 **Ask:** "Tell me about [name] from the waitlist" for detailed analysis`;
        } else {
          return `📋 **WAITLIST EMPTY**\n\nDrag emails from your inbox into the waitlist area to analyze candidates. Once added, you can ask me detailed questions about them!`;
        }
      }
      
      if (lowerMessage.includes('progress') || lowerMessage.includes('learning')) {
        const dist = analytics.progress_distribution || {};
        const topSkills = analytics.top_skills?.slice(0, 3).map(s => s.skill).join(', ') || 'Various skills';
        
        return `📊 Student Learning Analytics:\n\n• Total Students: ${analytics.total_students}\n• Active Learners: ${analytics.active_students}\n• Average Progress: ${analytics.average_progress}%\n\n📈 Progress Distribution:\n• High Progress (70%+): ${dist.high_progress} students\n• Medium Progress (30-70%): ${dist.medium_progress} students\n• Getting Started: ${dist.low_progress} students\n\n🔥 Top Skills: ${topSkills}\n\nStudents are actively improving their skills. This is a great time to post jobs and engage with high-potential candidates!`;
      }

      if (lowerMessage.includes('job') && (lowerMessage.includes('match') || lowerMessage.includes('insight'))) {
        const topSkills = analytics.top_skills?.slice(0, 5).map(s => `${s.skill} (${s.count} students)`).join(', ') || 'No skills data';
        const bestSkill = analytics.top_skills?.[0]?.skill || 'popular skills';
        
        return `🎯 Job Matching Insights:\n\n• Most In-Demand Skills: ${topSkills}\n• Total Skill Categories: ${analytics.top_skills?.length || 0}\n• High-Progress Candidates: ${analytics.progress_distribution?.high_progress || 0}\n\n💡 Recommendation: Post jobs requiring ${bestSkill} for best match rates\n\nWould you like me to help you create a job posting targeting these skills?`;
      }

      if (lowerMessage.includes('skill')) {
        const skills = analytics.top_skills?.slice(0, 8) || [];
        const skillList = skills.map(s => `• ${s.skill}: ${s.count} students (${s.percentage}%)`).join('\n');
        
        return `🔧 Current Skill Landscape:\n\n${skillList || 'No skills data available'}\n\nThese are the most in-demand skills among our student community. Consider posting jobs that match these competencies for higher response rates.`;
      }

      if (lowerMessage.includes('email') || lowerMessage.includes('message')) {
        // Check if asking about specific email or general email strategy
        if (lowerMessage.includes('from') || lowerMessage.includes('by') || lowerMessage.includes('find')) {
          // Search for specific email
          const searchQuery = message.replace(/.*(?:from|by|find|email|message)\s+/i, '').trim();
          
          if (searchQuery) {
            try {
              const searchResults = await recruiterAuthenticatedFetch('/recruiter/chatbot/search-emails', {
                method: 'POST',
                body: JSON.stringify({ query: searchQuery })
              });
              
              if (searchResults.emails && searchResults.emails.length > 0) {
                const email = searchResults.emails[0];
                let response = `📧 **APPLICATION FROM ${email.sender_name.toUpperCase()}**\n\n📋 **Email Details:**\n• Subject: ${email.subject}\n• From: ${email.sender_email}\n• Content: ${email.content.substring(0, 100)}...`;
                
                // Show PDF analysis if available
                if (email.pdf_analysis) {
                  response += `\n\n${email.pdf_analysis}`;
                } else if (email.attachments && email.attachments.length > 0) {
                  response += `\n\n📎 **ATTACHMENTS:**\n`;
                  email.attachments.forEach(att => {
                    if (att.type === 'pdf') {
                      response += `• 📄 ${att.filename}\n• Content Preview: ${att.content.substring(0, 150)}...\n`;
                    } else {
                      response += `• 📎 ${att.filename}\n`;
                    }
                  });
                }
                
                return response + `\n\n🚀 **ACTIONS:** Type "add ${email.sender_name} to watchlist" or "schedule interview with ${email.sender_name}"`;
              } else {
                return `No emails found matching "${searchQuery}". Try searching by name, email address, or subject keywords.`;
              }
            } catch (error) {
              return `Unable to search emails right now. Please try again later.`;
            }
          }
        }
        
        // General email strategy
        const totalEmails = analytics.total_emails || 0;
        const unreadEmails = analytics.unread_emails || 0;
        const highProgressCount = analytics.progress_distribution?.high_progress || 0;
        
        return `📧 Email Overview:\n\n• Total Emails: ${totalEmails}\n• Unread: ${unreadEmails}\n• High-Progress Candidates: ${highProgressCount}\n\n💡 **Email Strategy Tips:**\n• Personalize with candidate names and skills\n• Mention specific learning achievements\n• Include clear next steps\n• Target active learners for better response\n\n**Search emails by:** "find email from [name]" or "show email about [topic]"\n\nWhat would you like to know about your emails?`;
      }

      // Check if asking about specific person/candidate - enhanced search
      if (lowerMessage.includes('who is') || lowerMessage.includes('tell me about') || lowerMessage.includes('find student') || lowerMessage.includes('analyze') || lowerMessage.includes('profile')) {
        let nameQuery = '';
        
        // Extract name from various patterns
        if (lowerMessage.includes('analyze') && lowerMessage.includes('profile')) {
          nameQuery = message.replace(/.*analyze\s+([^\s]+(?:\s+[^\s]+)*)\s+profile.*/i, '$1').trim();
        } else if (lowerMessage.includes('who is')) {
          nameQuery = message.replace(/.*who is\s+([^\s]+(?:\s+[^\s]+)*).*/i, '$1').trim();
        } else if (lowerMessage.includes('tell me about')) {
          nameQuery = message.replace(/.*tell me about\s+([^\s]+(?:\s+[^\s]+)*).*/i, '$1').trim();
        } else if (lowerMessage.includes('find student')) {
          nameQuery = message.replace(/.*find student\s+([^\s]+(?:\s+[^\s]+)*).*/i, '$1').trim();
        }
        
        if (nameQuery && nameQuery.length > 2) {
          // Enhanced matching - check name parts, email, and partial matches
          const matchingStudent = students.find(s => {
            const studentName = (s.name || '').toLowerCase();
            const studentEmail = (s.email || '').toLowerCase();
            const queryLower = nameQuery.toLowerCase();
            
            // Exact match
            if (studentName.includes(queryLower) || studentEmail.includes(queryLower)) {
              return true;
            }
            
            // Check individual name parts
            const nameParts = queryLower.split(' ');
            const studentParts = studentName.split(' ');
            
            return nameParts.every(part => 
              studentParts.some(studentPart => 
                studentPart.includes(part) || part.includes(studentPart)
              )
            );
          });
          
          if (matchingStudent) {
            // Get comprehensive analytics for this student
            try {
              const analyticsResponse = await recruiterAuthenticatedFetch(`/recruiter/analytics/user/${matchingStudent.id}`);
              
              let response = `🎯 **CANDIDATE ANALYSIS: ${matchingStudent.name.toUpperCase()}**\n\n`;
              response += `📧 **Contact:** ${matchingStudent.email}\n`;
              response += `📈 **Learning Progress:** ${Math.round(matchingStudent.learning_progress)}%\n`;
              response += `🎯 **Career Goals:** ${matchingStudent.career_goals || 'Not specified'}\n`;
              response += `🔧 **Skills:** ${(matchingStudent.skills_tags || []).join(', ') || 'No skills listed'}\n`;
              response += `📅 **Joined:** ${new Date(matchingStudent.created_at).toLocaleDateString()}\n`;
              response += `📊 **Source:** ${matchingStudent.added_by_recruiter ? '✉️ Email Application' : '🎓 Platform User'}\n\n`;
              
              if (analyticsResponse) {
                const metrics = analyticsResponse.learning_metrics || {};
                response += `📊 **PERFORMANCE METRICS:**\n`;
                response += `• Learning Streak: ${metrics.current_streak || 0} days\n`;
                response += `• Quiz Performance: ${Math.round((metrics.avg_score || 0) * 100)}% average\n`;
                response += `• Total Assessments: ${metrics.total_quizzes || 0}\n`;
                response += `• Performance Trend: ${metrics.performance_trend || 'stable'}\n\n`;
                
                if (analyticsResponse.recommendations && analyticsResponse.recommendations.length > 0) {
                  response += `💡 **RECOMMENDATIONS:**\n`;
                  analyticsResponse.recommendations.forEach(rec => {
                    response += `• ${rec}\n`;
                  });
                  response += `\n`;
                }
                
                if (analyticsResponse.career_readiness) {
                  const readiness = analyticsResponse.career_readiness;
                  response += `🚀 **CAREER READINESS:** ${readiness.level} (${Math.round(readiness.overall_score * 100)}%)\n`;
                  response += `${readiness.description}\n\n`;
                }
              }
              
              response += `${matchingStudent.summary || 'No detailed summary available'}\n\n`;
              response += `🎯 **NEXT STEPS:**\n• Schedule interview\n• Send personalized job offer\n• Add to watchlist for future opportunities`;
              
              return response;
            } catch (error) {
              // Fallback to basic info if analytics fail
              return `👤 **${matchingStudent.name}**\n\n📧 Email: ${matchingStudent.email}\n📈 Learning Progress: ${Math.round(matchingStudent.learning_progress)}%\n🎯 Career Goals: ${matchingStudent.career_goals || 'Not specified'}\n🔧 Skills: ${(matchingStudent.skills_tags || []).join(', ') || 'No skills listed'}\n📅 Joined: ${new Date(matchingStudent.created_at).toLocaleDateString()}\n\n${matchingStudent.added_by_recruiter ? '✉️ Added from email application' : '🎓 Platform user'}\n\n${matchingStudent.summary || 'No summary available'}\n\nWould you like to see their detailed profile or find matching jobs?`;
            }
          } else {
            // Search in emails as well
            const emailMatch = emails.find(email => 
              email.sender_name.toLowerCase().includes(nameQuery.toLowerCase()) ||
              email.sender_email.toLowerCase().includes(nameQuery.toLowerCase())
            );
            
            if (emailMatch) {
              return `📧 **FOUND IN EMAILS: ${emailMatch.sender_name}**\n\n• Email: ${emailMatch.sender_email}\n• Subject: ${emailMatch.subject}\n• Content: ${emailMatch.content.substring(0, 200)}...\n\n💡 This person contacted you via email but isn't registered as a student yet. You can:\n• Add them to your watchlist\n• Reply to their email\n• Invite them to join the platform`;
            }
            
            return `❌ **No candidate found matching "${nameQuery}"**\n\n🔍 **Search suggestions:**\n• Try full name: "John Smith"\n• Use email address\n• Check spelling\n• Search in emails: "find email from ${nameQuery}"\n\n📊 **Available candidates:** ${students.length} students in database`;
          }
        }
      }
      
      // Default intelligent response with current stats
      const totalStudents = analytics.total_students || 0;
      const activeStudents = analytics.active_students || 0;
      const totalEmails = analytics.total_emails || 0;
      const topSkill = analytics.top_skills?.[0]?.skill || 'various skills';
      
      return `I can help you with:\n\n🎯 **Candidate Analysis** - ${totalStudents} students, ${activeStudents} active learners\n📊 **Progress Insights** - Track learning and engagement patterns\n💼 **Job Strategy** - Top skill: ${topSkill}\n📧 **Email Management** - ${totalEmails} emails received\n\n**Try asking:**\n• "Find email from [name]"\n• "Who is [student name]?"\n• "Show top candidates"\n• "Analyze learning progress"\n\nWhat would you like to explore?`;

    } catch (error) {
      console.error('Chatbot error:', error);
      return "I'm currently unable to access the latest student data. Please ensure you're connected and try again. You can still ask me general recruitment questions!";
    }
  };

  const handleQuickAction = async (action) => {
    if (action === 'show_waitlist') {
      setShowWaitlist(!showWaitlist);
      return;
    }
    
    const actionMessages = {
      top_candidates: "Show me the top candidates based on learning progress",
      job_insights: "What job matching insights do you have?",
      progress_analysis: "Analyze student learning progress for me",
      recent_emails: "Show me recent emails and applications"
    };

    const message = actionMessages[action];
    if (message) {
      setInputMessage(message);
      setTimeout(() => handleSendMessage(), 100);
    }
  };

  return (
    <>
      {/* Chat Toggle Button */}
      <motion.button
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        onClick={() => setIsOpen(!isOpen)}
        style={{
          position: 'fixed',
          bottom: '24px',
          right: '24px',
          width: '60px',
          height: '60px',
          borderRadius: '50%',
          background: 'linear-gradient(135deg, #4f8cff, #6366f1)',
          border: 'none',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 8px 25px rgba(79, 140, 255, 0.4)',
          zIndex: 1000,
          color: 'white'
        }}
      >
        {isOpen ? <FiX size={24} /> : <FiMessageCircle size={24} />}
      </motion.button>

      {/* Waitlist Panel */}
      <AnimatePresence>
        {showWaitlist && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            style={{
              position: 'fixed',
              bottom: '100px',
              right: '450px',
              width: '300px',
              height: '400px',
              background: 'white',
              borderRadius: '16px',
              boxShadow: '0 20px 40px rgba(0,0,0,0.15)',
              border: '2px dashed #4f8cff',
              zIndex: 999,
              display: 'flex',
              flexDirection: 'column',
              overflow: 'hidden'
            }}
            onDragOver={handleDragOver}
            onDrop={handleDrop}
          >
            <div style={{
              padding: '16px',
              background: 'linear-gradient(135deg, #4f8cff, #6366f1)',
              color: 'white',
              borderRadius: '14px 14px 0 0'
            }}>
              <h3 style={{ margin: 0, fontSize: '16px', fontWeight: '600' }}>
                📋 Waitlisted Candidates ({waitlistedCandidates.length})
              </h3>
              <p style={{ margin: '4px 0 0', fontSize: '12px', opacity: 0.9 }}>
                Drag emails here to analyze
              </p>
            </div>
            
            <div style={{
              flex: 1,
              padding: '12px',
              overflowY: 'auto'
            }}>
              {waitlistedCandidates.length === 0 ? (
                <div style={{
                  textAlign: 'center',
                  padding: '40px 20px',
                  color: '#718096'
                }}>
                  <FiList size={32} style={{ marginBottom: '12px' }} />
                  <p style={{ margin: 0, fontSize: '14px' }}>
                    Drag emails from your inbox here to create a waitlist for detailed analysis
                  </p>
                </div>
              ) : (
                waitlistedCandidates.map((candidate, index) => (
                  <motion.div
                    key={candidate.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    style={{
                      padding: '12px',
                      border: '1px solid #e2e8f0',
                      borderRadius: '8px',
                      marginBottom: '8px',
                      background: '#f8fafc',
                      cursor: 'pointer'
                    }}
                    onClick={() => askAboutCandidate(candidate)}
                  >
                    <div style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'flex-start',
                      marginBottom: '6px'
                    }}>
                      <h4 style={{
                        margin: 0,
                        fontSize: '14px',
                        fontWeight: '600',
                        color: '#1a202c'
                      }}>
                        {candidate.name}
                      </h4>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          removeFromWaitlist(candidate.id);
                        }}
                        style={{
                          padding: '2px',
                          background: 'none',
                          border: 'none',
                          cursor: 'pointer',
                          color: '#e53e3e'
                        }}
                      >
                        <FiTrash2 size={12} />
                      </button>
                    </div>
                    <p style={{
                      margin: '0 0 4px',
                      fontSize: '12px',
                      color: '#718096',
                      lineHeight: '1.3'
                    }}>
                      {candidate.subject}
                    </p>
                    <p style={{
                      margin: 0,
                      fontSize: '11px',
                      color: '#a0aec0'
                    }}>
                      Added: {new Date(candidate.addedAt).toLocaleDateString()}
                    </p>
                  </motion.div>
                ))
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Chat Window */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.9 }}
            style={{
              position: 'fixed',
              bottom: '100px',
              right: '24px',
              width: '400px',
              height: '600px',
              background: 'white',
              borderRadius: '16px',
              boxShadow: '0 20px 40px rgba(0,0,0,0.15)',
              border: '1px solid #e2e8f0',
              zIndex: 1000,
              display: 'flex',
              flexDirection: 'column',
              overflow: 'hidden'
            }}
          >
            {/* Header */}
            <div style={{
              padding: '20px',
              background: 'linear-gradient(135deg, #4f8cff, #6366f1)',
              color: 'white',
              borderRadius: '16px 16px 0 0'
            }}>
              <h3 style={{ margin: 0, fontSize: '18px', fontWeight: '600' }}>
                AI Recruiting Assistant
              </h3>
              <p style={{ margin: '4px 0 0', fontSize: '14px', opacity: 0.9 }}>
                Student insights & recruitment help
              </p>
            </div>

            {/* Quick Actions */}
            <div style={{
              padding: '16px',
              borderBottom: '1px solid #e2e8f0',
              display: 'flex',
              gap: '8px',
              flexWrap: 'wrap'
            }}>
              {quickActions.map((action, index) => (
                <button
                  key={index}
                  onClick={() => handleQuickAction(action.action)}
                  style={{
                    padding: '8px 12px',
                    background: '#f8fafc',
                    border: '1px solid #e2e8f0',
                    borderRadius: '20px',
                    cursor: 'pointer',
                    fontSize: '12px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    color: '#4f8cff',
                    fontWeight: '500'
                  }}
                >
                  <action.icon size={12} />
                  {action.text}
                </button>
              ))}
            </div>

            {/* Messages */}
            <div style={{
              flex: 1,
              padding: '16px',
              overflowY: 'auto',
              display: 'flex',
              flexDirection: 'column',
              gap: '12px'
            }}>
              {messages.map((message) => (
                <div
                  key={message.id}
                  style={{
                    display: 'flex',
                    justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start'
                  }}
                >
                  <div
                    style={{
                      maxWidth: '80%',
                      padding: '12px 16px',
                      borderRadius: message.sender === 'user' ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
                      background: message.sender === 'user' 
                        ? 'linear-gradient(135deg, #4f8cff, #6366f1)' 
                        : '#f8fafc',
                      color: message.sender === 'user' ? 'white' : '#1a202c',
                      fontSize: '14px',
                      lineHeight: '1.4',
                      whiteSpace: 'pre-line'
                    }}
                  >
                    {message.text}
                  </div>
                </div>
              ))}
              
              {isTyping && (
                <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
                  <div style={{
                    padding: '12px 16px',
                    borderRadius: '16px 16px 16px 4px',
                    background: '#f8fafc',
                    color: '#718096',
                    fontSize: '14px'
                  }}>
                    AI is typing...
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div style={{
              padding: '16px',
              borderTop: '1px solid #e2e8f0',
              display: 'flex',
              gap: '8px'
            }}>
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder="Ask about candidates, skills, or recruitment..."
                style={{
                  flex: 1,
                  padding: '12px 16px',
                  border: '1px solid #e2e8f0',
                  borderRadius: '24px',
                  outline: 'none',
                  fontSize: '14px'
                }}
              />
              <button
                onClick={handleSendMessage}
                disabled={!inputMessage.trim()}
                style={{
                  padding: '12px',
                  background: inputMessage.trim() ? 'linear-gradient(135deg, #4f8cff, #6366f1)' : '#e2e8f0',
                  border: 'none',
                  borderRadius: '50%',
                  cursor: inputMessage.trim() ? 'pointer' : 'not-allowed',
                  color: 'white',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                <FiSend size={16} />
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default RecruiterChatbot;