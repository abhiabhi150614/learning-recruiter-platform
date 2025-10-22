import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { recruiterAuthenticatedFetch } from '../api';
import { motion } from 'framer-motion';
import { 
  FiArrowLeft, 
  FiBriefcase, 
  FiMapPin, 
  FiDollarSign, 
  FiClock, 
  FiUsers,
  FiEye,
  FiTarget,
  FiZap
} from 'react-icons/fi';

const RecruiterJobPosting = () => {
  const [jobData, setJobData] = useState({
    title: '',
    company: '',
    location: '',
    type: 'full-time',
    salary_min: '',
    salary_max: '',
    description: '',
    requirements: '',
    benefits: '',
    skills: []
  });
  const [skillInput, setSkillInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [matches, setMatches] = useState([]);
  const [showPreview, setShowPreview] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('recruiter_token');
    if (!token) {
      navigate('/recruiter/login');
    }
  }, [navigate]);

  const handleInputChange = (e) => {
    setJobData({
      ...jobData,
      [e.target.name]: e.target.value
    });
  };

  const addSkill = () => {
    if (skillInput.trim() && !jobData.skills.includes(skillInput.trim())) {
      setJobData({
        ...jobData,
        skills: [...jobData.skills, skillInput.trim()]
      });
      setSkillInput('');
    }
  };

  const removeSkill = (skillToRemove) => {
    setJobData({
      ...jobData,
      skills: jobData.skills.filter(skill => skill !== skillToRemove)
    });
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addSkill();
    }
  };

  const findMatches = async () => {
    try {
      setLoading(true);
      const jobDescription = `${jobData.title} ${jobData.description} ${jobData.requirements} Skills: ${jobData.skills.join(', ')}`;
      
      const matchResults = await recruiterAuthenticatedFetch('/recruiter/match', {
        method: 'POST',
        body: JSON.stringify({ job_description: jobDescription })
      });
      
      setMatches(matchResults.slice(0, 10));
    } catch (err) {
      alert(`Error finding matches: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const postJob = async () => {
    try {
      setLoading(true);
      // Post job and trigger Composio automations
      await recruiterAuthenticatedFetch('/recruiter/jobs', {
        method: 'POST',
        body: JSON.stringify(jobData)
      });
      
      // Trigger automated candidate outreach
      await recruiterAuthenticatedFetch('/recruiter/pipeline/auto', {
        method: 'POST',
        body: JSON.stringify({ 
          job_description: `${jobData.title} ${jobData.description} ${jobData.requirements}`,
          job_data: jobData
        })
      });
      
      alert('Job posted successfully! Automated candidate outreach initiated.');
      navigate('/recruiter');
    } catch (err) {
      alert(`Error posting job: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: '#f8fafc'
    }}>
      {/* Header */}
      <div style={{
        background: 'white',
        borderBottom: '1px solid #e2e8f0',
        padding: '16px 24px',
        display: 'flex',
        alignItems: 'center',
        gap: '16px'
      }}>
        <button
          onClick={() => navigate('/recruiter')}
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
        
        <div>
          <h1 style={{
            fontSize: '24px',
            fontWeight: '700',
            color: '#1a202c',
            margin: 0
          }}>
            Post New Job
          </h1>
          <p style={{
            color: '#718096',
            margin: '4px 0 0',
            fontSize: '14px'
          }}>
            Create a job posting and find the best candidates with AI
          </p>
        </div>
      </div>

      <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: showPreview ? '1fr 1fr' : '1fr',
          gap: '24px'
        }}>
          {/* Job Form */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
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
              marginBottom: '20px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <FiBriefcase size={20} />
              Job Details
            </h2>

            <div style={{ display: 'grid', gap: '20px' }}>
              {/* Basic Info */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                <div>
                  <label style={{
                    display: 'block',
                    marginBottom: '8px',
                    color: '#2d3748',
                    fontWeight: '600',
                    fontSize: '14px'
                  }}>
                    Job Title *
                  </label>
                  <input
                    type="text"
                    name="title"
                    value={jobData.title}
                    onChange={handleInputChange}
                    placeholder="e.g. Senior React Developer"
                    style={{
                      width: '100%',
                      padding: '12px',
                      border: '2px solid #e2e8f0',
                      borderRadius: '8px',
                      fontSize: '14px',
                      boxSizing: 'border-box'
                    }}
                  />
                </div>

                <div>
                  <label style={{
                    display: 'block',
                    marginBottom: '8px',
                    color: '#2d3748',
                    fontWeight: '600',
                    fontSize: '14px'
                  }}>
                    Company
                  </label>
                  <input
                    type="text"
                    name="company"
                    value={jobData.company}
                    onChange={handleInputChange}
                    placeholder="Company name"
                    style={{
                      width: '100%',
                      padding: '12px',
                      border: '2px solid #e2e8f0',
                      borderRadius: '8px',
                      fontSize: '14px',
                      boxSizing: 'border-box'
                    }}
                  />
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px' }}>
                <div>
                  <label style={{
                    display: 'block',
                    marginBottom: '8px',
                    color: '#2d3748',
                    fontWeight: '600',
                    fontSize: '14px'
                  }}>
                    <FiMapPin size={14} style={{ marginRight: '4px' }} />
                    Location
                  </label>
                  <input
                    type="text"
                    name="location"
                    value={jobData.location}
                    onChange={handleInputChange}
                    placeholder="Remote / City, State"
                    style={{
                      width: '100%',
                      padding: '12px',
                      border: '2px solid #e2e8f0',
                      borderRadius: '8px',
                      fontSize: '14px',
                      boxSizing: 'border-box'
                    }}
                  />
                </div>

                <div>
                  <label style={{
                    display: 'block',
                    marginBottom: '8px',
                    color: '#2d3748',
                    fontWeight: '600',
                    fontSize: '14px'
                  }}>
                    <FiClock size={14} style={{ marginRight: '4px' }} />
                    Job Type
                  </label>
                  <select
                    name="type"
                    value={jobData.type}
                    onChange={handleInputChange}
                    style={{
                      width: '100%',
                      padding: '12px',
                      border: '2px solid #e2e8f0',
                      borderRadius: '8px',
                      fontSize: '14px',
                      boxSizing: 'border-box'
                    }}
                  >
                    <option value="full-time">Full-time</option>
                    <option value="part-time">Part-time</option>
                    <option value="contract">Contract</option>
                    <option value="internship">Internship</option>
                  </select>
                </div>

                <div>
                  <label style={{
                    display: 'block',
                    marginBottom: '8px',
                    color: '#2d3748',
                    fontWeight: '600',
                    fontSize: '14px'
                  }}>
                    <FiDollarSign size={14} style={{ marginRight: '4px' }} />
                    Salary Range
                  </label>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <input
                      type="number"
                      name="salary_min"
                      value={jobData.salary_min}
                      onChange={handleInputChange}
                      placeholder="Min"
                      style={{
                        flex: 1,
                        padding: '12px',
                        border: '2px solid #e2e8f0',
                        borderRadius: '8px',
                        fontSize: '14px',
                        boxSizing: 'border-box'
                      }}
                    />
                    <input
                      type="number"
                      name="salary_max"
                      value={jobData.salary_max}
                      onChange={handleInputChange}
                      placeholder="Max"
                      style={{
                        flex: 1,
                        padding: '12px',
                        border: '2px solid #e2e8f0',
                        borderRadius: '8px',
                        fontSize: '14px',
                        boxSizing: 'border-box'
                      }}
                    />
                  </div>
                </div>
              </div>

              {/* Skills */}
              <div>
                <label style={{
                  display: 'block',
                  marginBottom: '8px',
                  color: '#2d3748',
                  fontWeight: '600',
                  fontSize: '14px'
                }}>
                  Required Skills
                </label>
                <div style={{
                  display: 'flex',
                  gap: '8px',
                  marginBottom: '8px'
                }}>
                  <input
                    type="text"
                    value={skillInput}
                    onChange={(e) => setSkillInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Add a skill and press Enter"
                    style={{
                      flex: 1,
                      padding: '12px',
                      border: '2px solid #e2e8f0',
                      borderRadius: '8px',
                      fontSize: '14px',
                      boxSizing: 'border-box'
                    }}
                  />
                  <button
                    type="button"
                    onClick={addSkill}
                    style={{
                      padding: '12px 16px',
                      background: '#4f8cff',
                      color: 'white',
                      border: 'none',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      fontWeight: '600'
                    }}
                  >
                    Add
                  </button>
                </div>
                <div style={{
                  display: 'flex',
                  flexWrap: 'wrap',
                  gap: '8px'
                }}>
                  {jobData.skills.map((skill, index) => (
                    <span
                      key={index}
                      style={{
                        padding: '6px 12px',
                        background: '#e0f2fe',
                        color: '#0369a1',
                        borderRadius: '16px',
                        fontSize: '14px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px'
                      }}
                    >
                      {skill}
                      <button
                        onClick={() => removeSkill(skill)}
                        style={{
                          background: 'none',
                          border: 'none',
                          color: '#0369a1',
                          cursor: 'pointer',
                          fontSize: '16px',
                          padding: 0
                        }}
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>

              {/* Description */}
              <div>
                <label style={{
                  display: 'block',
                  marginBottom: '8px',
                  color: '#2d3748',
                  fontWeight: '600',
                  fontSize: '14px'
                }}>
                  Job Description *
                </label>
                <textarea
                  name="description"
                  value={jobData.description}
                  onChange={handleInputChange}
                  rows={6}
                  placeholder="Describe the role, responsibilities, and what makes this opportunity exciting..."
                  style={{
                    width: '100%',
                    padding: '12px',
                    border: '2px solid #e2e8f0',
                    borderRadius: '8px',
                    fontSize: '14px',
                    boxSizing: 'border-box',
                    resize: 'vertical'
                  }}
                />
              </div>

              {/* Requirements */}
              <div>
                <label style={{
                  display: 'block',
                  marginBottom: '8px',
                  color: '#2d3748',
                  fontWeight: '600',
                  fontSize: '14px'
                }}>
                  Requirements
                </label>
                <textarea
                  name="requirements"
                  value={jobData.requirements}
                  onChange={handleInputChange}
                  rows={4}
                  placeholder="List the required qualifications, experience, and skills..."
                  style={{
                    width: '100%',
                    padding: '12px',
                    border: '2px solid #e2e8f0',
                    borderRadius: '8px',
                    fontSize: '14px',
                    boxSizing: 'border-box',
                    resize: 'vertical'
                  }}
                />
              </div>

              {/* Benefits */}
              <div>
                <label style={{
                  display: 'block',
                  marginBottom: '8px',
                  color: '#2d3748',
                  fontWeight: '600',
                  fontSize: '14px'
                }}>
                  Benefits & Perks
                </label>
                <textarea
                  name="benefits"
                  value={jobData.benefits}
                  onChange={handleInputChange}
                  rows={3}
                  placeholder="Health insurance, remote work, professional development..."
                  style={{
                    width: '100%',
                    padding: '12px',
                    border: '2px solid #e2e8f0',
                    borderRadius: '8px',
                    fontSize: '14px',
                    boxSizing: 'border-box',
                    resize: 'vertical'
                  }}
                />
              </div>
            </div>

            {/* Action Buttons */}
            <div style={{
              display: 'flex',
              gap: '12px',
              marginTop: '24px',
              paddingTop: '24px',
              borderTop: '1px solid #e2e8f0'
            }}>
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={findMatches}
                disabled={loading || !jobData.title || !jobData.description}
                style={{
                  flex: 1,
                  padding: '12px 20px',
                  background: loading ? '#a0aec0' : '#f59e0b',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontWeight: '600',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px'
                }}
              >
                <FiTarget size={16} />
                {loading ? 'Finding...' : 'Find Matches'}
              </motion.button>

              <button
                onClick={() => setShowPreview(!showPreview)}
                style={{
                  padding: '12px 20px',
                  background: '#f7fafc',
                  color: '#4f8cff',
                  border: '1px solid #e2e8f0',
                  borderRadius: '8px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}
              >
                <FiEye size={16} />
                Preview
              </button>

              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={postJob}
                disabled={loading || !jobData.title || !jobData.description}
                style={{
                  flex: 1,
                  padding: '12px 20px',
                  background: loading ? '#a0aec0' : 'linear-gradient(135deg, #4f8cff, #6366f1)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontWeight: '600',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px'
                }}
              >
                <FiZap size={16} />
                {loading ? 'Posting...' : 'Post & Auto-Match'}
              </motion.button>
            </div>
          </motion.div>

          {/* Preview/Matches Panel */}
          {showPreview && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
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
                marginBottom: '20px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                <FiUsers size={20} />
                AI Matches ({matches.length})
              </h2>

              {matches.length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {matches.map((match, index) => (
                    <div
                      key={match.user_id}
                      style={{
                        padding: '16px',
                        border: '1px solid #e2e8f0',
                        borderRadius: '8px',
                        background: '#f8fafc'
                      }}
                    >
                      <div style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        marginBottom: '8px'
                      }}>
                        <h3 style={{
                          fontSize: '16px',
                          fontWeight: '600',
                          color: '#1a202c',
                          margin: 0
                        }}>
                          Candidate #{match.user_id}
                        </h3>
                        <span style={{
                          padding: '4px 8px',
                          background: match.score > 0.7 ? '#d1fae5' : '#fef3c7',
                          color: match.score > 0.7 ? '#065f46' : '#92400e',
                          borderRadius: '12px',
                          fontSize: '12px',
                          fontWeight: '600'
                        }}>
                          {(match.score * 100).toFixed(0)}% Match
                        </span>
                      </div>
                      
                      <p style={{
                        color: '#718096',
                        fontSize: '14px',
                        margin: '0 0 8px',
                        lineHeight: '1.4'
                      }}>
                        {match.summary?.substring(0, 100)}...
                      </p>
                      
                      <div style={{
                        display: 'flex',
                        flexWrap: 'wrap',
                        gap: '4px'
                      }}>
                        {(match.skills_tags || []).slice(0, 4).map((skill, i) => (
                          <span
                            key={i}
                            style={{
                              padding: '2px 6px',
                              background: '#e0f2fe',
                              color: '#0369a1',
                              borderRadius: '10px',
                              fontSize: '11px'
                            }}
                          >
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div style={{
                  textAlign: 'center',
                  padding: '40px 20px',
                  color: '#718096'
                }}>
                  <FiTarget size={48} style={{ marginBottom: '16px' }} />
                  <p>Click "Find Matches" to see AI-powered candidate recommendations</p>
                </div>
              )}
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RecruiterJobPosting;