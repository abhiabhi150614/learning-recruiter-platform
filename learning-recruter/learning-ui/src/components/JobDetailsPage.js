import React, { useState, useEffect } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import InterviewScheduler from './InterviewScheduler';
import './JobDetailsPage.css';

const JobDetailsPage = () => {
  const { jobId } = useParams();
  const [searchParams] = useSearchParams();
  const [activeTab, setActiveTab] = useState(searchParams.get('tab') || 'matches');
  const [job, setJob] = useState(null);
  const [matches, setMatches] = useState([]);
  const [shortlisted, setShortlisted] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showScheduler, setShowScheduler] = useState(false);
  const [selectedCandidate, setSelectedCandidate] = useState(null);

  useEffect(() => {
    if (jobId) {
      loadJobDetails();
      loadMatches();
      loadShortlisted();
    }
  }, [jobId]);

  const loadJobDetails = async () => {
    try {
      const token = localStorage.getItem('recruiter_token') || localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/recruiter/jobs/${jobId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Job data:', data); // Debug log
      setJob(data);
    } catch (error) {
      console.error('Error loading job:', error);
      alert('Error loading job details: ' + error.message);
    }
  };

  const loadMatches = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('recruiter_token') || localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/recruiter/jobs/${jobId}/matches`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Matches data:', data); // Debug log
      setMatches(data.matches || []);
      
      // Update job details if available
      if (data.job) {
        setJob(data.job);
      }
    } catch (error) {
      console.error('Error loading matches:', error);
      alert('Error loading matches: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const loadShortlisted = async () => {
    try {
      const token = localStorage.getItem('recruiter_token') || localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/recruiter/jobs/${jobId}/shortlisted`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setShortlisted(data.shortlisted_candidates || []);
    } catch (error) {
      console.error('Error loading shortlisted:', error);
    }
  };

  const addToShortlist = async (candidate) => {
    try {
      const token = localStorage.getItem('recruiter_token') || localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/recruiter/shortlist', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          job_id: parseInt(jobId),
          student_id: candidate.user_id,
          match_score: candidate.score,
          notes: `Added from AI matching with ${candidate.score}% match`
        })
      });

      if (response.ok) {
        // Update matches to show as shortlisted
        setMatches(prev => prev.map(m => 
          m.user_id === candidate.user_id ? { ...m, shortlisted: true } : m
        ));
        // Reload shortlisted candidates
        loadShortlisted();
        alert('Candidate added to shortlist!');
      } else {
        const errorData = await response.json();
        alert('Error: ' + (errorData.detail || 'Failed to add candidate'));
      }
    } catch (error) {
      console.error('Error adding to shortlist:', error);
      alert('Error adding candidate to shortlist: ' + error.message);
    }
  };

  const removeFromShortlist = async (shortlistId) => {
    try {
      const token = localStorage.getItem('recruiter_token') || localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/recruiter/shortlist/${shortlistId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        loadShortlisted();
        loadMatches(); // Refresh to update shortlisted status
        alert('Candidate removed from shortlist');
      } else {
        const errorData = await response.json();
        alert('Error: ' + (errorData.detail || 'Failed to remove candidate'));
      }
    } catch (error) {
      console.error('Error removing from shortlist:', error);
    }
  };

  const openScheduler = (candidate) => {
    setSelectedCandidate(candidate);
    setShowScheduler(true);
  };

  const handleScheduleInterview = async (scheduleData) => {
    try {
      const token = localStorage.getItem('recruiter_token') || localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/recruiter/shortlist/${selectedCandidate.shortlist_id}/schedule-interview`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(scheduleData)
      });

      const result = await response.json();
      
      if (result.success) {
        alert(`✅ Interview scheduled successfully!\n\n📅 ${new Date(result.interview_details.datetime).toLocaleString()}\n🎥 Google Meet: ${result.interview_details.meet_link}\n📧 Invitation sent: ${result.email_sent ? 'Yes' : 'No'}`);
        loadShortlisted(); // Refresh to show updated status
        setShowScheduler(false);
      } else {
        if (result.suggested_times && result.suggested_times.length > 0) {
          const suggestions = result.suggested_times.map(t => t.formatted).join('\n');
          alert(`❌ Time slot not available\n\n🕒 Suggested times:\n${suggestions}`);
        } else {
          alert('❌ Error: ' + (result.error || 'Failed to schedule interview'));
        }
      }
    } catch (error) {
      console.error('Error scheduling interview:', error);
      alert('❌ Error scheduling interview: ' + error.message);
    }
  };

  if (!job) {
    return <div className="loading">Loading job details...</div>;
  }

  return (
    <div className="job-details-page">
      <div className="job-header">
        <h1>{job.title}</h1>
        <div className="job-info">
          <p><strong>Location:</strong> {job.location || 'Not specified'}</p>
          <p><strong>Salary:</strong> {job.salary_range || 'Not specified'}</p>
          <p><strong>Posted:</strong> {new Date(job.created_at).toLocaleDateString()}</p>
        </div>
        <div className="job-description">
          <h3>Job Description</h3>
          <p>{job.description}</p>
          {job.requirements && job.requirements.length > 0 && (
            <div>
              <h4>Requirements:</h4>
              <ul>
                {job.requirements.map((req, index) => (
                  <li key={index}>{req}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      <div className="job-tabs">
        <div className="tab-buttons">
          <button 
            className={activeTab === 'matches' ? 'active' : ''}
            onClick={() => setActiveTab('matches')}
          >
            Find Matches ({matches.length})
          </button>
          <button 
            className={activeTab === 'shortlisted' ? 'active' : ''}
            onClick={() => setActiveTab('shortlisted')}
          >
            Shortlisted Candidates ({shortlisted.length})
          </button>
        </div>

        <div className="tab-content">
          {activeTab === 'matches' && (
            <div className="matches-tab">
              <div className="tab-header">
                <h3>AI-Matched Candidates</h3>
                <button 
                  onClick={() => {
                    console.log('🔄 Refresh button clicked');
                    loadMatches();
                  }} 
                  className="refresh-btn"
                  disabled={loading}
                >
                  {loading ? '⏳ Finding...' : '🔄 Refresh Matches'}
                </button>
                <button 
                  onClick={async () => {
                    const token = localStorage.getItem('recruiter_token') || localStorage.getItem('token');
                    try {
                      const response = await fetch(`http://localhost:8000/recruiter/test-matches/${jobId}`, {
                        headers: { 'Authorization': `Bearer ${token}` }
                      });
                      const data = await response.json();
                      console.log('Test result:', data);
                      alert('Backend test: ' + JSON.stringify(data));
                    } catch (error) {
                      console.error('Test failed:', error);
                      alert('Backend test failed: ' + error.message);
                    }
                  }}
                  className="refresh-btn"
                  style={{ marginLeft: '10px', background: '#28a745' }}
                >
                  🧪 Test Backend
                </button>
              </div>
              
              {loading ? (
                <div className="loading">
                  <div style={{
                    width: '48px',
                    height: '48px',
                    border: '4px solid #e2e8f0',
                    borderTop: '4px solid #4f8cff',
                    borderRadius: '50%',
                    animation: 'spin 1s linear infinite',
                    margin: '0 auto 16px'
                  }} />
                  Finding best matches using AI...
                </div>
              ) : matches.length === 0 ? (
                <div className="empty-state">
                  <p>No matches found. Click "Refresh Matches" to search for candidates.</p>
                </div>
              ) : (
                <div className="candidates-grid">
                  {matches.map((candidate) => (
                    <div key={candidate.user_id} className="candidate-card">
                      <div className="candidate-header">
                        <h4>{candidate.name}</h4>
                        <div className={`match-score score-${Math.floor(candidate.score / 10) * 10}`}>
                          {candidate.score}% Match
                        </div>
                      </div>
                      
                      <div className="candidate-info">
                        <p><strong>Email:</strong> {candidate.email}</p>
                        <p><strong>Skills:</strong> {candidate.skills}</p>
                        <p><strong>Career Goals:</strong> {candidate.career_goals}</p>
                        <p><strong>Quiz Performance:</strong> {candidate.avg_quiz_score}%</p>
                        <p><strong>Learning Progress:</strong> {candidate.learning_progress}%</p>
                        {candidate.github_skills && candidate.github_skills.length > 0 && (
                          <p><strong>GitHub Skills:</strong> {candidate.github_skills.join(', ')}</p>
                        )}
                      </div>
                      
                      <div className="match-explanation">
                        <p><strong>AI Analysis:</strong> {candidate.match_explanation}</p>
                      </div>
                      
                      <div className="candidate-actions">
                        {candidate.shortlisted ? (
                          <button className="shortlisted-btn" disabled>
                            ✓ Already Shortlisted
                          </button>
                        ) : (
                          <button 
                            className="add-shortlist-btn"
                            onClick={() => addToShortlist(candidate)}
                          >
                            + Add to Shortlist
                          </button>
                        )}
                        <span className={`recommendation ${candidate.recommendation.toLowerCase().replace(' ', '-')}`}>
                          {candidate.recommendation}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'shortlisted' && (
            <div className="shortlisted-tab">
              <div className="tab-header">
                <h3>Shortlisted Candidates</h3>
                <button onClick={loadShortlisted} className="refresh-btn">
                  🔄 Refresh
                </button>
              </div>
              
              <div className="candidates-grid">
                {shortlisted.map((candidate) => (
                  <div key={candidate.shortlist_id} className="candidate-card shortlisted">
                    <div className="candidate-header">
                      <h4>{candidate.name}</h4>
                      <div className="match-score">
                        {candidate.match_score}% Match
                      </div>
                    </div>
                    
                    <div className="candidate-info">
                      <p><strong>Email:</strong> {candidate.email}</p>
                      <p><strong>Skills:</strong> {candidate.skills}</p>
                      <p><strong>Career Goals:</strong> {candidate.career_goals}</p>
                      <p><strong>Status:</strong> {candidate.status}</p>
                      <p><strong>Shortlisted:</strong> {new Date(candidate.shortlisted_at).toLocaleDateString()}</p>
                    </div>
                    
                    {candidate.notes && (
                      <div className="notes">
                        <p><strong>Notes:</strong> {candidate.notes}</p>
                      </div>
                    )}
                    
                    <div className="candidate-actions">
                      <button 
                        className="invite-meet-btn"
                        onClick={() => openScheduler(candidate)}
                        style={{
                          background: '#34a853',
                          color: 'white',
                          border: 'none',
                          padding: '8px 16px',
                          borderRadius: '4px',
                          cursor: 'pointer',
                          marginRight: '8px'
                        }}
                      >
                        📅 Invite to Google Meet
                      </button>
                      <button 
                        className="remove-btn"
                        onClick={() => removeFromShortlist(candidate.shortlist_id)}
                      >
                        Remove from Shortlist
                      </button>
                      <button className="view-profile-btn">
                        View Full Profile
                      </button>
                    </div>
                  </div>
                ))}
              </div>
              
              {shortlisted.length === 0 && (
                <div className="empty-state">
                  <p>No candidates shortlisted yet. Go to "Find Matches" to discover potential candidates!</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
      
      {showScheduler && selectedCandidate && (
        <InterviewScheduler
          candidate={selectedCandidate}
          onSchedule={handleScheduleInterview}
          onClose={() => setShowScheduler(false)}
        />
      )}
    </div>
  );
};

export default JobDetailsPage;