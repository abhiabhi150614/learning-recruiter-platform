import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { recruiterAuthenticatedFetch, authenticatedFetch } from '../api';
import { motion } from 'framer-motion';
import { 
  FiArrowLeft, 
  FiUser, 
  FiMail, 
  FiLinkedin,
  FiCalendar,
  FiDownload,
  FiStar,
  FiTrendingUp,
  FiBookOpen,
  FiAward,
  FiClock,
  FiTarget,
  FiUsers,
  FiActivity,
  FiBarChart2
} from 'react-icons/fi';

const CandidateDetail = () => {
  const { userId } = useParams();
  const navigate = useNavigate();
  const [candidate, setCandidate] = useState(null);
  const [userProfile, setUserProfile] = useState(null);
  const [learningProgress, setLearningProgress] = useState(null);
  const [relatedCandidates, setRelatedCandidates] = useState([]);
  const [comprehensiveAnalytics, setComprehensiveAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('recruiter_token');
    if (!token) {
      navigate('/recruiter/login');
      return;
    }
    loadCandidateData();
  }, [userId, navigate]);

  const loadCandidateData = async () => {
    try {
      setLoading(true);
      
      // Load candidate match data
      const matches = await recruiterAuthenticatedFetch('/recruiter/match', {
        method: 'POST',
        body: JSON.stringify({ job_description: 'Software Developer' })
      });
      
      const candidateMatch = matches.find(m => m.user_id === parseInt(userId));
      setCandidate(candidateMatch);

      // Load related candidates
      try {
        const related = await recruiterAuthenticatedFetch(`/recruiter/related/${userId}`);
        setRelatedCandidates(related.neighbors || []);
      } catch (err) {
        console.log('No related candidates found');
      }

      // Try to load additional user data (this might fail if not accessible)
      try {
        const profile = await authenticatedFetch(`/users/${userId}/profile`);
        setUserProfile(profile);
      } catch (err) {
        console.log('User profile not accessible');
      }

      // Try to load learning progress
      try {
        const progress = await authenticatedFetch(`/learning-plan/${userId}`);
        setLearningProgress(progress);
      } catch (err) {
        console.log('Learning progress not accessible');
      }

      // Load comprehensive analytics
      try {
        const analytics = await recruiterAuthenticatedFetch(`/recruiter/analytics/user/${userId}`);
        setComprehensiveAnalytics(analytics);
      } catch (err) {
        console.log('Comprehensive analytics not available');
      }

    } catch (err) {
      console.error('Error loading candidate data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleComposioAction = async (action) => {
    try {
      setActionLoading(true);
      
      switch (action) {
        case 'email':
          await recruiterAuthenticatedFetch('/recruiter/composio/send-email', {
            method: 'POST',
            body: JSON.stringify({ 
              user_id: parseInt(userId),
              template: 'interview_invitation',
              personalized: true
            })
          });
          alert('Personalized email sent successfully!');
          break;
          
        case 'linkedin':
          await recruiterAuthenticatedFetch('/recruiter/composio/linkedin-enrich', {
            method: 'POST',
            body: JSON.stringify({ user_id: parseInt(userId) })
          });
          alert('LinkedIn profile enriched successfully!');
          break;
          
        case 'calendar':
          await recruiterAuthenticatedFetch('/recruiter/composio/schedule-interview', {
            method: 'POST',
            body: JSON.stringify({ 
              user_id: parseInt(userId),
              duration: 60,
              type: 'technical_interview'
            })
          });
          alert('Interview scheduled successfully!');
          break;
          
        case 'resume':
          await recruiterAuthenticatedFetch('/recruiter/composio/generate-resume', {
            method: 'POST',
            body: JSON.stringify({ user_id: parseInt(userId) })
          });
          alert('Resume generated and downloaded!');
          break;
          
        default:
          break;
      }
    } catch (err) {
      alert(`Action failed: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: '#f8fafc'
      }}>
        <div style={{
          width: '40px',
          height: '40px',
          border: '4px solid #e2e8f0',
          borderTop: '4px solid #4f8cff',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite'
        }} />
      </div>
    );
  }

  if (!candidate) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: '#f8fafc'
      }}>
        <div style={{ textAlign: 'center' }}>
          <h2>Candidate not found</h2>
          <button
            onClick={() => navigate('/recruiter/candidates')}
            style={{
              padding: '12px 24px',
              background: '#4f8cff',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer'
            }}
          >
            Back to Candidates
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: '#f8fafc'
    }}>
      {/* Header */}
      <div style={{
        background: 'white',
        borderBottom: '1px solid #e2e8f0',
        padding: '16px 24px'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <button
              onClick={() => navigate('/recruiter/candidates')}
              style={{
                padding: '8px',
                background: '#f7fafc',
                border: '1px solid #e2e8f0',
                borderRadius: '8px',
                cursor: 'pointer'
              }}
            >
              <FiArrowLeft size={20} color="#718096" />
            </button>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{
                width: '48px',
                height: '48px',
                background: 'linear-gradient(135deg, #4f8cff, #6366f1)',
                borderRadius: '12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontWeight: '700',
                fontSize: '18px'
              }}>
                {userId.slice(-2)}
              </div>
              <div>
                <h1 style={{
                  fontSize: '24px',
                  fontWeight: '700',
                  color: '#1a202c',
                  margin: 0
                }}>
                  Candidate #{userId}
                </h1>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginTop: '4px' }}>
                  <span style={{
                    padding: '4px 8px',
                    background: candidate.score > 0.7 ? '#d1fae5' : candidate.score > 0.5 ? '#fef3c7' : '#fee2e2',
                    color: candidate.score > 0.7 ? '#065f46' : candidate.score > 0.5 ? '#92400e' : '#991b1b',
                    borderRadius: '12px',
                    fontSize: '12px',
                    fontWeight: '600'
                  }}>
                    {(candidate.score * 100).toFixed(0)}% Match
                  </span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <FiTrendingUp size={14} color="#10b981" />
                    <span style={{ fontSize: '14px', color: '#10b981', fontWeight: '600' }}>
                      Active Learner
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div style={{ display: 'flex', gap: '12px' }}>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => handleComposioAction('email')}
              disabled={actionLoading}
              style={{
                padding: '10px 16px',
                background: '#10b981',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontWeight: '600',
                cursor: actionLoading ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}
            >
              <FiMail size={16} />
              Send Email
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => handleComposioAction('linkedin')}
              disabled={actionLoading}
              style={{
                padding: '10px 16px',
                background: '#0077b5',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontWeight: '600',
                cursor: actionLoading ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}
            >
              <FiLinkedin size={16} />
              LinkedIn
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => handleComposioAction('calendar')}
              disabled={actionLoading}
              style={{
                padding: '10px 16px',
                background: '#8b5cf6',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontWeight: '600',
                cursor: actionLoading ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}
            >
              <FiCalendar size={16} />
              Schedule
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => handleComposioAction('resume')}
              disabled={actionLoading}
              style={{
                padding: '10px 16px',
                background: '#f59e0b',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontWeight: '600',
                cursor: actionLoading ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}
            >
              <FiDownload size={16} />
              Resume
            </motion.button>
          </div>
        </div>
      </div>

      <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: '2fr 1fr',
          gap: '24px'
        }}>
          {/* Main Content */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {/* Summary Card */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              style={{
                background: 'white',
                borderRadius: '12px',
                padding: '24px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                border: '1px solid #e2e8f0'
              }}
            >
              <h2 style={{
                fontSize: '18px',
                fontWeight: '600',
                color: '#1a202c',
                marginBottom: '16px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                <FiUser size={20} />
                Candidate Summary
              </h2>
              
              <p style={{
                color: '#4a5568',
                fontSize: '16px',
                lineHeight: '1.6',
                margin: 0
              }}>
                {candidate.summary || 'No summary available for this candidate.'}
              </p>
            </motion.div>

            {/* Skills & Expertise */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              style={{
                background: 'white',
                borderRadius: '12px',
                padding: '24px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                border: '1px solid #e2e8f0'
              }}
            >
              <h2 style={{
                fontSize: '18px',
                fontWeight: '600',
                color: '#1a202c',
                marginBottom: '16px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                <FiTarget size={20} />
                Skills & Expertise
              </h2>
              
              <div style={{
                display: 'flex',
                flexWrap: 'wrap',
                gap: '8px'
              }}>
                {(candidate.skills_tags || []).map((skill, index) => (
                  <span
                    key={index}
                    style={{
                      padding: '8px 16px',
                      background: 'linear-gradient(135deg, #e0f2fe, #f0f9ff)',
                      color: '#0369a1',
                      borderRadius: '20px',
                      fontSize: '14px',
                      fontWeight: '600',
                      border: '1px solid #bae6fd'
                    }}
                  >
                    {skill}
                  </span>
                ))}
                {(candidate.skills_tags || []).length === 0 && (
                  <p style={{ color: '#718096', fontStyle: 'italic' }}>
                    No skills data available
                  </p>
                )}
              </div>
            </motion.div>

            {/* Comprehensive Learning Analytics */}
            {comprehensiveAnalytics && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                style={{
                  background: 'white',
                  borderRadius: '12px',
                  padding: '24px',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                  border: '1px solid #e2e8f0'
                }}
              >
                <h2 style={{
                  fontSize: '18px',
                  fontWeight: '600',
                  color: '#1a202c',
                  marginBottom: '16px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  <FiBookOpen size={20} />
                  Learning Analytics
                </h2>
                
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
                  gap: '16px',
                  marginBottom: '20px'
                }}>
                  <div style={{
                    padding: '16px',
                    background: '#f0f9ff',
                    borderRadius: '8px',
                    textAlign: 'center'
                  }}>
                    <FiActivity size={24} color="#4f8cff" style={{ marginBottom: '8px' }} />
                    <p style={{ fontSize: '20px', fontWeight: '700', color: '#1a202c', margin: '0 0 4px' }}>
                      {comprehensiveAnalytics.learning_metrics?.current_streak || 0}
                    </p>
                    <p style={{ fontSize: '12px', color: '#718096', margin: 0 }}>
                      Day Streak
                    </p>
                  </div>
                  
                  <div style={{
                    padding: '16px',
                    background: '#f0fdf4',
                    borderRadius: '8px',
                    textAlign: 'center'
                  }}>
                    <FiTrendingUp size={24} color="#10b981" style={{ marginBottom: '8px' }} />
                    <p style={{ fontSize: '20px', fontWeight: '700', color: '#1a202c', margin: '0 0 4px' }}>
                      {(comprehensiveAnalytics.learning_metrics?.avg_score * 100 || 0).toFixed(0)}%
                    </p>
                    <p style={{ fontSize: '12px', color: '#718096', margin: 0 }}>
                      Avg Quiz Score
                    </p>
                  </div>
                  
                  <div style={{
                    padding: '16px',
                    background: '#fefce8',
                    borderRadius: '8px',
                    textAlign: 'center'
                  }}>
                    <FiBarChart2 size={24} color="#f59e0b" style={{ marginBottom: '8px' }} />
                    <p style={{ fontSize: '20px', fontWeight: '700', color: '#1a202c', margin: '0 0 4px' }}>
                      {comprehensiveAnalytics.learning_metrics?.total_quizzes || 0}
                    </p>
                    <p style={{ fontSize: '12px', color: '#718096', margin: 0 }}>
                      Quizzes Taken
                    </p>
                  </div>
                  
                  <div style={{
                    padding: '16px',
                    background: '#fdf2f8',
                    borderRadius: '8px',
                    textAlign: 'center'
                  }}>
                    <FiTarget size={24} color="#ec4899" style={{ marginBottom: '8px' }} />
                    <p style={{ fontSize: '20px', fontWeight: '700', color: '#1a202c', margin: '0 0 4px' }}>
                      {comprehensiveAnalytics.learning_metrics?.performance_trend || 'Stable'}
                    </p>
                    <p style={{ fontSize: '12px', color: '#718096', margin: 0 }}>
                      Trend
                    </p>
                  </div>
                </div>

                {/* Learning Recommendations */}
                {comprehensiveAnalytics.recommendations && comprehensiveAnalytics.recommendations.length > 0 && (
                  <div style={{ marginBottom: '20px' }}>
                    <h4 style={{ color: '#2d3748', marginBottom: '12px', fontSize: '16px' }}>Learning Recommendations</h4>
                    <ul style={{ paddingLeft: '16px', color: '#4a5568' }}>
                      {comprehensiveAnalytics.recommendations.map((rec, i) => (
                        <li key={i} style={{ marginBottom: '4px', fontSize: '14px' }}>
                          {rec}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Skill Progression */}
                {comprehensiveAnalytics.skill_progression && comprehensiveAnalytics.skill_progression.length > 0 && (
                  <div>
                    <h4 style={{ color: '#2d3748', marginBottom: '12px', fontSize: '16px' }}>Skill Progression</h4>
                    <div style={{ display: 'flex', gap: '8px', overflowX: 'auto', paddingBottom: '8px' }}>
                      {comprehensiveAnalytics.skill_progression.slice(-6).map((month, i) => (
                        <div
                          key={i}
                          style={{
                            minWidth: '120px',
                            padding: '12px',
                            background: month.status === 'completed' ? '#d1fae5' : '#fef3c7',
                            borderRadius: '8px',
                            textAlign: 'center'
                          }}
                        >
                          <p style={{ fontSize: '14px', fontWeight: '600', margin: '0 0 4px' }}>
                            Month {month.month}
                          </p>
                          <p style={{ fontSize: '12px', color: '#6b7280', margin: '0 0 4px' }}>
                            {month.topics_count} topics
                          </p>
                          <span style={{
                            fontSize: '10px',
                            padding: '2px 6px',
                            borderRadius: '10px',
                            background: month.status === 'completed' ? '#065f46' : '#92400e',
                            color: 'white'
                          }}>
                            {month.status}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </motion.div>
            )}

            {/* Fallback Learning Progress */}
            {!comprehensiveAnalytics && learningProgress && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                style={{
                  background: 'white',
                  borderRadius: '12px',
                  padding: '24px',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                  border: '1px solid #e2e8f0'
                }}
              >
                <h2 style={{
                  fontSize: '18px',
                  fontWeight: '600',
                  color: '#1a202c',
                  marginBottom: '16px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  <FiBookOpen size={20} />
                  Learning Progress
                </h2>
                
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                  gap: '16px'
                }}>
                  <div style={{
                    padding: '16px',
                    background: '#f8fafc',
                    borderRadius: '8px',
                    textAlign: 'center'
                  }}>
                    <FiActivity size={24} color="#4f8cff" style={{ marginBottom: '8px' }} />
                    <p style={{ fontSize: '24px', fontWeight: '700', color: '#1a202c', margin: '0 0 4px' }}>
                      {learningProgress.completed_months || 0}
                    </p>
                    <p style={{ fontSize: '14px', color: '#718096', margin: 0 }}>
                      Months Completed
                    </p>
                  </div>
                  
                  <div style={{
                    padding: '16px',
                    background: '#f8fafc',
                    borderRadius: '8px',
                    textAlign: 'center'
                  }}>
                    <FiBarChart2 size={24} color="#10b981" style={{ marginBottom: '8px' }} />
                    <p style={{ fontSize: '24px', fontWeight: '700', color: '#1a202c', margin: '0 0 4px' }}>
                      {learningProgress.progress_percentage || 0}%
                    </p>
                    <p style={{ fontSize: '14px', color: '#718096', margin: 0 }}>
                      Overall Progress
                    </p>
                  </div>
                </div>
              </motion.div>
            )}

            {/* Match Analysis */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              style={{
                background: 'white',
                borderRadius: '12px',
                padding: '24px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                border: '1px solid #e2e8f0'
              }}
            >
              <h2 style={{
                fontSize: '18px',
                fontWeight: '600',
                color: '#1a202c',
                marginBottom: '16px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                <FiAward size={20} />
                Match Analysis
              </h2>
              
              <div style={{
                padding: '16px',
                background: candidate.score > 0.7 ? '#d1fae5' : candidate.score > 0.5 ? '#fef3c7' : '#fee2e2',
                borderRadius: '8px',
                marginBottom: '16px'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                  <FiStar size={20} color={candidate.score > 0.7 ? '#065f46' : candidate.score > 0.5 ? '#92400e' : '#991b1b'} />
                  <span style={{
                    fontSize: '18px',
                    fontWeight: '700',
                    color: candidate.score > 0.7 ? '#065f46' : candidate.score > 0.5 ? '#92400e' : '#991b1b'
                  }}>
                    {(candidate.score * 100).toFixed(1)}% Match Score
                  </span>
                </div>
                <p style={{
                  color: candidate.score > 0.7 ? '#065f46' : candidate.score > 0.5 ? '#92400e' : '#991b1b',
                  fontSize: '14px',
                  margin: 0
                }}>
                  {candidate.match_explanation || 'AI-powered matching based on skills, experience, and learning progress'}
                </p>
              </div>

              <div style={{
                display: 'grid',
                gridTemplateColumns: '1fr 1fr',
                gap: '16px'
              }}>
                <div>
                  <h4 style={{ color: '#2d3748', marginBottom: '8px' }}>Strengths</h4>
                  <ul style={{ color: '#4a5568', fontSize: '14px', paddingLeft: '16px' }}>
                    <li>Strong technical skills match</li>
                    <li>Active learning engagement</li>
                    <li>Relevant project experience</li>
                  </ul>
                </div>
                <div>
                  <h4 style={{ color: '#2d3748', marginBottom: '8px' }}>Growth Areas</h4>
                  <ul style={{ color: '#4a5568', fontSize: '14px', paddingLeft: '16px' }}>
                    <li>Could benefit from advanced training</li>
                    <li>Potential for leadership development</li>
                    <li>Industry-specific knowledge</li>
                  </ul>
                </div>
              </div>
            </motion.div>
          </div>

          {/* Sidebar */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {/* Quick Stats */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              style={{
                background: 'white',
                borderRadius: '12px',
                padding: '20px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                border: '1px solid #e2e8f0'
              }}
            >
              <h3 style={{
                fontSize: '16px',
                fontWeight: '600',
                color: '#1a202c',
                marginBottom: '16px'
              }}>
                Quick Stats
              </h3>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ color: '#718096', fontSize: '14px' }}>User ID</span>
                  <span style={{ fontWeight: '600', color: '#1a202c' }}>#{userId}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ color: '#718096', fontSize: '14px' }}>Match Score</span>
                  <span style={{ fontWeight: '600', color: '#1a202c' }}>
                    {(candidate.score * 100).toFixed(0)}%
                  </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ color: '#718096', fontSize: '14px' }}>Skills Count</span>
                  <span style={{ fontWeight: '600', color: '#1a202c' }}>
                    {(candidate.skills_tags || []).length}
                  </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ color: '#718096', fontSize: '14px' }}>Status</span>
                  <span style={{
                    padding: '2px 8px',
                    background: '#d1fae5',
                    color: '#065f46',
                    borderRadius: '12px',
                    fontSize: '12px',
                    fontWeight: '600'
                  }}>
                    Active
                  </span>
                </div>
              </div>
            </motion.div>

            {/* Related Candidates */}
            {relatedCandidates.length > 0 && (
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1 }}
                style={{
                  background: 'white',
                  borderRadius: '12px',
                  padding: '20px',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                  border: '1px solid #e2e8f0'
                }}
              >
                <h3 style={{
                  fontSize: '16px',
                  fontWeight: '600',
                  color: '#1a202c',
                  marginBottom: '16px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  <FiUsers size={16} />
                  Similar Candidates
                </h3>
                
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {relatedCandidates.slice(0, 5).map((relatedId, index) => (
                    <button
                      key={relatedId}
                      onClick={() => navigate(`/recruiter/candidate/${relatedId}`)}
                      style={{
                        padding: '12px',
                        background: '#f8fafc',
                        border: '1px solid #e2e8f0',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        textAlign: 'left',
                        transition: 'all 0.3s ease'
                      }}
                      onMouseEnter={(e) => {
                        e.target.style.background = '#f1f5f9';
                        e.target.style.borderColor = '#cbd5e1';
                      }}
                      onMouseLeave={(e) => {
                        e.target.style.background = '#f8fafc';
                        e.target.style.borderColor = '#e2e8f0';
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <div style={{
                          width: '24px',
                          height: '24px',
                          background: '#4f8cff',
                          borderRadius: '6px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          color: 'white',
                          fontSize: '12px',
                          fontWeight: '600'
                        }}>
                          {relatedId.toString().slice(-2)}
                        </div>
                        <span style={{ fontWeight: '600', color: '#1a202c' }}>
                          Candidate #{relatedId}
                        </span>
                      </div>
                    </button>
                  ))}
                </div>
              </motion.div>
            )}

            {/* AI Insights */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              style={{
                background: 'linear-gradient(135deg, #667eea, #764ba2)',
                borderRadius: '12px',
                padding: '20px',
                color: 'white'
              }}
            >
              <h3 style={{
                fontSize: '16px',
                fontWeight: '600',
                marginBottom: '12px',
                color: 'white'
              }}>
                AI Insights
              </h3>
              
              <div style={{ fontSize: '14px', lineHeight: '1.5' }}>
                {comprehensiveAnalytics?.career_readiness ? (
                  <>
                    <p style={{ margin: '0 0 8px' }}>
                      🎯 <strong>Career Level:</strong> {comprehensiveAnalytics.career_readiness.level}
                    </p>
                    <p style={{ margin: '0 0 8px' }}>
                      📈 <strong>Readiness Score:</strong> {(comprehensiveAnalytics.career_readiness.overall_score * 100).toFixed(0)}%
                    </p>
                    <p style={{ margin: '0 0 8px' }}>
                      🤝 <strong>Learning Trend:</strong> {comprehensiveAnalytics.learning_metrics?.performance_trend || 'Stable'}
                    </p>
                    <p style={{ margin: 0 }}>
                      ⚡ <strong>Recommendation:</strong> {comprehensiveAnalytics.career_readiness.description}
                    </p>
                  </>
                ) : (
                  <>
                    <p style={{ margin: '0 0 8px' }}>
                      🎯 <strong>Best fit for:</strong> Mid-level technical roles
                    </p>
                    <p style={{ margin: '0 0 8px' }}>
                      📈 <strong>Growth potential:</strong> High learning velocity
                    </p>
                    <p style={{ margin: '0 0 8px' }}>
                      🤝 <strong>Team fit:</strong> Collaborative learner
                    </p>
                    <p style={{ margin: 0 }}>
                      ⚡ <strong>Recommendation:</strong> Fast-track interview
                    </p>
                  </>
                )}
              </div>
            </motion.div>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default CandidateDetail;