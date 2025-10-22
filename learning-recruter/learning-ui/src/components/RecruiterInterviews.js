import React, { useState, useEffect } from 'react';

const RecruiterInterviews = () => {
  const [interviews, setInterviews] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadInterviews();
  }, []);

  const loadInterviews = async () => {
    try {
      const token = localStorage.getItem('recruiter_token') || localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/recruiter/interviews/upcoming', {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setInterviews(data.interviews || []);
      }
    } catch (error) {
      console.error('Error loading interviews:', error);
    } finally {
      setLoading(false);
    }
  };

  const cancelInterview = async (eventId, title) => {
    const reason = prompt(`Cancel interview: ${title}\n\nReason for cancellation (optional):`);
    if (reason === null) return; // User clicked cancel

    try {
      const token = localStorage.getItem('recruiter_token') || localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/recruiter/interviews/${eventId}/cancel`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ reason })
      });

      const result = await response.json();
      
      if (result.success) {
        alert('✅ Interview cancelled successfully');
        loadInterviews(); // Refresh list
      } else {
        alert('❌ Error: ' + (result.error || 'Failed to cancel interview'));
      }
    } catch (error) {
      console.error('Error cancelling interview:', error);
      alert('❌ Error cancelling interview: ' + error.message);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <div style={{
          width: '40px',
          height: '40px',
          border: '4px solid #e2e8f0',
          borderTop: '4px solid #4f8cff',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite',
          margin: '0 auto 16px'
        }} />
        Loading interviews...
      </div>
    );
  }

  return (
    <div style={{ padding: '20px' }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '24px'
      }}>
        <h2 style={{ margin: 0, color: '#1a202c' }}>
          📅 Upcoming Interviews ({interviews.length})
        </h2>
        <button
          onClick={loadInterviews}
          style={{
            padding: '8px 16px',
            border: '1px solid #e2e8f0',
            borderRadius: '4px',
            backgroundColor: 'white',
            cursor: 'pointer'
          }}
        >
          🔄 Refresh
        </button>
      </div>

      {interviews.length === 0 ? (
        <div style={{
          textAlign: 'center',
          padding: '40px',
          backgroundColor: '#f7fafc',
          borderRadius: '8px',
          border: '1px solid #e2e8f0'
        }}>
          <h3 style={{ color: '#4a5568', margin: '0 0 8px 0' }}>
            No upcoming interviews
          </h3>
          <p style={{ color: '#718096', margin: 0 }}>
            Schedule interviews with shortlisted candidates to see them here.
          </p>
        </div>
      ) : (
        <div style={{
          display: 'grid',
          gap: '16px',
          gridTemplateColumns: 'repeat(auto-fill, minmax(400px, 1fr))'
        }}>
          {interviews.map((interview) => (
            <div
              key={interview.event_id}
              style={{
                backgroundColor: 'white',
                border: '1px solid #e2e8f0',
                borderRadius: '8px',
                padding: '20px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
              }}
            >
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'flex-start',
                marginBottom: '16px'
              }}>
                <h3 style={{
                  margin: '0 0 8px 0',
                  color: '#1a202c',
                  fontSize: '18px'
                }}>
                  {interview.title || 'Interview'}
                </h3>
                <span style={{
                  backgroundColor: '#e6fffa',
                  color: '#234e52',
                  padding: '4px 8px',
                  borderRadius: '4px',
                  fontSize: '12px',
                  fontWeight: '600'
                }}>
                  {interview.status || 'confirmed'}
                </span>
              </div>

              <div style={{ marginBottom: '16px' }}>
                <p style={{
                  margin: '4px 0',
                  color: '#4a5568',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  <span>📅</span>
                  <strong>{interview.formatted_time}</strong>
                </p>
                
                {interview.candidate && (
                  <p style={{
                    margin: '4px 0',
                    color: '#4a5568',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}>
                    <span>👤</span>
                    {interview.candidate.name} ({interview.candidate.email})
                  </p>
                )}

                {interview.description && (
                  <p style={{
                    margin: '8px 0',
                    color: '#718096',
                    fontSize: '14px',
                    lineHeight: '1.4'
                  }}>
                    {interview.description.substring(0, 150)}
                    {interview.description.length > 150 ? '...' : ''}
                  </p>
                )}
              </div>

              <div style={{
                display: 'flex',
                gap: '8px',
                flexWrap: 'wrap'
              }}>
                {interview.meet_link && (
                  <a
                    href={interview.meet_link}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      padding: '8px 12px',
                      backgroundColor: '#34a853',
                      color: 'white',
                      textDecoration: 'none',
                      borderRadius: '4px',
                      fontSize: '14px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px'
                    }}
                  >
                    🎥 Join Meet
                  </a>
                )}

                {interview.calendar_link && (
                  <a
                    href={interview.calendar_link}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      padding: '8px 12px',
                      backgroundColor: '#1a73e8',
                      color: 'white',
                      textDecoration: 'none',
                      borderRadius: '4px',
                      fontSize: '14px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px'
                    }}
                  >
                    📅 View in Calendar
                  </a>
                )}

                <button
                  onClick={() => cancelInterview(interview.event_id, interview.title)}
                  style={{
                    padding: '8px 12px',
                    backgroundColor: '#e53e3e',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    fontSize: '14px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px'
                  }}
                >
                  ❌ Cancel
                </button>
              </div>

              {interview.attendees && interview.attendees.length > 0 && (
                <div style={{ marginTop: '12px', paddingTop: '12px', borderTop: '1px solid #e2e8f0' }}>
                  <p style={{ margin: '0 0 4px 0', fontSize: '12px', color: '#718096' }}>
                    Attendees:
                  </p>
                  {interview.attendees.map((attendee, index) => (
                    <span
                      key={index}
                      style={{
                        display: 'inline-block',
                        backgroundColor: '#f7fafc',
                        padding: '2px 6px',
                        borderRadius: '3px',
                        fontSize: '12px',
                        color: '#4a5568',
                        marginRight: '4px',
                        marginBottom: '2px'
                      }}
                    >
                      {attendee.name || attendee.email}
                      {attendee.response_status === 'accepted' && ' ✅'}
                      {attendee.response_status === 'declined' && ' ❌'}
                      {attendee.response_status === 'tentative' && ' ❓'}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <style jsx>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default RecruiterInterviews;