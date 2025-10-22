import React, { useState } from 'react';

const InterviewScheduler = ({ candidate, onSchedule, onClose }) => {
  const [formData, setFormData] = useState({
    date: '',
    time: '',
    duration: 60,
    notes: ''
  });
  const [loading, setLoading] = useState(false);

  // Get today's date for min date
  const today = new Date().toISOString().split('T')[0];
  
  // Get current time + 1 hour for default time
  const defaultTime = new Date(Date.now() + 60 * 60 * 1000).toTimeString().slice(0, 5);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.date || !formData.time) {
      alert('Please select both date and time');
      return;
    }

    setLoading(true);
    
    try {
      const interviewDateTime = new Date(`${formData.date}T${formData.time}:00`);
      
      await onSchedule({
        interview_datetime: interviewDateTime.toISOString(),
        duration_minutes: parseInt(formData.duration),
        notes: formData.notes
      });
      
      onClose();
    } catch (error) {
      console.error('Error in form submission:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0,0,0,0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000
    }}>
      <div className="modal-content" style={{
        backgroundColor: 'white',
        padding: '24px',
        borderRadius: '8px',
        width: '90%',
        maxWidth: '500px',
        maxHeight: '90vh',
        overflow: 'auto'
      }}>
        <div className="modal-header" style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '20px',
          borderBottom: '1px solid #e2e8f0',
          paddingBottom: '16px'
        }}>
          <h2 style={{ margin: 0, color: '#1a202c' }}>
            📅 Schedule Interview
          </h2>
          <button 
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              fontSize: '24px',
              cursor: 'pointer',
              color: '#718096'
            }}
          >
            ×
          </button>
        </div>

        <div className="candidate-info" style={{
          backgroundColor: '#f7fafc',
          padding: '16px',
          borderRadius: '6px',
          marginBottom: '20px'
        }}>
          <h3 style={{ margin: '0 0 8px 0', color: '#2d3748' }}>
            👤 {candidate.name}
          </h3>
          <p style={{ margin: '4px 0', color: '#4a5568' }}>
            📧 {candidate.email}
          </p>
          <p style={{ margin: '4px 0', color: '#4a5568' }}>
            🎯 Match Score: {candidate.match_score}%
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group" style={{ marginBottom: '16px' }}>
            <label style={{
              display: 'block',
              marginBottom: '6px',
              fontWeight: '600',
              color: '#2d3748'
            }}>
              📅 Interview Date *
            </label>
            <input
              type="date"
              value={formData.date}
              min={today}
              onChange={(e) => setFormData({...formData, date: e.target.value})}
              required
              style={{
                width: '100%',
                padding: '8px 12px',
                border: '1px solid #e2e8f0',
                borderRadius: '4px',
                fontSize: '14px'
              }}
            />
          </div>

          <div className="form-group" style={{ marginBottom: '16px' }}>
            <label style={{
              display: 'block',
              marginBottom: '6px',
              fontWeight: '600',
              color: '#2d3748'
            }}>
              🕐 Interview Time *
            </label>
            <input
              type="time"
              value={formData.time}
              onChange={(e) => setFormData({...formData, time: e.target.value})}
              required
              style={{
                width: '100%',
                padding: '8px 12px',
                border: '1px solid #e2e8f0',
                borderRadius: '4px',
                fontSize: '14px'
              }}
            />
            <small style={{ color: '#718096', fontSize: '12px' }}>
              Time will be in UTC. Current time: {new Date().toLocaleTimeString()}
            </small>
          </div>

          <div className="form-group" style={{ marginBottom: '16px' }}>
            <label style={{
              display: 'block',
              marginBottom: '6px',
              fontWeight: '600',
              color: '#2d3748'
            }}>
              ⏱️ Duration (minutes)
            </label>
            <select
              value={formData.duration}
              onChange={(e) => setFormData({...formData, duration: e.target.value})}
              style={{
                width: '100%',
                padding: '8px 12px',
                border: '1px solid #e2e8f0',
                borderRadius: '4px',
                fontSize: '14px'
              }}
            >
              <option value={30}>30 minutes</option>
              <option value={45}>45 minutes</option>
              <option value={60}>60 minutes</option>
              <option value={90}>90 minutes</option>
            </select>
          </div>

          <div className="form-group" style={{ marginBottom: '20px' }}>
            <label style={{
              display: 'block',
              marginBottom: '6px',
              fontWeight: '600',
              color: '#2d3748'
            }}>
              📝 Additional Notes (Optional)
            </label>
            <textarea
              value={formData.notes}
              onChange={(e) => setFormData({...formData, notes: e.target.value})}
              placeholder="Any specific topics to discuss, preparation instructions, etc."
              rows={3}
              style={{
                width: '100%',
                padding: '8px 12px',
                border: '1px solid #e2e8f0',
                borderRadius: '4px',
                fontSize: '14px',
                resize: 'vertical'
              }}
            />
          </div>

          <div className="interview-features" style={{
            backgroundColor: '#e6fffa',
            padding: '12px',
            borderRadius: '6px',
            marginBottom: '20px',
            border: '1px solid #81e6d9'
          }}>
            <h4 style={{ margin: '0 0 8px 0', color: '#234e52' }}>
              ✨ What happens next:
            </h4>
            <ul style={{ margin: 0, paddingLeft: '20px', color: '#2c7a7b' }}>
              <li>Google Meet link will be automatically created</li>
              <li>Calendar invitation sent to both parties</li>
              <li>Email notification sent to candidate</li>
              <li>Automatic reminders 24 hours and 30 minutes before</li>
            </ul>
          </div>

          <div className="form-actions" style={{
            display: 'flex',
            gap: '12px',
            justifyContent: 'flex-end'
          }}>
            <button
              type="button"
              onClick={onClose}
              disabled={loading}
              style={{
                padding: '10px 20px',
                border: '1px solid #e2e8f0',
                borderRadius: '4px',
                backgroundColor: 'white',
                color: '#4a5568',
                cursor: 'pointer'
              }}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              style={{
                padding: '10px 20px',
                border: 'none',
                borderRadius: '4px',
                backgroundColor: loading ? '#a0aec0' : '#34a853',
                color: 'white',
                cursor: loading ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}
            >
              {loading ? (
                <>
                  <div style={{
                    width: '16px',
                    height: '16px',
                    border: '2px solid #ffffff40',
                    borderTop: '2px solid #ffffff',
                    borderRadius: '50%',
                    animation: 'spin 1s linear infinite'
                  }} />
                  Scheduling...
                </>
              ) : (
                <>
                  🎥 Schedule Google Meet
                </>
              )}
            </button>
          </div>
        </form>

        <style jsx>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    </div>
  );
};

export default InterviewScheduler;