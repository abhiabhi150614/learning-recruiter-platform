import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { recruiterAuthenticatedFetch } from '../api';
import { motion } from 'framer-motion';
import RecruiterLayout from './RecruiterLayout';
import { 
  FiUser, 
  FiMail, 
  FiCalendar,
  FiEdit3,
  FiSave,
  FiX,
  FiBriefcase,
  FiTrendingUp,
  FiUsers,
  FiSettings,
  FiShield,
  FiLogOut,
  FiDownload,
  FiEye,
  FiBarChart2
} from 'react-icons/fi';

const RecruiterProfile = () => {
  const [profile, setProfile] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [editForm, setEditForm] = useState({});
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    loadProfileData();
  }, []);

  const loadProfileData = async () => {
    try {
      setLoading(true);
      setError('');
      
      const [profileData, analyticsData] = await Promise.all([
        recruiterAuthenticatedFetch('/recruiter/profile'),
        recruiterAuthenticatedFetch('/recruiter/analytics/advanced')
      ]);
      
      setProfile(profileData);
      setAnalytics(analyticsData);
      setEditForm({
        name: profileData.google_name || profileData.name || '',
        email: profileData.email || '',
        organization: profileData.organization || ''
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      // In a real app, you'd have an update profile endpoint
      // For now, just simulate the save
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setProfile({
        ...profile,
        google_name: editForm.name,
        name: editForm.name,
        organization: editForm.organization
      });
      
      setEditing(false);
    } catch (err) {
      setError('Failed to save profile');
    } finally {
      setSaving(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('recruiter_token');
    localStorage.removeItem('recruiter_user');
    navigate('/recruiter/login');
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

  return (
    <RecruiterLayout>


      <div style={{ padding: '32px' }}>
        {/* Header */}
        <div style={{
          background: 'white',
          borderRadius: '16px',
          padding: '32px',
          marginBottom: '32px',
          boxShadow: '0 4px 6px rgba(0,0,0,0.05)',
          border: '1px solid #e2e8f0'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}>
            <div>
              <h1 style={{
                fontSize: '32px',
                fontWeight: '700',
                color: '#1a202c',
                margin: '0 0 8px'
              }}>
                Profile & Settings
              </h1>
              <p style={{
                color: '#718096',
                margin: 0,
                fontSize: '16px'
              }}>
                Manage your account settings and view analytics
              </p>
            </div>
          </div>
        </div>
        {error && (
          <div style={{
            background: '#fed7d7',
            color: '#c53030',
            padding: '12px 16px',
            borderRadius: '8px',
            marginBottom: '20px',
            border: '1px solid #feb2b2'
          }}>
            {error}
          </div>
        )}

        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '24px'
        }}>
          {/* Profile Information */}
          <div style={{
            background: 'white',
            borderRadius: '12px',
            padding: '24px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            border: '1px solid #e2e8f0'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '24px'
            }}>
              <h2 style={{
                fontSize: '18px',
                fontWeight: '600',
                color: '#1a202c',
                margin: 0
              }}>
                Profile Information
              </h2>
              
              {!editing ? (
                <button
                  onClick={() => setEditing(true)}
                  style={{
                    padding: '8px 12px',
                    background: '#4f8cff',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    fontSize: '14px',
                    fontWeight: '600'
                  }}
                >
                  <FiEdit3 size={14} />
                  Edit
                </button>
              ) : (
                <div style={{ display: 'flex', gap: '8px' }}>
                  <button
                    onClick={handleSave}
                    disabled={saving}
                    style={{
                      padding: '8px 12px',
                      background: '#10b981',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: saving ? 'not-allowed' : 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      fontSize: '14px',
                      fontWeight: '600'
                    }}
                  >
                    <FiSave size={14} />
                    {saving ? 'Saving...' : 'Save'}
                  </button>
                  <button
                    onClick={() => {
                      setEditing(false);
                      setEditForm({
                        name: profile.google_name || profile.name || '',
                        email: profile.email || '',
                        organization: profile.organization || ''
                      });
                    }}
                    style={{
                      padding: '8px 12px',
                      background: '#f7fafc',
                      border: '1px solid #e2e8f0',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      fontSize: '14px',
                      fontWeight: '600',
                      color: '#718096'
                    }}
                  >
                    <FiX size={14} />
                    Cancel
                  </button>
                </div>
              )}
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '20px', marginBottom: '24px' }}>
              <div style={{
                width: '80px',
                height: '80px',
                borderRadius: '50%',
                background: profile?.google_picture 
                  ? `url(${profile.google_picture})` 
                  : 'linear-gradient(135deg, #4f8cff, #6366f1)',
                backgroundSize: 'cover',
                backgroundPosition: 'center',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontSize: '32px',
                fontWeight: '600'
              }}>
                {!profile?.google_picture && (profile?.name || profile?.google_name || 'R').charAt(0).toUpperCase()}
              </div>
              
              <div>
                <h3 style={{
                  fontSize: '20px',
                  fontWeight: '600',
                  color: '#1a202c',
                  margin: '0 0 4px'
                }}>
                  {profile?.name || profile?.google_name || 'Recruiter'}
                </h3>
                <p style={{
                  color: '#718096',
                  margin: '0 0 8px',
                  fontSize: '14px'
                }}>
                  {profile?.email}
                </p>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  color: '#10b981',
                  fontSize: '12px',
                  fontWeight: '600'
                }}>
                  <FiShield size={12} />
                  Verified Recruiter
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div>
                <label style={{
                  display: 'block',
                  marginBottom: '6px',
                  color: '#2d3748',
                  fontWeight: '600',
                  fontSize: '14px'
                }}>
                  Full Name
                </label>
                {editing ? (
                  <input
                    type="text"
                    value={editForm.name}
                    onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                    style={{
                      width: '100%',
                      padding: '10px 12px',
                      border: '2px solid #e2e8f0',
                      borderRadius: '8px',
                      fontSize: '14px',
                      boxSizing: 'border-box',
                      outline: 'none'
                    }}
                    onFocus={(e) => e.target.style.borderColor = '#4f8cff'}
                    onBlur={(e) => e.target.style.borderColor = '#e2e8f0'}
                  />
                ) : (
                  <p style={{
                    margin: 0,
                    padding: '10px 12px',
                    background: '#f8fafc',
                    borderRadius: '8px',
                    color: '#1a202c',
                    fontSize: '14px'
                  }}>
                    {profile?.name || profile?.google_name || 'Not specified'}
                  </p>
                )}
              </div>

              <div>
                <label style={{
                  display: 'block',
                  marginBottom: '6px',
                  color: '#2d3748',
                  fontWeight: '600',
                  fontSize: '14px'
                }}>
                  Email Address
                </label>
                <p style={{
                  margin: 0,
                  padding: '10px 12px',
                  background: '#f8fafc',
                  borderRadius: '8px',
                  color: '#718096',
                  fontSize: '14px'
                }}>
                  {profile?.email} (Google Account)
                </p>
              </div>

              <div>
                <label style={{
                  display: 'block',
                  marginBottom: '6px',
                  color: '#2d3748',
                  fontWeight: '600',
                  fontSize: '14px'
                }}>
                  Organization
                </label>
                {editing ? (
                  <input
                    type="text"
                    value={editForm.organization}
                    onChange={(e) => setEditForm({ ...editForm, organization: e.target.value })}
                    placeholder="Enter your organization name"
                    style={{
                      width: '100%',
                      padding: '10px 12px',
                      border: '2px solid #e2e8f0',
                      borderRadius: '8px',
                      fontSize: '14px',
                      boxSizing: 'border-box',
                      outline: 'none'
                    }}
                    onFocus={(e) => e.target.style.borderColor = '#4f8cff'}
                    onBlur={(e) => e.target.style.borderColor = '#e2e8f0'}
                  />
                ) : (
                  <p style={{
                    margin: 0,
                    padding: '10px 12px',
                    background: '#f8fafc',
                    borderRadius: '8px',
                    color: '#1a202c',
                    fontSize: '14px'
                  }}>
                    {profile?.organization || 'Not specified'}
                  </p>
                )}
              </div>

              <div>
                <label style={{
                  display: 'block',
                  marginBottom: '6px',
                  color: '#2d3748',
                  fontWeight: '600',
                  fontSize: '14px'
                }}>
                  Member Since
                </label>
                <p style={{
                  margin: 0,
                  padding: '10px 12px',
                  background: '#f8fafc',
                  borderRadius: '8px',
                  color: '#1a202c',
                  fontSize: '14px'
                }}>
                  {profile?.stats?.member_since || 'Recently'}
                </p>
              </div>
            </div>
          </div>

          {/* Analytics & Stats */}
          <div style={{
            background: 'white',
            borderRadius: '12px',
            padding: '24px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            border: '1px solid #e2e8f0'
          }}>
            <h2 style={{
              fontSize: '18px',
              fontWeight: '600',
              color: '#1a202c',
              margin: '0 0 24px'
            }}>
              Account Analytics
            </h2>

            <div style={{
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: '16px',
              marginBottom: '24px'
            }}>
              {[
                { 
                  icon: FiBriefcase, 
                  label: 'Jobs Posted', 
                  value: profile?.stats?.jobs_posted || 0, 
                  color: '#4f8cff' 
                },
                { 
                  icon: FiMail, 
                  label: 'Emails Sent', 
                  value: profile?.stats?.emails_sent || 0, 
                  color: '#10b981' 
                },
                { 
                  icon: FiUsers, 
                  label: 'Candidates Viewed', 
                  value: analytics?.overview?.total_students || 0, 
                  color: '#f59e0b' 
                },
                { 
                  icon: FiTrendingUp, 
                  label: 'Active Candidates', 
                  value: analytics?.overview?.active_candidates || 0, 
                  color: '#8b5cf6' 
                }
              ].map((stat, index) => (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.1 }}
                  style={{
                    padding: '16px',
                    background: `${stat.color}10`,
                    borderRadius: '8px',
                    border: `1px solid ${stat.color}30`
                  }}
                >
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    marginBottom: '8px'
                  }}>
                    <stat.icon size={16} color={stat.color} />
                    <span style={{
                      fontSize: '12px',
                      color: '#718096',
                      fontWeight: '600'
                    }}>
                      {stat.label}
                    </span>
                  </div>
                  <p style={{
                    margin: 0,
                    fontSize: '20px',
                    fontWeight: '700',
                    color: stat.color
                  }}>
                    {stat.value}
                  </p>
                </motion.div>
              ))}
            </div>

            {analytics?.skill_insights && (
              <div>
                <h3 style={{
                  fontSize: '16px',
                  fontWeight: '600',
                  color: '#1a202c',
                  margin: '0 0 16px'
                }}>
                  Top Skills in Talent Pool
                </h3>
                <div style={{
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '8px'
                }}>
                  {analytics.skill_insights.top_skills.slice(0, 5).map((skill, index) => (
                    <div
                      key={skill.skill}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        padding: '8px 12px',
                        background: '#f8fafc',
                        borderRadius: '6px'
                      }}
                    >
                      <span style={{
                        fontSize: '14px',
                        color: '#1a202c',
                        fontWeight: '500'
                      }}>
                        {skill.skill}
                      </span>
                      <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px'
                      }}>
                        <div style={{
                          width: '60px',
                          height: '4px',
                          background: '#e2e8f0',
                          borderRadius: '2px',
                          overflow: 'hidden'
                        }}>
                          <div style={{
                            width: `${skill.percentage}%`,
                            height: '100%',
                            background: '#4f8cff',
                            borderRadius: '2px'
                          }} />
                        </div>
                        <span style={{
                          fontSize: '12px',
                          color: '#718096',
                          fontWeight: '600'
                        }}>
                          {skill.count}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Quick Actions */}
        <div style={{
          background: 'white',
          borderRadius: '12px',
          padding: '24px',
          marginTop: '24px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          border: '1px solid #e2e8f0'
        }}>
          <h2 style={{
            fontSize: '18px',
            fontWeight: '600',
            color: '#1a202c',
            margin: '0 0 20px'
          }}>
            Quick Actions
          </h2>
          
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '16px'
          }}>
            {[
              { 
                icon: FiUsers, 
                label: 'View Candidates', 
                action: () => navigate('/recruiter/candidates'), 
                color: '#4f8cff' 
              },
              { 
                icon: FiBriefcase, 
                label: 'Manage Jobs', 
                action: () => navigate('/recruiter/jobs'), 
                color: '#10b981' 
              },
              { 
                icon: FiMail, 
                label: 'Email Center', 
                action: () => navigate('/recruiter/emails'), 
                color: '#f59e0b' 
              },
              { 
                icon: FiBarChart2, 
                label: 'Analytics', 
                action: () => navigate('/recruiter'), 
                color: '#8b5cf6' 
              },
              { 
                icon: FiDownload, 
                label: 'Export Data', 
                action: () => alert('Export feature coming soon!'), 
                color: '#e53e3e' 
              },
              { 
                icon: FiSettings, 
                label: 'Social Connections', 
                action: () => navigate('/recruiter/settings'), 
                color: '#718096' 
              }
            ].map((action, index) => (
              <motion.button
                key={action.label}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={action.action}
                style={{
                  padding: '16px',
                  background: `${action.color}10`,
                  border: `1px solid ${action.color}30`,
                  borderRadius: '8px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  transition: 'all 0.3s ease'
                }}
              >
                <action.icon size={20} color={action.color} />
                <span style={{
                  fontWeight: '600',
                  color: action.color
                }}>
                  {action.label}
                </span>
              </motion.button>
            ))}
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

export default RecruiterProfile;