import React, { useState, useEffect } from 'react';
import { authenticatedFetch } from '../api';
import { FaTrophy, FaChartLine, FaCalendarAlt, FaSpinner, FaCheckCircle, FaTimesCircle } from 'react-icons/fa';

const Progress = () => {
  const [quizData, setQuizData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchQuizProgress();
  }, []);

  const fetchQuizProgress = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await authenticatedFetch('/quiz/progress');
      setQuizData(data);
    } catch (err) {
      console.error('Error fetching quiz progress:', err);
      setError('Failed to load quiz progress. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return '#28a745';
    if (score >= 60) return '#ffc107';
    return '#dc3545';
  };

  const getPerformanceLevel = (score) => {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    return 'Needs Improvement';
  };

  if (loading) {
    return (
      <div style={{ padding: 32, textAlign: 'center' }}>
        <FaSpinner style={{ fontSize: 32, color: '#4f8cff', animation: 'spin 1s linear infinite' }} />
        <p>Loading your progress...</p>
        <style>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: 32, textAlign: 'center', color: '#dc3545' }}>
        <h2>Error</h2>
        <p>{error}</p>
        <button 
          onClick={fetchQuizProgress}
          style={{
            padding: '8px 16px',
            background: '#4f8cff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Try Again
        </button>
      </div>
    );
  }

  if (!quizData || !quizData.submissions || quizData.submissions.length === 0) {
    return (
      <div style={{ padding: 32, textAlign: 'center' }}>
        <h2>No Quiz Data</h2>
        <p>You haven't taken any quizzes yet. Start learning to see your progress!</p>
      </div>
    );
  }

  const avgScore = quizData.submissions.reduce((sum, quiz) => sum + quiz.score, 0) / quizData.submissions.length;
  const passedQuizzes = quizData.submissions.filter(quiz => quiz.passed).length;
  const passRate = (passedQuizzes / quizData.submissions.length) * 100;

  const totalDaysCompleted = quizData.month_progress ? quizData.month_progress.reduce((sum, month) => sum + month.days_completed, 0) : 0;
  const totalDays = quizData.month_progress ? quizData.month_progress.reduce((sum, month) => sum + month.total_days, 0) : 0;
  const completedMonths = quizData.month_progress ? quizData.month_progress.filter(m => m.status === 'completed').length : 0;
  const totalMonths = quizData.month_progress ? quizData.month_progress.length : 0;
  const overallProgress = quizData.learning_progress_percentage || 0;

  return (
    <div style={{ padding: 32, maxWidth: 1200, margin: '0 auto' }}>
      <h1 style={{ marginBottom: 24, color: '#333' }}>Learning Progress & Performance</h1>
      
      {/* Current Position */}
      {quizData.current_position && (
        <div style={{ 
          background: 'linear-gradient(135deg, #4f8cff, #6d9eff)', 
          padding: 24, 
          borderRadius: 12,
          color: 'white',
          marginBottom: 32,
          boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
        }}>
          <h2 style={{ marginTop: 0 }}>{quizData.current_position.plan_title}</h2>
          <div style={{ display: 'flex', gap: 24, flexWrap: 'wrap' }}>
            <div>
              <h3 style={{ fontSize: 16, opacity: 0.9, margin: '0 0 8px 0' }}>
                <FaCalendarAlt style={{ marginRight: 8 }} />
                Current Position
              </h3>
              <p style={{ fontSize: 20, fontWeight: 'bold', margin: 0 }}>
                Month {quizData.current_position.current_month_index}, Day {quizData.current_position.current_day}
              </p>
            </div>
            <div>
              <h3 style={{ fontSize: 16, opacity: 0.9, margin: '0 0 8px 0' }}>
                <FaCheckCircle style={{ marginRight: 8 }} />
                Overall Progress
              </h3>
              <p style={{ fontSize: 20, fontWeight: 'bold', margin: 0 }}>
                {Math.round(overallProgress)}%
              </p>
            </div>
          </div>
        </div>
      )}
      
      {/* Overview Stats */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', 
        gap: 16, 
        marginBottom: 32 
      }}>
        <div style={{
          background: 'linear-gradient(135deg, #4f8cff, #6d9eff)',
          padding: 20,
          borderRadius: 12,
          color: 'white',
          textAlign: 'center',
          boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
        }}>
          <FaTrophy style={{ fontSize: 28, marginBottom: 8 }} />
          <h3 style={{ margin: 0, fontSize: 24, fontWeight: 'bold' }}>{Math.round(avgScore)}%</h3>
          <p style={{ margin: 0, opacity: 0.9, fontSize: 14 }}>Quiz Average</p>
        </div>
        
        <div style={{
          background: 'linear-gradient(135deg, #28a745, #20c997)',
          padding: 20,
          borderRadius: 12,
          color: 'white',
          textAlign: 'center',
          boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
        }}>
          <FaCheckCircle style={{ fontSize: 28, marginBottom: 8 }} />
          <h3 style={{ margin: 0, fontSize: 24, fontWeight: 'bold' }}>{totalDaysCompleted}</h3>
          <p style={{ margin: 0, opacity: 0.9, fontSize: 14 }}>Days Completed</p>
        </div>
        
        <div style={{
          background: 'linear-gradient(135deg, #ffc107, #fd7e14)',
          padding: 20,
          borderRadius: 12,
          color: 'white',
          textAlign: 'center',
          boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
        }}>
          <FaChartLine style={{ fontSize: 28, marginBottom: 8 }} />
          <h3 style={{ margin: 0, fontSize: 24, fontWeight: 'bold' }}>{completedMonths}</h3>
          <p style={{ margin: 0, opacity: 0.9, fontSize: 14 }}>Months Done</p>
        </div>
        
        <div style={{
          background: 'linear-gradient(135deg, #6f42c1, #e83e8c)',
          padding: 20,
          borderRadius: 12,
          color: 'white',
          textAlign: 'center',
          boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
        }}>
          <FaCalendarAlt style={{ fontSize: 28, marginBottom: 8 }} />
          <h3 style={{ margin: 0, fontSize: 24, fontWeight: 'bold' }}>{passedQuizzes}</h3>
          <p style={{ margin: 0, opacity: 0.9, fontSize: 14 }}>Quizzes Passed</p>
        </div>
        
        <div style={{
          background: 'linear-gradient(135deg, #17a2b8, #6f42c1)',
          padding: 20,
          borderRadius: 12,
          color: 'white',
          textAlign: 'center',
          boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
        }}>
          <FaCheckCircle style={{ fontSize: 28, marginBottom: 8 }} />
          <h3 style={{ margin: 0, fontSize: 24, fontWeight: 'bold' }}>{Math.round(passRate)}%</h3>
          <p style={{ margin: 0, opacity: 0.9, fontSize: 14 }}>Pass Rate</p>
        </div>
      </div>

      {/* Performance Chart */}
      <div style={{
        background: 'white',
        padding: 24,
        borderRadius: 12,
        boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
        marginBottom: 32
      }}>
        <h2 style={{ marginBottom: 20 }}>Score Trend</h2>
        <div style={{ 
          display: 'flex', 
          alignItems: 'end', 
          gap: 8, 
          height: 200, 
          padding: '0 20px 20px 0',
          borderBottom: '2px solid #e9ecef',
          borderLeft: '2px solid #e9ecef'
        }}>
          {quizData.submissions.map((quiz, index) => (
            <div key={index} style={{ 
              display: 'flex', 
              flexDirection: 'column', 
              alignItems: 'center',
              flex: 1,
              minWidth: 40
            }}>
              <div style={{
                background: getScoreColor(quiz.score),
                height: `${(quiz.score / 100) * 160}px`,
                width: '100%',
                maxWidth: 30,
                borderRadius: '4px 4px 0 0',
                position: 'relative',
                display: 'flex',
                alignItems: 'end',
                justifyContent: 'center',
                color: 'white',
                fontSize: 12,
                fontWeight: 'bold',
                paddingBottom: 4
              }}>
                {quiz.score}%
              </div>
              <div style={{
                fontSize: 10,
                color: '#666',
                marginTop: 8,
                textAlign: 'center',
                transform: 'rotate(-45deg)',
                transformOrigin: 'center'
              }}>
                M{quiz.month_index}D{quiz.day}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Month Progress */}
      {quizData.month_progress && quizData.month_progress.length > 0 && (
        <div style={{
          background: 'white',
          padding: 24,
          borderRadius: 12,
          boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
          marginBottom: 32
        }}>
          <h2 style={{ marginBottom: 20 }}>Monthly Progress</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 16 }}>
            {quizData.month_progress.map((month) => (
              <div key={month.index} style={{
                padding: 16,
                border: '1px solid #e9ecef',
                borderRadius: 8,
                background: month.status === 'completed' ? '#f8fff9' : month.status === 'in_progress' ? '#fff8e1' : '#f8f9fa'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                  <h4 style={{ margin: 0, color: '#333' }}>{month.title}</h4>
                  <span style={{
                    padding: '4px 8px',
                    borderRadius: 12,
                    fontSize: 12,
                    background: month.status === 'completed' ? '#28a745' : month.status === 'in_progress' ? '#ffc107' : '#6c757d',
                    color: 'white'
                  }}>
                    {month.status === 'completed' ? 'Completed' : month.status === 'in_progress' ? 'In Progress' : 'Not Started'}
                  </span>
                </div>
                <div style={{ marginBottom: 8 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                    <span style={{ fontSize: 14 }}>Progress</span>
                    <span style={{ fontSize: 14, fontWeight: 'bold' }}>{month.days_completed}/{month.total_days} days</span>
                  </div>
                  <div style={{
                    height: 8,
                    background: '#e9ecef',
                    borderRadius: 4,
                    overflow: 'hidden'
                  }}>
                    <div style={{
                      height: '100%',
                      width: `${month.progress_percentage}%`,
                      background: month.status === 'completed' ? '#28a745' : month.status === 'in_progress' ? '#ffc107' : '#6c757d',
                      borderRadius: 4
                    }} />
                  </div>
                </div>
                <p style={{ margin: 0, fontSize: 14, color: '#666' }}>
                  {Math.round(month.progress_percentage)}% Complete
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Quiz Details */}
      <div style={{
        background: 'white',
        padding: 24,
        borderRadius: 12,
        boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
      }}>
        <h2 style={{ marginBottom: 20 }}>Quiz History</h2>
        <div style={{ display: 'grid', gap: 16 }}>
          {quizData.submissions.map((quiz, index) => (
            <div key={index} style={{
              padding: 16,
              border: '1px solid #e9ecef',
              borderRadius: 8,
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              background: quiz.passed ? '#f8fff9' : '#fff5f5'
            }}>
              <div>
                <h4 style={{ margin: '0 0 8px 0', color: '#333' }}>
                  Month {quiz.month_index}, Day {quiz.day}
                </h4>
                <p style={{ margin: 0, color: '#666', fontSize: 14 }}>
                  Completed: {new Date(quiz.created_at).toLocaleDateString()}
                </p>
              </div>
              
              <div style={{ textAlign: 'right' }}>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  marginBottom: 8
                }}>
                  {quiz.passed ? (
                    <FaCheckCircle style={{ color: '#28a745' }} />
                  ) : (
                    <FaTimesCircle style={{ color: '#dc3545' }} />
                  )}
                  <span style={{
                    fontSize: 20,
                    fontWeight: 'bold',
                    color: getScoreColor(quiz.score)
                  }}>
                    {quiz.score}%
                  </span>
                </div>
                <span style={{
                  fontSize: 12,
                  padding: '4px 8px',
                  borderRadius: 12,
                  background: getScoreColor(quiz.score),
                  color: 'white'
                }}>
                  {getPerformanceLevel(quiz.score)}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Progress;