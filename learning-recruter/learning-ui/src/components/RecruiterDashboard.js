import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { recruiterAuthenticatedFetch } from '../api';
import { motion, AnimatePresence } from 'framer-motion';
import RecruiterLayout from './RecruiterLayout';
import { 
  FiUsers, 
  FiBriefcase, 
  FiTrendingUp, 
  FiMail, 
  FiSearch,
  FiPlus,
  FiEye,
  FiStar,
  FiLinkedin,
  FiGithub,
  FiTwitter,
  FiAward,
  FiClock,
  FiTarget,
  FiMessageSquare
} from 'react-icons/fi';

const RecruiterDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('top_performers');
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('recruiter_token');
    if (!token) {
      navigate('/recruiter/login');
      return;
    }
    loadDashboard();
  }, [navigate]);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      const data = await recruiterAuthenticatedFetch('/recruiter/dashboard');
      setDashboardData(data);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const getCategoryIcon = (category) => {
    const icons = {
      top_performers: FiAward,
      active_learners: FiTrendingUp,
      social_connected: FiUsers,
      recent_joiners: FiClock
    };
    return icons[category] || FiUsers;
  };

  const getCategoryColor = (category) => {
    const colors = {
      top_performers: '#f59e0b',
      active_learners: '#10b981',
      social_connected: '#8b5cf6',
      recent_joiners: '#4f8cff'
    };
    return colors[category] || '#4f8cff';
  };

  const getCategoryTitle = (category) => {
    const titles = {
      top_performers: 'Top Performers',
      active_learners: 'Active Learners',
      social_connected: 'Social Connected',
      recent_joiners: 'Recent Joiners'
    };
    return titles[category] || 'Students';
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
          textAlign: 'center'
        }}>
          <div style={{
            width: '48px',
            height: '48px',
            border: '4px solid #e2e8f0',
            borderTop: '4px solid #4f8cff',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 16px'
          }} />
          <p style={{ color: '#718096', fontSize: '16px' }}>Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <RecruiterLayout>
        <div style={{
          padding: '40px',
          textAlign: 'center'
        }}>
          <div style={{
            background: '#fed7d7',
            color: '#c53030',
            padding: '20px',
            borderRadius: '12px',
            maxWidth: '500px',
            margin: '0 auto'
          }}>
            <h2>Error Loading Dashboard</h2>
            <p>{error}</p>
            <button
              onClick={loadDashboard}
              style={{
                padding: '12px 24px',
                background: '#4f8cff',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                marginTop: '16px'
              }}
            >
              Retry
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
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        padding: '40px 32px'
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <h1 style={{
            fontSize: '36px',
            fontWeight: '700',
            margin: '0 0 12px',
            textShadow: '0 2px 4px rgba(0,0,0,0.1)'
          }}>
            Recruiter Dashboard
          </h1>
          <p style={{
            fontSize: '18px',
            opacity: 0.9,
            margin: 0
          }}>
            Find, evaluate, and connect with top talent
          </p>
        </div>
      </div>

      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '32px' }}>
        {/* Overview Stats */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '20px',
          marginBottom: '40px'
        }}>
          {[
            { 
              icon: FiUsers, 
              label: 'Total Students', 
              value: dashboardData.overview.total_students, 
              color: '#4f8cff',
              description: 'Available candidates'
            },
            { 
              icon: FiAward, 
              label: 'Top Performers', 
              value: dashboardData.overview.top_performers, 
              color: '#f59e0b',
              description: '75+ avg score'
            },
            { 
              icon: FiTrendingUp, 
              label: 'Active Learners', 
              value: dashboardData.overview.active_learners, 
              color: '#10b981',
              description: '20+ progress'
            },
            { 
              icon: FiUsers, 
              label: 'Social Connected', 
              value: dashboardData.overview.social_connected, 
              color: '#8b5cf6',
              description: '2+ platforms'
            }
          ].map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              style={{
                background: 'white',
                padding: '24px',
                borderRadius: '16px',
                boxShadow: '0 4px 6px rgba(0,0,0,0.05)',
                border: '1px solid #e2e8f0',
                textAlign: 'center'
              }}
            >
              <div style={{
                width: '56px',
                height: '56px',
                background: `${stat.color}15`,
                borderRadius: '16px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 16px'
              }}>
                <stat.icon size={28} color={stat.color} />
              </div>
              <h3 style={{
                fontSize: '32px',
                fontWeight: '700',
                color: '#1a202c',
                margin: '0 0 8px'
              }}>
                {stat.value}
              </h3>
              <p style={{
                fontSize: '16px',
                fontWeight: '600',
                color: '#1a202c',
                margin: '0 0 4px'
              }}>
                {stat.label}
              </p>
              <p style={{
                fontSize: '14px',
                color: '#718096',
                margin: 0
              }}>
                {stat.description}
              </p>
            </motion.div>
          ))}
        </div>

        {/* Quick Actions */}
        <div style={{
          background: 'white',
          borderRadius: '20px',
          padding: '32px',
          marginBottom: '40px',
          boxShadow: '0 8px 25px rgba(0,0,0,0.08)',
          border: '1px solid #e2e8f0'
        }}>
          <h2 style={{
            fontSize: '24px',
            fontWeight: '700',
            color: '#1a202c',
            margin: '0 0 24px',
            textAlign: 'center'
          }}>
            Quick Actions
          </h2>
          
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '20px'
          }}>
            {[
              { 
                icon: FiPlus, 
                label: 'Post New Job', 
                action: () => navigate('/recruiter/post-job'), 
                color: '#4f8cff',
                description: 'Create job posting and find matches',
                primary: true
              },
              { 
                icon: FiSearch, 
                label: 'Search Students', 
                action: () => navigate('/recruiter/students/search'), 
                color: '#10b981',
                description: 'Advanced filtering and search'
              },
              { 
                icon: FiTarget, 
                label: 'AI Matching', 
                action: () => navigate('/recruiter/match'), 
                color: '#f59e0b',
                description: 'Smart candidate-job matching'
              },
              { 
                icon: FiMessageSquare, 
                label: 'AI Assistant', 
                action: () => navigate('/recruiter/chat'), 
                color: '#8b5cf6',
                description: 'Get recruitment insights'
              },
              { 
                icon: FiClock, 
                label: 'Interviews', 
                action: () => navigate('/recruiter/interviews'), 
                color: '#e53e3e',
                description: 'Manage scheduled interviews'
              }
            ].map((action, index) => (
              <motion.button
                key={action.label}
                whileHover={{ scale: 1.05, y: -4 }}
                whileTap={{ scale: 0.95 }}
                onClick={action.action}
                style={{
                  padding: '24px',
                  background: action.primary 
                    ? `linear-gradient(135deg, ${action.color}, #6366f1)` 
                    : 'white',
                  border: action.primary ? 'none' : `2px solid ${action.color}20`,
                  borderRadius: '16px',
                  cursor: 'pointer',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: '16px',
                  transition: 'all 0.3s ease',
                  textAlign: 'center',
                  boxShadow: action.primary 
                    ? '0 8px 25px rgba(79, 140, 255, 0.3)' 
                    : '0 4px 6px rgba(0,0,0,0.05)'
                }}
              >
                <div style={{
                  width: '56px',
                  height: '56px',
                  background: action.primary ? 'rgba(255,255,255,0.2)' : `${action.color}15`,
                  borderRadius: '16px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  <action.icon size={28} color={action.primary ? 'white' : action.color} />
                </div>
                
                <div>
                  <h3 style={{
                    fontSize: '18px',
                    fontWeight: '600',
                    color: action.primary ? 'white' : '#1a202c',
                    margin: '0 0 8px'
                  }}>
                    {action.label}
                  </h3>
                  <p style={{
                    fontSize: '14px',
                    color: action.primary ? 'rgba(255,255,255,0.8)' : '#718096',
                    margin: 0,
                    lineHeight: '1.4'
                  }}>
                    {action.description}
                  </p>
                </div>
              </motion.button>
            ))}
          </div>
        </div>

        {/* Student Categories */}
        <div style={{
          background: 'white',
          borderRadius: '20px',
          padding: '32px',
          boxShadow: '0 8px 25px rgba(0,0,0,0.08)',
          border: '1px solid #e2e8f0'
        }}>
          <h2 style={{
            fontSize: '24px',
            fontWeight: '700',
            color: '#1a202c',
            margin: '0 0 24px',
            textAlign: 'center'
          }}>
            Student Categories
          </h2>

          {/* Category Tabs */}
          <div style={{
            display: 'flex',
            gap: '8px',
            marginBottom: '32px',
            background: '#f8fafc',
            padding: '8px',
            borderRadius: '12px',
            flexWrap: 'wrap',
            justifyContent: 'center'
          }}>
            {Object.keys(dashboardData.categories).map((category) => {
              const Icon = getCategoryIcon(category);
              const isActive = selectedCategory === category;
              
              return (
                <button
                  key={category}
                  onClick={() => setSelectedCategory(category)}
                  style={{
                    padding: '12px 20px',
                    background: isActive ? 'white' : 'transparent',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    fontSize: '14px',
                    fontWeight: '600',
                    color: isActive ? getCategoryColor(category) : '#718096',
                    transition: 'all 0.3s ease',
                    boxShadow: isActive ? '0 2px 4px rgba(0,0,0,0.1)' : 'none'
                  }}
                >
                  <Icon size={16} />
                  {getCategoryTitle(category)}
                  <span style={{
                    background: isActive ? `${getCategoryColor(category)}20` : '#e2e8f0',
                    color: isActive ? getCategoryColor(category) : '#718096',
                    padding: '2px 8px',
                    borderRadius: '12px',
                    fontSize: '12px',
                    fontWeight: '600'
                  }}>
                    {dashboardData.categories[category].length}
                  </span>
                </button>
              );
            })}
          </div>

          {/* Selected Category Students */}
          <AnimatePresence mode="wait">
            <motion.div
              key={selectedCategory}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
                gap: '20px'
              }}>
                {dashboardData.categories[selectedCategory].map((student, index) => (
                  <motion.div
                    key={student.id}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.1 }}
                    style={{
                      background: '#f8fafc',
                      border: '1px solid #e2e8f0',
                      borderRadius: '16px',
                      padding: '20px',
                      transition: 'all 0.3s ease'
                    }}
                    whileHover={{ 
                      scale: 1.02, 
                      boxShadow: '0 8px 25px rgba(0,0,0,0.1)',
                      borderColor: getCategoryColor(selectedCategory)
                    }}
                  >
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px',
                      marginBottom: '16px'
                    }}>
                      <div style={{
                        width: '48px',
                        height: '48px',
                        borderRadius: '50%',
                        background: student.picture 
                          ? `url(${student.picture})` 
                          : `linear-gradient(135deg, ${getCategoryColor(selectedCategory)}, #6366f1)`,
                        backgroundSize: 'cover',
                        backgroundPosition: 'center',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: 'white',
                        fontWeight: '600',
                        fontSize: '18px'
                      }}>
                        {!student.picture && student.name.charAt(0).toUpperCase()}
                      </div>
                      <div style={{ flex: 1 }}>
                        <h3 style={{
                          fontSize: '16px',
                          fontWeight: '600',
                          color: '#1a202c',
                          margin: '0 0 4px'
                        }}>
                          {student.name}
                        </h3>
                        <p style={{
                          fontSize: '14px',
                          color: '#718096',
                          margin: 0
                        }}>
                          {student.email}
                        </p>
                      </div>
                    </div>

                    <div style={{
                      display: 'flex',
                      gap: '12px',
                      marginBottom: '16px'
                    }}>
                      <div style={{
                        background: 'white',
                        padding: '8px 12px',
                        borderRadius: '8px',
                        textAlign: 'center',
                        flex: 1
                      }}>
                        <p style={{
                          fontSize: '18px',
                          fontWeight: '700',
                          color: getCategoryColor(selectedCategory),
                          margin: '0 0 4px'
                        }}>
                          {student.avg_score}%
                        </p>
                        <p style={{
                          fontSize: '12px',
                          color: '#718096',
                          margin: 0
                        }}>
                          Avg Score
                        </p>
                      </div>
                      <div style={{
                        background: 'white',
                        padding: '8px 12px',
                        borderRadius: '8px',
                        textAlign: 'center',
                        flex: 1
                      }}>
                        <p style={{
                          fontSize: '18px',
                          fontWeight: '700',
                          color: getCategoryColor(selectedCategory),
                          margin: '0 0 4px'
                        }}>
                          {student.learning_progress}%
                        </p>
                        <p style={{
                          fontSize: '12px',
                          color: '#718096',
                          margin: 0
                        }}>
                          Progress
                        </p>
                      </div>
                      <div style={{
                        background: 'white',
                        padding: '8px 12px',
                        borderRadius: '8px',
                        textAlign: 'center',
                        flex: 1
                      }}>
                        <p style={{
                          fontSize: '18px',
                          fontWeight: '700',
                          color: getCategoryColor(selectedCategory),
                          margin: '0 0 4px'
                        }}>
                          {student.social_connections}
                        </p>
                        <p style={{
                          fontSize: '12px',
                          color: '#718096',
                          margin: 0
                        }}>
                          Social
                        </p>
                      </div>
                    </div>

                    <p style={{
                      fontSize: '14px',
                      color: '#4a5568',
                      margin: '0 0 16px',
                      lineHeight: '1.4',
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical',
                      overflow: 'hidden'
                    }}>
                      {student.career_goals}
                    </p>

                    <div style={{
                      display: 'flex',
                      gap: '8px',
                      justifyContent: 'space-between'
                    }}>
                      <button
                        onClick={() => navigate(`/recruiter/student-profile/${student.id}`)}
                        style={{
                          flex: 1,
                          padding: '10px',
                          background: getCategoryColor(selectedCategory),
                          color: 'white',
                          border: 'none',
                          borderRadius: '8px',
                          cursor: 'pointer',
                          fontSize: '14px',
                          fontWeight: '600',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          gap: '6px'
                        }}
                      >
                        <FiEye size={16} />
                        View Profile
                      </button>
                      <button
                        onClick={() => {
                          // Add to shortlist or contact
                          alert(`Added ${student.name} to shortlist!`);
                        }}
                        style={{
                          padding: '10px',
                          background: 'white',
                          border: `2px solid ${getCategoryColor(selectedCategory)}`,
                          borderRadius: '8px',
                          cursor: 'pointer',
                          color: getCategoryColor(selectedCategory)
                        }}
                      >
                        <FiStar size={16} />
                      </button>
                    </div>
                  </motion.div>
                ))}
              </div>

              {dashboardData.categories[selectedCategory].length === 0 && (
                <div style={{
                  textAlign: 'center',
                  padding: '60px 20px',
                  color: '#718096'
                }}>
                  <div style={{
                    width: '64px',
                    height: '64px',
                    background: '#f7fafc',
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto 16px'
                  }}>
                    <FiUsers size={32} color="#cbd5e0" />
                  </div>
                  <h3 style={{ margin: '0 0 8px', fontSize: '18px' }}>
                    No {getCategoryTitle(selectedCategory).toLowerCase()} found
                  </h3>
                  <p style={{ margin: 0 }}>
                    Check back later as more students join the platform
                  </p>
                </div>
              )}
            </motion.div>
          </AnimatePresence>
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

export default RecruiterDashboard;