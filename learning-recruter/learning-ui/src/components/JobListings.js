import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { recruiterAuthenticatedFetch } from '../api';
import RecruiterLayout from './RecruiterLayout';
import { FiBriefcase, FiMapPin, FiDollarSign, FiCalendar, FiEye, FiUsers, FiTarget } from 'react-icons/fi';

const JobListings = () => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadJobs();
  }, []);

  const loadJobs = async () => {
    try {
      setLoading(true);
      const data = await recruiterAuthenticatedFetch('/recruiter/jobs');
      setJobs(data.jobs || []);
    } catch (error) {
      console.error('Error loading jobs:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <RecruiterLayout>
        <div style={{ padding: '40px', textAlign: 'center' }}>
          <div style={{
            width: '48px',
            height: '48px',
            border: '4px solid #e2e8f0',
            borderTop: '4px solid #4f8cff',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 16px'
          }} />
          <p>Loading your job postings...</p>
        </div>
      </RecruiterLayout>
    );
  }

  return (
    <RecruiterLayout>
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '32px' }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '32px'
        }}>
          <div>
            <h1 style={{ fontSize: '32px', fontWeight: '700', color: '#1a202c', margin: '0 0 8px' }}>
              My Job Postings
            </h1>
            <p style={{ color: '#718096', margin: 0 }}>
              Manage your job postings and find the best candidates
            </p>
          </div>
          <button
            onClick={() => navigate('/recruiter/post-job')}
            style={{
              background: 'linear-gradient(135deg, #4f8cff, #6366f1)',
              color: 'white',
              border: 'none',
              padding: '12px 24px',
              borderRadius: '12px',
              cursor: 'pointer',
              fontSize: '16px',
              fontWeight: '600',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              boxShadow: '0 4px 15px rgba(79, 140, 255, 0.3)'
            }}
          >
            <FiBriefcase size={20} />
            Post New Job
          </button>
        </div>

        {jobs.length === 0 ? (
          <div style={{
            background: 'white',
            borderRadius: '16px',
            padding: '60px',
            textAlign: 'center',
            boxShadow: '0 4px 6px rgba(0,0,0,0.05)'
          }}>
            <FiBriefcase size={64} color="#cbd5e0" style={{ marginBottom: '16px' }} />
            <h3 style={{ fontSize: '24px', color: '#1a202c', margin: '0 0 12px' }}>
              No Job Postings Yet
            </h3>
            <p style={{ color: '#718096', marginBottom: '24px' }}>
              Create your first job posting to start finding great candidates
            </p>
            <button
              onClick={() => navigate('/recruiter/post-job')}
              style={{
                background: '#4f8cff',
                color: 'white',
                border: 'none',
                padding: '12px 24px',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '16px',
                fontWeight: '600'
              }}
            >
              Create Job Posting
            </button>
          </div>
        ) : (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(400px, 1fr))',
            gap: '24px'
          }}>
            {jobs.map((job) => (
              <div
                key={job.id}
                style={{
                  background: 'white',
                  borderRadius: '16px',
                  padding: '24px',
                  boxShadow: '0 4px 6px rgba(0,0,0,0.05)',
                  border: '1px solid #e2e8f0',
                  transition: 'all 0.3s ease',
                  cursor: 'pointer'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-4px)';
                  e.currentTarget.style.boxShadow = '0 8px 25px rgba(0,0,0,0.1)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 4px 6px rgba(0,0,0,0.05)';
                }}
              >
                <div style={{ marginBottom: '20px' }}>
                  <h3 style={{
                    fontSize: '20px',
                    fontWeight: '700',
                    color: '#1a202c',
                    margin: '0 0 12px'
                  }}>
                    {job.title}
                  </h3>
                  
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '16px', marginBottom: '16px' }}>
                    {job.location && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <FiMapPin size={16} color="#718096" />
                        <span style={{ fontSize: '14px', color: '#718096' }}>{job.location}</span>
                      </div>
                    )}
                    {job.salary_range && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <FiDollarSign size={16} color="#718096" />
                        <span style={{ fontSize: '14px', color: '#718096' }}>{job.salary_range}</span>
                      </div>
                    )}
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <FiCalendar size={16} color="#718096" />
                      <span style={{ fontSize: '14px', color: '#718096' }}>
                        {new Date(job.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>

                  <p style={{
                    color: '#4a5568',
                    fontSize: '14px',
                    lineHeight: '1.5',
                    margin: '0 0 16px',
                    display: '-webkit-box',
                    WebkitLineClamp: 3,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden'
                  }}>
                    {job.description}
                  </p>

                  {job.requirements && job.requirements.length > 0 && (
                    <div style={{ marginBottom: '16px' }}>
                      <p style={{ fontSize: '12px', color: '#718096', margin: '0 0 8px', fontWeight: '600' }}>
                        KEY REQUIREMENTS:
                      </p>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                        {job.requirements.slice(0, 3).map((req, index) => (
                          <span
                            key={index}
                            style={{
                              background: '#f0f9ff',
                              color: '#0369a1',
                              padding: '4px 8px',
                              borderRadius: '6px',
                              fontSize: '12px',
                              fontWeight: '500'
                            }}
                          >
                            {req}
                          </span>
                        ))}
                        {job.requirements.length > 3 && (
                          <span style={{
                            color: '#718096',
                            fontSize: '12px',
                            padding: '4px 8px'
                          }}>
                            +{job.requirements.length - 3} more
                          </span>
                        )}
                      </div>
                    </div>
                  )}
                </div>

                <div style={{
                  display: 'flex',
                  gap: '12px',
                  paddingTop: '16px',
                  borderTop: '1px solid #e2e8f0'
                }}>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      navigate(`/recruiter/job/${job.id}`);
                    }}
                    style={{
                      flex: 1,
                      background: 'linear-gradient(135deg, #4f8cff, #6366f1)',
                      color: 'white',
                      border: 'none',
                      padding: '12px',
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
                    <FiTarget size={16} />
                    Find Matches
                  </button>
                  
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      navigate(`/recruiter/job/${job.id}?tab=shortlisted`);
                    }}
                    style={{
                      flex: 1,
                      background: 'white',
                      color: '#4f8cff',
                      border: '2px solid #4f8cff',
                      padding: '12px',
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
                    <FiUsers size={16} />
                    Shortlisted
                  </button>
                </div>
              </div>
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

export default JobListings;