import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { recruiterAuthenticatedFetch } from '../api';
import RecruiterLayout from './RecruiterLayout';
import { 
  FiUser, 
  FiMail, 
  FiCalendar, 
  FiTrendingUp, 
  FiAward, 
  FiLinkedin, 
  FiGithub, 
  FiTwitter,
  FiTarget,
  FiBook,
  FiClock,
  FiStar,
  FiArrowLeft,
  FiPhone,
  FiMapPin
} from 'react-icons/fi';

const RecruiterStudentProfile = () => {
  const { studentId } = useParams();
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadStudentProfile();
  }, [studentId]);

  const loadStudentProfile = async () => {
    try {
      setLoading(true);
      const data = await recruiterAuthenticatedFetch(`/recruiter/student/${studentId}/profile`);
      setProfile(data);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const getPerformanceColor = (score) => {
    if (score >= 80) return '#10b981';
    if (score >= 60) return '#f59e0b';
    return '#ef4444';
  };

  const getProgressColor = (progress) => {
    if (progress >= 70) return '#10b981';
    if (progress >= 30) return '#f59e0b';
    return '#6b7280';
  };

  if (loading) {
    return (
      <RecruiterLayout>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '60vh'
        }}>
          <div style={{
            width: '48px',
            height: '48px',
            border: '4px solid #e2e8f0',
            borderTop: '4px solid #4f8cff',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite'
          }} />
        </div>
      </RecruiterLayout>
    );
  }

  if (error) {
    return (
      <RecruiterLayout>
        <div style={{ padding: '40px', textAlign: 'center' }}>
          <div style={{
            background: '#fed7d7',
            color: '#c53030',
            padding: '20px',
            borderRadius: '12px',
            maxWidth: '500px',
            margin: '0 auto'
          }}>
            <h2>Error Loading Profile</h2>
            <p>{error}</p>
            <button
              onClick={() => navigate('/recruiter/dashboard')}
              style={{
                padding: '12px 24px',
                background: '#4f8cff',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer'
              }}
            >
              Back to Dashboard
            </button>
          </div>
        </div>
      </RecruiterLayout>
    );
  }

  return (
    <RecruiterLayout>
      {/* Header */}
      <div style={{
        background: 'white',
        borderBottom: '1px solid #e2e8f0',
        padding: '24px 32px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <button
            onClick={() => navigate('/recruiter/dashboard')}
            style={{
              padding: '8px',
              background: '#f7fafc',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            <FiArrowLeft size={20} color="#4a5568" />
          </button>
          <div>
            <h1 style={{
              fontSize: '28px',
              fontWeight: '700',
              color: '#1a202c',
              margin: '0 0 4px'
            }}>
              Student Profile
            </h1>
            <p style={{
              color: '#718096',
              margin: 0
            }}>
              Comprehensive candidate evaluation
            </p>
          </div>
        </div>
      </div>

      <div style={{ padding: '32px', maxWidth: '1200px', margin: '0 auto' }}>
        {/* Basic Info Card */}
        <div style={{
          background: 'white',
          borderRadius: '16px',
          padding: '32px',
          marginBottom: '24px',
          boxShadow: '0 4px 6px rgba(0,0,0,0.05)',
          border: '1px solid #e2e8f0'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '24px',
            marginBottom: '24px'
          }}>
            <div style={{
              width: '80px',
              height: '80px',
              borderRadius: '50%',
              background: profile.basic_info.picture 
                ? `url(${profile.basic_info.picture})` 
                : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              backgroundSize: 'cover',
              backgroundPosition: 'center',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              fontSize: '32px',
              fontWeight: '700'
            }}>
              {!profile.basic_info.picture && profile.basic_info.name.charAt(0).toUpperCase()}
            </div>
            <div style={{ flex: 1 }}>
              <h2 style={{
                fontSize: '24px',
                fontWeight: '700',
                color: '#1a202c',
                margin: '0 0 8px'
              }}>
                {profile.basic_info.name}
              </h2>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '16px',
                flexWrap: 'wrap'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <FiMail size={16} color="#718096" />
                  <span style={{ color: '#4a5568' }}>{profile.basic_info.email}</span>
                </div>
                {profile.basic_info.created_at && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <FiCalendar size={16} color="#718096" />
                    <span style={{ color: '#4a5568' }}>
                      Joined {new Date(profile.basic_info.created_at).toLocaleDateString()}
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Quick Stats */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
            gap: '16px'
          }}>
            <div style={{
              background: '#f8fafc',
              padding: '16px',
              borderRadius: '12px',
              textAlign: 'center'
            }}>
              <div style={{
                fontSize: '24px',
                fontWeight: '700',
                color: getPerformanceColor(profile.quiz_performance.average_score),
                marginBottom: '4px'
              }}>
                {profile.quiz_performance.average_score}%
              </div>
              <div style={{ fontSize: '14px', color: '#718096' }}>
                Average Score
              </div>
            </div>
            <div style={{
              background: '#f8fafc',
              padding: '16px',
              borderRadius: '12px',
              textAlign: 'center'
            }}>
              <div style={{
                fontSize: '24px',
                fontWeight: '700',
                color: getProgressColor(profile.learning_progress.progress_percentage),
                marginBottom: '4px'
              }}>
                {profile.learning_progress.progress_percentage}%
              </div>
              <div style={{ fontSize: '14px', color: '#718096' }}>
                Learning Progress
              </div>
            </div>
            <div style={{
              background: '#f8fafc',
              padding: '16px',
              borderRadius: '12px',
              textAlign: 'center'
            }}>
              <div style={{
                fontSize: '24px',
                fontWeight: '700',
                color: '#8b5cf6',
                marginBottom: '4px'
              }}>
                {profile.profile_summary.profile_completeness.social_connections}
              </div>
              <div style={{ fontSize: '14px', color: '#718096' }}>
                Social Connections
              </div>
            </div>
            <div style={{
              background: '#f8fafc',
              padding: '16px',
              borderRadius: '12px',
              textAlign: 'center'
            }}>
              <div style={{
                fontSize: '24px',
                fontWeight: '700',
                color: '#10b981',
                marginBottom: '4px'
              }}>
                {profile.profile_summary.profile_completeness.overall_score}%
              </div>
              <div style={{ fontSize: '14px', color: '#718096' }}>
                Profile Complete
              </div>
            </div>
          </div>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: '2fr 1fr',
          gap: '24px'
        }}>
          {/* Left Column */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {/* Onboarding Details */}
            <div style={{
              background: 'white',
              borderRadius: '16px',
              padding: '24px',
              boxShadow: '0 4px 6px rgba(0,0,0,0.05)',
              border: '1px solid #e2e8f0'
            }}>
              <h3 style={{
                fontSize: '20px',
                fontWeight: '600',
                color: '#1a202c',
                margin: '0 0 20px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                <FiUser size={20} color="#4f8cff" />
                Profile Information
              </h3>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div>
                  <label style={{
                    fontSize: '14px',
                    fontWeight: '600',
                    color: '#4a5568',
                    marginBottom: '4px',
                    display: 'block'
                  }}>
                    Career Goals
                  </label>
                  <p style={{
                    color: '#1a202c',
                    margin: 0,
                    lineHeight: '1.5'
                  }}>
                    {profile.onboarding_details.career_goals}
                  </p>
                </div>
                
                <div>
                  <label style={{
                    fontSize: '14px',
                    fontWeight: '600',
                    color: '#4a5568',
                    marginBottom: '4px',
                    display: 'block'
                  }}>
                    Current Skills
                  </label>
                  <p style={{
                    color: '#1a202c',
                    margin: 0,
                    lineHeight: '1.5'
                  }}>
                    {profile.onboarding_details.current_skills}
                  </p>
                </div>
                
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr',
                  gap: '16px'
                }}>
                  <div>
                    <label style={{
                      fontSize: '14px',
                      fontWeight: '600',
                      color: '#4a5568',
                      marginBottom: '4px',
                      display: 'block'
                    }}>
                      Grade Level
                    </label>
                    <p style={{
                      color: '#1a202c',
                      margin: 0
                    }}>
                      {profile.onboarding_details.grade}
                    </p>
                  </div>
                  
                  <div>
                    <label style={{
                      fontSize: '14px',
                      fontWeight: '600',
                      color: '#4a5568',
                      marginBottom: '4px',
                      display: 'block'
                    }}>
                      Time Commitment
                    </label>
                    <p style={{
                      color: '#1a202c',
                      margin: 0
                    }}>
                      {profile.onboarding_details.time_commitment}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Learning Progress */}
            <div style={{
              background: 'white',
              borderRadius: '16px',
              padding: '24px',
              boxShadow: '0 4px 6px rgba(0,0,0,0.05)',
              border: '1px solid #e2e8f0'
            }}>
              <h3 style={{
                fontSize: '20px',
                fontWeight: '600',
                color: '#1a202c',
                margin: '0 0 20px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                <FiBook size={20} color="#10b981" />
                Learning Progress
              </h3>
              
              <div style={{
                display: 'grid',
                gridTemplateColumns: '1fr 1fr',
                gap: '16px',
                marginBottom: '20px'
              }}>
                <div>
                  <label style={{
                    fontSize: '14px',
                    fontWeight: '600',
                    color: '#4a5568',
                    marginBottom: '4px',
                    display: 'block'
                  }}>
                    Learning Plan
                  </label>
                  <p style={{
                    color: '#1a202c',
                    margin: 0
                  }}>
                    {profile.learning_progress.plan_title}
                  </p>
                </div>
                
                <div>
                  <label style={{
                    fontSize: '14px',
                    fontWeight: '600',
                    color: '#4a5568',
                    marginBottom: '4px',
                    display: 'block'
                  }}>
                    Current Topic
                  </label>
                  <p style={{
                    color: '#1a202c',
                    margin: 0
                  }}>
                    {profile.learning_progress.current_topic}
                  </p>
                </div>
              </div>
              
              <div style={{
                background: '#f8fafc',
                padding: '16px',
                borderRadius: '12px'
              }}>
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: '8px'
                }}>
                  <span style={{ fontSize: '14px', fontWeight: '600', color: '#4a5568' }}>
                    Overall Progress
                  </span>
                  <span style={{
                    fontSize: '14px',
                    fontWeight: '600',
                    color: getProgressColor(profile.learning_progress.progress_percentage)
                  }}>
                    {profile.learning_progress.progress_percentage}%
                  </span>
                </div>
                <div style={{
                  width: '100%',
                  height: '8px',
                  background: '#e2e8f0',
                  borderRadius: '4px',
                  overflow: 'hidden'
                }}>
                  <div style={{
                    width: `${profile.learning_progress.progress_percentage}%`,
                    height: '100%',
                    background: getProgressColor(profile.learning_progress.progress_percentage),
                    transition: 'width 0.3s ease'
                  }} />
                </div>
              </div>
            </div>

            {/* Quiz Performance */}
            <div style={{
              background: 'white',
              borderRadius: '16px',
              padding: '24px',
              boxShadow: '0 4px 6px rgba(0,0,0,0.05)',
              border: '1px solid #e2e8f0'
            }}>
              <h3 style={{
                fontSize: '20px',
                fontWeight: '600',
                color: '#1a202c',
                margin: '0 0 20px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                <FiAward size={20} color="#f59e0b" />
                Quiz Performance
              </h3>
              
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
                gap: '16px',
                marginBottom: '20px'
              }}>
                <div style={{
                  background: '#f8fafc',
                  padding: '12px',
                  borderRadius: '8px',
                  textAlign: 'center'
                }}>
                  <div style={{
                    fontSize: '20px',
                    fontWeight: '700',
                    color: getPerformanceColor(profile.quiz_performance.average_score),
                    marginBottom: '4px'
                  }}>
                    {profile.quiz_performance.average_score}%
                  </div>
                  <div style={{ fontSize: '12px', color: '#718096' }}>
                    Average
                  </div>
                </div>
                
                <div style={{
                  background: '#f8fafc',
                  padding: '12px',
                  borderRadius: '8px',
                  textAlign: 'center'
                }}>
                  <div style={{
                    fontSize: '20px',
                    fontWeight: '700',
                    color: '#4f8cff',
                    marginBottom: '4px'
                  }}>
                    {profile.quiz_performance.total_quizzes}
                  </div>
                  <div style={{ fontSize: '12px', color: '#718096' }}>
                    Total Quizzes
                  </div>
                </div>
                
                <div style={{
                  background: '#f8fafc',
                  padding: '12px',
                  borderRadius: '8px',
                  textAlign: 'center'
                }}>
                  <div style={{
                    fontSize: '20px',
                    fontWeight: '700',
                    color: '#10b981',
                    marginBottom: '4px'
                  }}>
                    {profile.quiz_performance.pass_rate}%
                  </div>
                  <div style={{ fontSize: '12px', color: '#718096' }}>
                    Pass Rate
                  </div>
                </div>
              </div>
              
              <div style={{
                padding: '12px',
                background: getPerformanceColor(profile.quiz_performance.average_score) + '15',
                borderRadius: '8px',
                textAlign: 'center'
              }}>
                <span style={{
                  fontSize: '14px',
                  fontWeight: '600',
                  color: getPerformanceColor(profile.quiz_performance.average_score)
                }}>
                  {profile.quiz_performance.performance_level}
                </span>
              </div>
            </div>
          </div>

          {/* Right Column */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {/* Social Connections */}
            <div style={{
              background: 'white',
              borderRadius: '16px',
              padding: '24px',
              boxShadow: '0 4px 6px rgba(0,0,0,0.05)',
              border: '1px solid #e2e8f0'
            }}>
              <h3 style={{
                fontSize: '18px',
                fontWeight: '600',
                color: '#1a202c',
                margin: '0 0 20px'
              }}>
                Social Connections
              </h3>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {/* LinkedIn */}
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '12px',
                  background: profile.social_connections.linkedin.connected ? '#f0f9ff' : '#f8fafc',
                  borderRadius: '8px',
                  border: `1px solid ${profile.social_connections.linkedin.connected ? '#0ea5e9' : '#e2e8f0'}`
                }}>
                  <FiLinkedin size={20} color={profile.social_connections.linkedin.connected ? '#0ea5e9' : '#9ca3af'} />
                  <div style={{ flex: 1 }}>
                    <div style={{
                      fontSize: '14px',
                      fontWeight: '600',
                      color: profile.social_connections.linkedin.connected ? '#0ea5e9' : '#6b7280'
                    }}>
                      LinkedIn
                    </div>
                    <div style={{
                      fontSize: '12px',
                      color: '#718096'
                    }}>
                      {profile.social_connections.linkedin.connected 
                        ? profile.social_connections.linkedin.name || 'Connected'
                        : 'Not connected'
                      }
                    </div>
                  </div>
                  <div style={{
                    width: '8px',
                    height: '8px',
                    borderRadius: '50%',
                    background: profile.social_connections.linkedin.connected ? '#10b981' : '#e5e7eb'
                  }} />
                </div>

                {/* GitHub */}
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '12px',
                  background: profile.social_connections.github.connected ? '#f8fafc' : '#f8fafc',
                  borderRadius: '8px',
                  border: `1px solid ${profile.social_connections.github.connected ? '#6b7280' : '#e2e8f0'}`
                }}>
                  <FiGithub size={20} color={profile.social_connections.github.connected ? '#1f2937' : '#9ca3af'} />
                  <div style={{ flex: 1 }}>
                    <div style={{
                      fontSize: '14px',
                      fontWeight: '600',
                      color: profile.social_connections.github.connected ? '#1f2937' : '#6b7280'
                    }}>
                      GitHub
                    </div>
                    <div style={{
                      fontSize: '12px',
                      color: '#718096'
                    }}>
                      {profile.social_connections.github.connected 
                        ? `${profile.social_connections.github.repos_count} repositories`
                        : 'Not connected'
                      }
                    </div>
                  </div>
                  <div style={{
                    width: '8px',
                    height: '8px',
                    borderRadius: '50%',
                    background: profile.social_connections.github.connected ? '#10b981' : '#e5e7eb'
                  }} />
                </div>

                {/* Twitter */}
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '12px',
                  background: profile.social_connections.twitter.connected ? '#f0f9ff' : '#f8fafc',
                  borderRadius: '8px',
                  border: `1px solid ${profile.social_connections.twitter.connected ? '#1d9bf0' : '#e2e8f0'}`
                }}>
                  <FiTwitter size={20} color={profile.social_connections.twitter.connected ? '#1d9bf0' : '#9ca3af'} />
                  <div style={{ flex: 1 }}>
                    <div style={{
                      fontSize: '14px',
                      fontWeight: '600',
                      color: profile.social_connections.twitter.connected ? '#1d9bf0' : '#6b7280'
                    }}>
                      Twitter
                    </div>
                    <div style={{
                      fontSize: '12px',
                      color: '#718096'
                    }}>
                      {profile.social_connections.twitter.connected 
                        ? profile.social_connections.twitter.username || 'Connected'
                        : 'Not connected'
                      }
                    </div>
                  </div>
                  <div style={{
                    width: '8px',
                    height: '8px',
                    borderRadius: '50%',
                    background: profile.social_connections.twitter.connected ? '#10b981' : '#e5e7eb'
                  }} />
                </div>
              </div>
            </div>

            {/* Actions */}
            <div style={{
              background: 'white',
              borderRadius: '16px',
              padding: '24px',
              boxShadow: '0 4px 6px rgba(0,0,0,0.05)',
              border: '1px solid #e2e8f0'
            }}>
              <h3 style={{
                fontSize: '18px',
                fontWeight: '600',
                color: '#1a202c',
                margin: '0 0 20px'
              }}>
                Actions
              </h3>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <button
                  onClick={() => {
                    const subject = `Job Opportunity - ${profile.basic_info.name}`;
                    const body = `Hi ${profile.basic_info.name},\n\nI found your profile interesting and would like to discuss potential opportunities.\n\nBest regards`;
                    window.location.href = `mailto:${profile.basic_info.email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
                  }}
                  style={{
                    padding: '12px 16px',
                    background: '#4f8cff',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    fontSize: '14px',
                    fontWeight: '600',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '8px'
                  }}
                >
                  <FiMail size={16} />
                  Send Email
                </button>
                
                <button
                  onClick={() => {
                    alert(`Added ${profile.basic_info.name} to shortlist!`);
                  }}
                  style={{
                    padding: '12px 16px',
                    background: 'white',
                    color: '#f59e0b',
                    border: '2px solid #f59e0b',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    fontSize: '14px',
                    fontWeight: '600',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '8px'
                  }}
                >
                  <FiStar size={16} />
                  Add to Shortlist
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </RecruiterLayout>
  );
};

export default RecruiterStudentProfile;