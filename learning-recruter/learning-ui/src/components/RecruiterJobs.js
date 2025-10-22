import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { recruiterAuthenticatedFetch } from '../api';
import { motion, AnimatePresence } from 'framer-motion';
import RecruiterLayout from './RecruiterLayout';
import { FiBriefcase, FiEye, FiUsers, FiMapPin, FiDollarSign, FiMail, FiStar, FiRefreshCw, FiChevronDown, FiChevronUp, FiPlus } from 'react-icons/fi';

const RecruiterJobs = () => {
  const [jobs, setJobs] = useState([]);
  const [jobMatches, setJobMatches] = useState({});
  const [expandedJobs, setExpandedJobs] = useState({});
  const [loading, setLoading] = useState(true);
  const [matchingLoading, setMatchingLoading] = useState({});
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    loadJobs();
  }, []);

  const loadJobs = async () => {
    try {
      setLoading(true);
      const response = await recruiterAuthenticatedFetch('/recruiter/jobs');
      setJobs(response.jobs || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleMatchCandidates = async (jobId) => {
    try {
      setMatchingLoading(prev => ({ ...prev, [jobId]: true }));
      const response = await recruiterAuthenticatedFetch(`/recruiter/jobs/${jobId}/match`, {
        method: 'POST'
      });
      
      setJobMatches(prev => ({ ...prev, [jobId]: response.matches || [] }));
      setExpandedJobs(prev => ({ ...prev, [jobId]: true }));
    } catch (err) {
      setError(`Error finding matches: ${err.message}`);
    } finally {
      setMatchingLoading(prev => ({ ...prev, [jobId]: false }));
    }
  };

  const handleSendEmail = async (candidate, jobTitle) => {
    try {
      await recruiterAuthenticatedFetch('/recruiter/send-email', {
        method: 'POST',
        body: JSON.stringify({
          to: candidate.email,
          subject: `Job Opportunity: ${jobTitle}`,
          message: `Hi ${candidate.name},\n\nI found your profile and believe you'd be a great fit for our ${jobTitle} position. Your skills and experience align well with what we're looking for.\n\nWould you be interested in learning more about this opportunity?\n\nBest regards`
        })
      });
      alert('Email sent successfully!');
    } catch (err) {
      alert(`Failed to send email: ${err.message}`);
    }
  };

  const toggleJobExpansion = (jobId) => {
    setExpandedJobs(prev => ({ ...prev, [jobId]: !prev[jobId] }));
  };

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ width: '40px', height: '40px', border: '4px solid #e2e8f0', borderTop: '4px solid #4f8cff', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
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
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h1 style={{ fontSize: '32px', fontWeight: '700', color: '#1a202c', margin: '0 0 8px' }}>
                My Job Postings
              </h1>
              <p style={{ color: '#718096', margin: 0, fontSize: '16px' }}>
                Manage your job postings and find matching candidates
              </p>
            </div>
            
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => navigate('/recruiter/post-job')}
              style={{
                padding: '16px 24px',
                background: 'linear-gradient(135deg, #4f8cff, #6366f1)',
                color: 'white',
                border: 'none',
                borderRadius: '12px',
                fontWeight: '600',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                boxShadow: '0 8px 25px rgba(79, 140, 255, 0.3)'
              }}
            >
              <FiPlus size={16} />
              Post New Job
            </motion.button>
          </div>
        </div>

        {error && (
          <div style={{
            background: '#fed7d7',
            color: '#c53030',
            padding: '12px 16px',
            borderRadius: '8px',
            marginBottom: '24px'
          }}>
            {error}
          </div>
        )}

        {/* Jobs List */}
        {jobs.length === 0 ? (
          <div style={{
            background: 'white',
            borderRadius: '12px',
            padding: '60px',
            textAlign: 'center',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
          }}>
            <FiBriefcase size={48} style={{ color: '#718096', marginBottom: '16px' }} />
            <h3 style={{ color: '#1a202c', marginBottom: '8px' }}>No jobs posted yet</h3>
            <p style={{ color: '#718096', marginBottom: '24px' }}>
              Start by posting your first job to find matching candidates
            </p>
            <button
              onClick={() => navigate('/recruiter/post-job')}
              style={{
                padding: '12px 24px',
                background: '#4f8cff',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontWeight: '600',
                cursor: 'pointer'
              }}
            >
              Post Your First Job
            </button>
          </div>
        ) : (
          <div style={{ display: 'grid', gap: '20px' }}>
            {jobs.map((job, index) => (
              <motion.div
                key={job.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                style={{
                  background: 'white',
                  borderRadius: '12px',
                  padding: '24px',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                  border: '1px solid #e2e8f0'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                  <div style={{ flex: 1 }}>
                    <h3 style={{
                      fontSize: '20px',
                      fontWeight: '600',
                      color: '#1a202c',
                      margin: '0 0 8px'
                    }}>
                      {job.title}
                    </h3>
                    
                    <div style={{ display: 'flex', gap: '16px', marginBottom: '12px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#718096' }}>
                        <FiMapPin size={14} />
                        <span style={{ fontSize: '14px' }}>{job.location}</span>
                      </div>
                      {job.salary_range && (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#718096' }}>
                          <FiDollarSign size={14} />
                          <span style={{ fontSize: '14px' }}>{job.salary_range}</span>
                        </div>
                      )}
                      <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#718096' }}>
                        <span style={{ fontSize: '14px' }}>Posted {new Date(job.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                    
                    <p style={{
                      color: '#4a5568',
                      fontSize: '14px',
                      lineHeight: '1.5',
                      margin: '0 0 16px'
                    }}>
                      {job.description.length > 150 ? job.description.substring(0, 150) + '...' : job.description}
                    </p>
                    
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                      {(job.requirements || []).slice(0, 5).map((req, i) => (
                        <span
                          key={i}
                          style={{
                            padding: '4px 8px',
                            background: '#e0f2fe',
                            color: '#0369a1',
                            borderRadius: '12px',
                            fontSize: '12px',
                            fontWeight: '500'
                          }}
                        >
                          {req}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  <div style={{ display: 'flex', gap: '8px', marginLeft: '16px' }}>
                    <button
                      onClick={() => handleMatchCandidates(job.id)}
                      disabled={matchingLoading[job.id]}
                      style={{
                        padding: '10px 16px',
                        background: matchingLoading[job.id] ? '#a0aec0' : '#10b981',
                        color: 'white',
                        border: 'none',
                        borderRadius: '6px',
                        cursor: matchingLoading[job.id] ? 'not-allowed' : 'pointer',
                        fontSize: '14px',
                        fontWeight: '600',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px'
                      }}
                    >
                      {matchingLoading[job.id] ? (
                        <FiRefreshCw size={14} style={{ animation: 'spin 1s linear infinite' }} />
                      ) : (
                        <FiUsers size={14} />
                      )}
                      {matchingLoading[job.id] ? 'Finding...' : 'Find Matches'}
                    </button>
                    
                    {jobMatches[job.id] && jobMatches[job.id].length > 0 && (
                      <button
                        onClick={() => toggleJobExpansion(job.id)}
                        style={{
                          padding: '10px 16px',
                          background: '#4f8cff',
                          color: 'white',
                          border: 'none',
                          borderRadius: '6px',
                          cursor: 'pointer',
                          fontSize: '14px',
                          fontWeight: '600',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '6px'
                        }}
                      >
                        {jobMatches[job.id].length} Matches
                        {expandedJobs[job.id] ? <FiChevronUp size={14} /> : <FiChevronDown size={14} />}
                      </button>
                    )}
                  </div>
                </div>
                
                {/* Matched Candidates Section */}
                <AnimatePresence>
                  {expandedJobs[job.id] && jobMatches[job.id] && jobMatches[job.id].length > 0 && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      style={{
                        marginTop: '20px',
                        paddingTop: '20px',
                        borderTop: '1px solid #e2e8f0'
                      }}
                    >
                      <h4 style={{
                        fontSize: '16px',
                        fontWeight: '600',
                        color: '#1a202c',
                        margin: '0 0 16px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px'
                      }}>
                        <FiUsers size={16} color="#4f8cff" />
                        Matched Candidates ({jobMatches[job.id].length})
                      </h4>
                      
                      <div style={{ display: 'grid', gap: '12px' }}>
                        {jobMatches[job.id].slice(0, 10).map((candidate, idx) => (
                          <motion.div
                            key={candidate.user_id}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: idx * 0.05 }}
                            style={{
                              padding: '16px',
                              background: '#f8fafc',
                              borderRadius: '8px',
                              border: '1px solid #e2e8f0',
                              display: 'flex',
                              justifyContent: 'space-between',
                              alignItems: 'center'
                            }}
                          >
                            <div style={{ flex: 1 }}>
                              <div style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '12px',
                                marginBottom: '8px'
                              }}>
                                <h5 style={{
                                  fontSize: '16px',
                                  fontWeight: '600',
                                  color: '#1a202c',
                                  margin: 0
                                }}>
                                  {candidate.name}
                                </h5>
                                
                                <div style={{
                                  display: 'flex',
                                  alignItems: 'center',
                                  gap: '4px',
                                  padding: '2px 8px',
                                  background: candidate.score >= 80 ? '#d1fae5' : candidate.score >= 60 ? '#fef3c7' : '#fed7d7',
                                  color: candidate.score >= 80 ? '#065f46' : candidate.score >= 60 ? '#92400e' : '#991b1b',
                                  borderRadius: '12px',
                                  fontSize: '12px',
                                  fontWeight: '600'
                                }}>
                                  <FiStar size={10} />
                                  {candidate.score}% Match
                                </div>
                              </div>
                              
                              <p style={{
                                color: '#718096',
                                fontSize: '14px',
                                margin: '0 0 8px',
                                lineHeight: '1.4'
                              }}>
                                {candidate.career_goals || candidate.profile || 'No profile information available'}
                              </p>
                              
                              <div style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '12px',
                                fontSize: '12px',
                                color: '#a0aec0'
                              }}>
                                <span>{candidate.email}</span>
                                {candidate.learning_progress && (
                                  <span>Learning Progress: {Math.round(candidate.learning_progress)}%</span>
                                )}
                              </div>
                            </div>
                            
                            <div style={{
                              display: 'flex',
                              gap: '8px',
                              marginLeft: '16px'
                            }}>
                              <button
                                onClick={() => navigate(`/recruiter/candidate/${candidate.user_id}`)}
                                style={{
                                  padding: '8px',
                                  background: '#4f8cff',
                                  color: 'white',
                                  border: 'none',
                                  borderRadius: '6px',
                                  cursor: 'pointer'
                                }}
                              >
                                <FiEye size={14} />
                              </button>
                              
                              <button
                                onClick={() => handleSendEmail(candidate, job.title)}
                                style={{
                                  padding: '8px',
                                  background: '#10b981',
                                  color: 'white',
                                  border: 'none',
                                  borderRadius: '6px',
                                  cursor: 'pointer'
                                }}
                              >
                                <FiMail size={14} />
                              </button>
                            </div>
                          </motion.div>
                        ))}
                      </div>
                      
                      {jobMatches[job.id].length > 10 && (
                        <div style={{
                          textAlign: 'center',
                          marginTop: '16px'
                        }}>
                          <button
                            onClick={() => navigate('/recruiter/candidates', { state: { jobId: job.id, matches: jobMatches[job.id] } })}
                            style={{
                              padding: '8px 16px',
                              background: '#f7fafc',
                              border: '1px solid #e2e8f0',
                              borderRadius: '6px',
                              cursor: 'pointer',
                              fontSize: '14px',
                              fontWeight: '600',
                              color: '#4f8cff'
                            }}
                          >
                            View All {jobMatches[job.id].length} Matches
                          </button>
                        </div>
                      )}
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            ))}
          </div>
        )}
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

export default RecruiterJobs;