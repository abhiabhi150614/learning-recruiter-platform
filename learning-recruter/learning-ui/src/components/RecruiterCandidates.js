import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { recruiterAuthenticatedFetch } from '../api';
import { motion } from 'framer-motion';
import { 
  FiArrowLeft, 
  FiSearch, 
  FiFilter, 
  FiUsers, 
  FiMail, 
  FiLinkedin,
  FiCalendar,
  FiEye,
  FiDownload,
  FiRefreshCw,
  FiStar,
  FiMapPin,
  FiClock,
  FiTrendingUp
} from 'react-icons/fi';

const RecruiterCandidates = () => {
  const [candidates, setCandidates] = useState([]);
  const [filteredCandidates, setFilteredCandidates] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    skills: '',
    minScore: 0,
    location: '',
    experience: ''
  });
  const [loading, setLoading] = useState(true);
  const [selectedCandidates, setSelectedCandidates] = useState([]);
  const [sortBy, setSortBy] = useState('score');
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('recruiter_token');
    if (!token) {
      navigate('/recruiter/login');
      return;
    }
    loadCandidates();
  }, [navigate]);

  useEffect(() => {
    filterAndSortCandidates();
  }, [candidates, searchTerm, filters, sortBy]);

  const loadCandidates = async () => {
    try {
      setLoading(true);
      // Load all students instead of using match endpoint
      const results = await recruiterAuthenticatedFetch('/recruiter/students');
      
      // Transform students data to match candidate format
      const candidatesData = results.students.map(student => ({
        user_id: student.id,
        score: 0.85, // Default score for display
        summary: student.summary,
        skills_tags: student.skills || [],
        name: student.name,
        email: student.email,
        source: student.source || 'Platform User',
        added_by_recruiter: student.added_by_recruiter || false,
        career_goals: student.career_goals,
        learning_progress: student.learning_progress || 0
      }));
      
      setCandidates(candidatesData);
    } catch (err) {
      console.error('Error loading candidates:', err);
    } finally {
      setLoading(false);
    }
  };

  const filterAndSortCandidates = () => {
    let filtered = candidates.filter(candidate => {
      const matchesSearch = !searchTerm || 
        candidate.summary?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        candidate.skills_tags?.some(skill => 
          skill.toLowerCase().includes(searchTerm.toLowerCase())
        );
      
      const matchesSkills = !filters.skills || 
        candidate.skills_tags?.some(skill => 
          skill.toLowerCase().includes(filters.skills.toLowerCase())
        );
      
      const matchesScore = candidate.score >= filters.minScore / 100;
      
      return matchesSearch && matchesSkills && matchesScore;
    });

    // Sort candidates
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'score':
          return b.score - a.score;
        case 'user_id':
          return a.user_id - b.user_id;
        default:
          return b.score - a.score;
      }
    });

    setFilteredCandidates(filtered);
  };

  const handleCandidateSelect = (candidateId) => {
    setSelectedCandidates(prev => 
      prev.includes(candidateId) 
        ? prev.filter(id => id !== candidateId)
        : [...prev, candidateId]
    );
  };

  const handleBulkAction = async (action) => {
    if (selectedCandidates.length === 0) {
      alert('Please select candidates first');
      return;
    }

    try {
      setLoading(true);
      for (const candidateId of selectedCandidates) {
        await recruiterAuthenticatedFetch(`/recruiter/composio/${action}`, {
          method: 'POST',
          body: JSON.stringify({ user_id: candidateId })
        });
      }
      alert(`${action} completed for ${selectedCandidates.length} candidates`);
      setSelectedCandidates([]);
    } catch (err) {
      alert(`Bulk action failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const reindexCandidates = async () => {
    try {
      setLoading(true);
      await recruiterAuthenticatedFetch('/recruiter/reindex-students', {
        method: 'POST'
      });
      await loadCandidates();
      alert('Candidate database reindexed successfully!');
    } catch (err) {
      alert(`Reindex failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  if (loading && candidates.length === 0) {
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
          justifyContent: 'space-between',
          marginBottom: '16px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
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
                Candidate Database
              </h1>
              <p style={{
                color: '#718096',
                margin: '4px 0 0',
                fontSize: '14px'
              }}>
                {filteredCandidates.length} candidates found
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '12px' }}>
            <button
              onClick={reindexCandidates}
              disabled={loading}
              style={{
                padding: '10px 16px',
                background: '#f59e0b',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontWeight: '600',
                cursor: loading ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}
            >
              <FiRefreshCw size={16} />
              Reindex
            </button>

            {selectedCandidates.length > 0 && (
              <div style={{ display: 'flex', gap: '8px' }}>
                <button
                  onClick={() => handleBulkAction('send-email')}
                  style={{
                    padding: '10px 16px',
                    background: '#10b981',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    fontWeight: '600',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}
                >
                  <FiMail size={16} />
                  Email ({selectedCandidates.length})
                </button>

                <button
                  onClick={() => handleBulkAction('linkedin-enrich')}
                  style={{
                    padding: '10px 16px',
                    background: '#0077b5',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    fontWeight: '600',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}
                >
                  <FiLinkedin size={16} />
                  LinkedIn
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Search and Filters */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '2fr 1fr 1fr 1fr 1fr',
          gap: '12px',
          alignItems: 'end'
        }}>
          <div>
            <label style={{
              display: 'block',
              marginBottom: '4px',
              color: '#2d3748',
              fontWeight: '600',
              fontSize: '12px'
            }}>
              Search Candidates
            </label>
            <div style={{ position: 'relative' }}>
              <FiSearch style={{
                position: 'absolute',
                left: '12px',
                top: '50%',
                transform: 'translateY(-50%)',
                color: '#a0aec0'
              }} />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search by skills, summary..."
                style={{
                  width: '100%',
                  padding: '10px 12px 10px 40px',
                  border: '2px solid #e2e8f0',
                  borderRadius: '8px',
                  fontSize: '14px',
                  boxSizing: 'border-box'
                }}
              />
            </div>
          </div>

          <div>
            <label style={{
              display: 'block',
              marginBottom: '4px',
              color: '#2d3748',
              fontWeight: '600',
              fontSize: '12px'
            }}>
              Skills Filter
            </label>
            <input
              type="text"
              value={filters.skills}
              onChange={(e) => setFilters({...filters, skills: e.target.value})}
              placeholder="e.g. React"
              style={{
                width: '100%',
                padding: '10px 12px',
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
              marginBottom: '4px',
              color: '#2d3748',
              fontWeight: '600',
              fontSize: '12px'
            }}>
              Min Score
            </label>
            <input
              type="range"
              min="0"
              max="100"
              value={filters.minScore}
              onChange={(e) => setFilters({...filters, minScore: parseInt(e.target.value)})}
              style={{
                width: '100%',
                height: '40px'
              }}
            />
            <span style={{ fontSize: '12px', color: '#718096' }}>{filters.minScore}%</span>
          </div>

          <div>
            <label style={{
              display: 'block',
              marginBottom: '4px',
              color: '#2d3748',
              fontWeight: '600',
              fontSize: '12px'
            }}>
              Sort By
            </label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              style={{
                width: '100%',
                padding: '10px 12px',
                border: '2px solid #e2e8f0',
                borderRadius: '8px',
                fontSize: '14px',
                boxSizing: 'border-box'
              }}
            >
              <option value="score">Match Score</option>
              <option value="user_id">User ID</option>
            </select>
          </div>

          <div>
            <button
              onClick={() => {
                setSearchTerm('');
                setFilters({ skills: '', minScore: 0, location: '', experience: '' });
              }}
              style={{
                width: '100%',
                padding: '10px 12px',
                background: '#f7fafc',
                border: '1px solid #e2e8f0',
                borderRadius: '8px',
                cursor: 'pointer',
                fontWeight: '600',
                color: '#4f8cff'
              }}
            >
              Clear
            </button>
          </div>
        </div>
      </div>

      {/* Candidates Grid */}
      <div style={{ padding: '24px' }}>
        {filteredCandidates.length === 0 ? (
          <div style={{
            background: 'white',
            borderRadius: '12px',
            padding: '60px 20px',
            textAlign: 'center',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            border: '1px solid #e2e8f0'
          }}>
            <FiUsers size={48} color="#a0aec0" style={{ marginBottom: '16px' }} />
            <h3 style={{ color: '#2d3748', marginBottom: '8px' }}>No candidates found</h3>
            <p style={{ color: '#718096', margin: 0 }}>
              Try adjusting your search criteria or reindex the database
            </p>
          </div>
        ) : (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(400px, 1fr))',
            gap: '20px'
          }}>
            {filteredCandidates.map((candidate, index) => (
              <motion.div
                key={candidate.user_id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                style={{
                  background: 'white',
                  borderRadius: '12px',
                  padding: '20px',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                  border: selectedCandidates.includes(candidate.user_id) 
                    ? '2px solid #4f8cff' 
                    : '1px solid #e2e8f0',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease'
                }}
                onClick={() => handleCandidateSelect(candidate.user_id)}
              >
                {/* Header */}
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: '12px'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div style={{
                      width: '40px',
                      height: '40px',
                      background: 'linear-gradient(135deg, #4f8cff, #6366f1)',
                      borderRadius: '10px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: 'white',
                      fontWeight: '700',
                      fontSize: '16px'
                    }}>
                      {candidate.user_id.toString().slice(-2)}
                    </div>
                    <div>
                      <h3 style={{
                        fontSize: '16px',
                        fontWeight: '600',
                        color: '#1a202c',
                        margin: 0
                      }}>
                        {candidate.name || `Candidate #${candidate.user_id}`}
                      </h3>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{
                          fontSize: '12px',
                          color: candidate.added_by_recruiter ? '#8b5cf6' : '#10b981',
                          fontWeight: '600',
                          padding: '2px 6px',
                          background: candidate.added_by_recruiter ? '#f3e8ff' : '#d1fae5',
                          borderRadius: '8px'
                        }}>
                          {candidate.source}
                        </span>
                        {candidate.learning_progress > 0 && (
                          <span style={{
                            fontSize: '11px',
                            color: '#059669',
                            fontWeight: '600'
                          }}>
                            {candidate.learning_progress.toFixed(0)}% Progress
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{
                      padding: '4px 8px',
                      background: candidate.score > 0.7 ? '#d1fae5' : candidate.score > 0.5 ? '#fef3c7' : '#fee2e2',
                      color: candidate.score > 0.7 ? '#065f46' : candidate.score > 0.5 ? '#92400e' : '#991b1b',
                      borderRadius: '12px',
                      fontSize: '12px',
                      fontWeight: '600'
                    }}>
                      {(candidate.score * 100).toFixed(0)}%
                    </span>
                    {selectedCandidates.includes(candidate.user_id) && (
                      <FiStar size={16} color="#4f8cff" />
                    )}
                  </div>
                </div>

                {/* Summary */}
                <p style={{
                  color: '#718096',
                  fontSize: '14px',
                  lineHeight: '1.5',
                  margin: '0 0 12px',
                  display: '-webkit-box',
                  WebkitLineClamp: 3,
                  WebkitBoxOrient: 'vertical',
                  overflow: 'hidden'
                }}>
                  {candidate.summary || 'No summary available'}
                </p>

                {/* Skills */}
                <div style={{
                  display: 'flex',
                  flexWrap: 'wrap',
                  gap: '6px',
                  marginBottom: '16px'
                }}>
                  {(candidate.skills_tags || []).slice(0, 6).map((skill, i) => (
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
                      {skill}
                    </span>
                  ))}
                  {(candidate.skills_tags || []).length > 6 && (
                    <span style={{
                      padding: '4px 8px',
                      background: '#f3f4f6',
                      color: '#6b7280',
                      borderRadius: '12px',
                      fontSize: '12px'
                    }}>
                      +{(candidate.skills_tags || []).length - 6} more
                    </span>
                  )}
                </div>

                {/* Actions */}
                <div style={{
                  display: 'flex',
                  gap: '8px',
                  paddingTop: '12px',
                  borderTop: '1px solid #f3f4f6'
                }}>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      navigate(`/recruiter/candidate/${candidate.user_id}`);
                    }}
                    style={{
                      flex: 1,
                      padding: '8px 12px',
                      background: '#4f8cff',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      fontSize: '12px',
                      fontWeight: '600',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '4px'
                    }}
                  >
                    <FiEye size={12} />
                    View
                  </button>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleBulkAction('send-email');
                    }}
                    style={{
                      padding: '8px',
                      background: '#10b981',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: 'pointer'
                    }}
                  >
                    <FiMail size={12} />
                  </button>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleBulkAction('linkedin-enrich');
                    }}
                    style={{
                      padding: '8px',
                      background: '#0077b5',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: 'pointer'
                    }}
                  >
                    <FiLinkedin size={12} />
                  </button>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleBulkAction('schedule-interview');
                    }}
                    style={{
                      padding: '8px',
                      background: '#8b5cf6',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: 'pointer'
                    }}
                  >
                    <FiCalendar size={12} />
                  </button>
                </div>
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
    </div>
  );
};

export default RecruiterCandidates;