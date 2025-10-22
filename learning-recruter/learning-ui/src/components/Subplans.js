import React, { useState } from 'react';
import { FaBookOpen, FaChartLine, FaClock, FaUsers, FaExternalLinkAlt, FaHeart, FaComment, FaRetweet, FaSave, FaEye } from 'react-icons/fa';
import Layout from './Layout';

const Subplans = () => {
  const [learningPath, setLearningPath] = useState(null);
  const [tweets, setTweets] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedTab, setSelectedTab] = useState('learning-path');
  const [connectionStatus, setConnectionStatus] = useState('unknown');
  const [expandedPath, setExpandedPath] = useState(false);
  const [savedPaths, setSavedPaths] = useState([]);

  const testConnection = async () => {
    try {
      const response = await fetch('http://localhost:8000/health');
      if (response.ok) {
        setConnectionStatus('connected');
      } else {
        setConnectionStatus('error');
      }
    } catch (error) {
      setConnectionStatus('disconnected');
    }
  };

  const saveLearningPath = async () => {
    if (!learningPath) return;
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/subplans/save-learning-path', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          learning_path: learningPath,
          title: learningPath.title
        })
      });
      
      const data = await response.json();
      if (data.success) {
        setSavedPaths([...savedPaths, learningPath]);
        alert('✅ Learning path saved successfully!');
      }
    } catch (error) {
      console.error('Save error:', error);
    }
  };

  // Learning Path Generator
  const [pathForm, setPathForm] = useState({
    topic: '',
    skill_level: 'beginner',
    duration_weeks: 12,
    hours_per_week: 10
  });

  // Trending Tweets
  const [tweetForm, setTweetForm] = useState({
    query: 'AI learning OR machine learning OR data science',
    max_results: 10
  });

  const trendingTopics = [
    {
      category: "🤖 AI & Machine Learning",
      queries: [
        "AI learning OR machine learning OR data science",
        "artificial intelligence OR deep learning OR neural networks",
        "python machine learning OR tensorflow OR pytorch"
      ]
    },
    {
      category: "💻 Programming",
      queries: [
        "python programming OR javascript OR react",
        "web development OR frontend OR backend",
        "coding tips OR programming tutorial"
      ]
    },
    {
      category: "📊 Data Science",
      queries: [
        "data science OR data analysis OR statistics",
        "pandas OR numpy OR matplotlib",
        "data visualization OR analytics"
      ]
    }
  ];

  const generateLearningPath = async () => {
    if (!pathForm.topic.trim()) {
      alert('Please enter a topic');
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      console.log('Sending request to generate learning path...');
      
      const response = await fetch('http://localhost:8000/subplans/generate-learning-path', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(pathForm)
      });

      console.log('Response status:', response.status);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Response error:', errorText);
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const data = await response.json();
      console.log('Response data:', data);
      
      if (data.success) {
        setLearningPath(data.learning_path);
        setExpandedPath(false);
        console.log('Learning path generated:', data.learning_path);
      } else {
        console.error('API returned success=false:', data);
        alert(`Failed to generate learning path: ${data.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Full error:', error);
      alert(`Error: ${error.message || 'Network error - check if backend is running on port 8000'}`);
    } finally {
      setLoading(false);
    }
  };

  const fetchTrendingTweets = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      console.log('Sending request to fetch tweets...');
      
      const response = await fetch('http://localhost:8000/subplans/trending-tweets', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(tweetForm)
      });

      console.log('Response status:', response.status);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Response error:', errorText);
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const data = await response.json();
      console.log('Response data:', data);
      
      if (data.success) {
        setTweets(data.tweets);
        console.log('Tweets fetched:', data.tweets);
      } else {
        console.error('API returned success=false:', data);
        alert(`Failed to fetch tweets: ${data.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Full error:', error);
      alert(`Error: ${error.message || 'Network error - check if backend is running on port 8000'}`);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <Layout>
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <h1 style={{ fontSize: '2rem', fontWeight: 'bold', color: '#333', marginBottom: '0.5rem' }}>Learning Subplans</h1>
          <p style={{ color: '#666' }}>Generate custom learning paths and discover trending educational content</p>
          <button 
            onClick={testConnection}
            style={{
              padding: '0.5rem 1rem',
              background: connectionStatus === 'connected' ? '#10b981' : '#6b7280',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              marginTop: '1rem'
            }}
          >
            {connectionStatus === 'connected' ? '✅ Connected' : 
             connectionStatus === 'disconnected' ? '❌ Disconnected' : 
             connectionStatus === 'error' ? '⚠️ Error' : '🔍 Test Connection'}
          </button>
        </div>

        <div style={{ marginBottom: '2rem' }}>
          <div style={{ display: 'flex', borderBottom: '2px solid #e5e7eb' }}>
            <button
              onClick={() => setSelectedTab('learning-path')}
              style={{
                padding: '1rem 2rem',
                border: 'none',
                background: selectedTab === 'learning-path' ? '#4f8cff' : 'transparent',
                color: selectedTab === 'learning-path' ? 'white' : '#666',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                borderRadius: '8px 8px 0 0'
              }}
            >
              <FaBookOpen />
              Learning Path Generator
            </button>
            <button
              onClick={() => setSelectedTab('trending-tweets')}
              style={{
                padding: '1rem 2rem',
                border: 'none',
                background: selectedTab === 'trending-tweets' ? '#4f8cff' : 'transparent',
                color: selectedTab === 'trending-tweets' ? 'white' : '#666',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                borderRadius: '8px 8px 0 0'
              }}
            >
              <FaChartLine />
              Trending Tweets
            </button>
          </div>

          {/* Learning Path Generator */}
          {selectedTab === 'learning-path' && (
            <div style={{ marginTop: '2rem' }}>
              <div style={{ background: 'white', borderRadius: '12px', padding: '2rem', boxShadow: '0 2px 10px rgba(0,0,0,0.1)', marginBottom: '2rem' }}>
                <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem', fontSize: '1.25rem', fontWeight: '600' }}>
                  <FaBookOpen />
                  Generate Custom Learning Path
                </h2>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', marginBottom: '0.5rem' }}>Topic</label>
                    <input
                      style={{
                        width: '100%',
                        padding: '0.75rem',
                        border: '1px solid #d1d5db',
                        borderRadius: '6px',
                        fontSize: '0.875rem'
                      }}
                      placeholder="e.g., Machine Learning, React.js, Data Science"
                      value={pathForm.topic}
                      onChange={(e) => setPathForm({...pathForm, topic: e.target.value})}
                    />
                  </div>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', marginBottom: '0.5rem' }}>Skill Level</label>
                    <select
                      style={{
                        width: '100%',
                        padding: '0.75rem',
                        border: '1px solid #d1d5db',
                        borderRadius: '6px',
                        fontSize: '0.875rem'
                      }}
                      value={pathForm.skill_level}
                      onChange={(e) => setPathForm({...pathForm, skill_level: e.target.value})}
                    >
                      <option value="beginner">Beginner</option>
                      <option value="intermediate">Intermediate</option>
                      <option value="advanced">Advanced</option>
                    </select>
                  </div>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', marginBottom: '0.5rem' }}>Duration (weeks)</label>
                    <input
                      style={{
                        width: '100%',
                        padding: '0.75rem',
                        border: '1px solid #d1d5db',
                        borderRadius: '6px',
                        fontSize: '0.875rem'
                      }}
                      type="number"
                      min="4"
                      max="52"
                      value={pathForm.duration_weeks}
                      onChange={(e) => setPathForm({...pathForm, duration_weeks: parseInt(e.target.value)})}
                    />
                  </div>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', marginBottom: '0.5rem' }}>Hours per week</label>
                    <input
                      style={{
                        width: '100%',
                        padding: '0.75rem',
                        border: '1px solid #d1d5db',
                        borderRadius: '6px',
                        fontSize: '0.875rem'
                      }}
                      type="number"
                      min="1"
                      max="40"
                      value={pathForm.hours_per_week}
                      onChange={(e) => setPathForm({...pathForm, hours_per_week: parseInt(e.target.value)})}
                    />
                  </div>
                </div>
                <button
                  onClick={generateLearningPath}
                  disabled={loading}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    background: loading ? '#9ca3af' : '#4f8cff',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    fontSize: '1rem',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '0.5rem'
                  }}
                >
                  <FaBookOpen />
                  {loading ? 'Generating...' : 'Generate Learning Path'}
                </button>
              </div>

              {/* Learning Path Results */}
              {learningPath && (
                <div style={{ background: 'white', borderRadius: '12px', padding: '2rem', boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                    <div>
                      <h3 style={{ fontSize: '1.5rem', fontWeight: '600', marginBottom: '0.5rem' }}>{learningPath.title}</h3>
                      <p style={{ color: '#666', margin: 0 }}>{learningPath.description}</p>
                    </div>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <button
                        onClick={() => setExpandedPath(!expandedPath)}
                        style={{
                          padding: '0.5rem 1rem',
                          background: '#6b7280',
                          color: 'white',
                          border: 'none',
                          borderRadius: '6px',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.5rem'
                        }}
                      >
                        <FaEye />
                        {expandedPath ? 'Collapse' : 'View Full Path'}
                      </button>
                      <button
                        onClick={saveLearningPath}
                        style={{
                          padding: '0.5rem 1rem',
                          background: '#10b981',
                          color: 'white',
                          border: 'none',
                          borderRadius: '6px',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.5rem'
                        }}
                      >
                        <FaSave />
                        Save Path
                      </button>
                    </div>
                  </div>
                  
                  <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem' }}>
                    <span style={{ background: '#e5e7eb', padding: '0.25rem 0.75rem', borderRadius: '12px', fontSize: '0.75rem' }}>{learningPath.skill_level}</span>
                    <span style={{ background: '#e5e7eb', padding: '0.25rem 0.75rem', borderRadius: '12px', fontSize: '0.75rem' }}>{learningPath.total_weeks} weeks</span>
                    <span style={{ background: '#e5e7eb', padding: '0.25rem 0.75rem', borderRadius: '12px', fontSize: '0.75rem' }}>{learningPath.hours_per_week}h/week</span>
                  </div>
                  
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    {learningPath.weeks?.slice(0, expandedPath ? learningPath.weeks.length : 2).map((week) => (
                      <div key={week.week_number} style={{ border: '1px solid #e5e7eb', borderLeft: '4px solid #4f8cff', borderRadius: '8px', padding: '1rem' }}>
                        <h4 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '0.5rem' }}>Week {week.week_number}: {week.title}</h4>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem', marginBottom: '1rem' }}>
                          {week.objectives?.map((obj, idx) => (
                            <span key={idx} style={{ background: '#f3f4f6', padding: '0.125rem 0.5rem', borderRadius: '8px', fontSize: '0.75rem' }}>{obj}</span>
                          ))}
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                          {week.days?.slice(0, expandedPath ? week.days?.length : 3).map((day) => (
                            <div key={day.day} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.5rem', background: '#f9fafb', borderRadius: '6px' }}>
                              <div>
                                <span style={{ fontWeight: '500' }}>Day {day.day}: {day.topic}</span>
                                <p style={{ fontSize: '0.875rem', color: '#666', margin: 0 }}>{day.concept}</p>
                                {expandedPath && (
                                  <div style={{ marginTop: '0.5rem' }}>
                                    <p style={{ fontSize: '0.75rem', color: '#9ca3af', margin: 0 }}>Activities: {day.activities?.join(', ')}</p>
                                    <p style={{ fontSize: '0.75rem', color: '#9ca3af', margin: 0 }}>Resources: {day.resources?.join(', ')}</p>
                                  </div>
                                )}
                              </div>
                              <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', fontSize: '0.875rem', color: '#9ca3af' }}>
                                <FaClock style={{ width: '12px', height: '12px' }} />
                                {day.estimated_hours}h
                              </div>
                            </div>
                          ))}
                          {!expandedPath && week.days?.length > 3 && (
                            <p style={{ fontSize: '0.875rem', color: '#9ca3af', textAlign: 'center', margin: 0 }}>
                              +{week.days.length - 3} more days
                            </p>
                          )}
                        </div>
                      </div>
                    ))}
                    {!expandedPath && learningPath.weeks?.length > 2 && (
                      <p style={{ fontSize: '0.875rem', color: '#9ca3af', textAlign: 'center', margin: 0 }}>
                        +{learningPath.weeks.length - 2} more weeks
                      </p>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Trending Tweets */}
          {selectedTab === 'trending-tweets' && (
            <div style={{ marginTop: '2rem' }}>
              <div style={{ background: 'white', borderRadius: '12px', padding: '2rem', boxShadow: '0 2px 10px rgba(0,0,0,0.1)', marginBottom: '2rem' }}>
                <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem', fontSize: '1.25rem', fontWeight: '600' }}>
                  <FaChartLine />
                  Discover Trending Educational Content
                </h2>
                
                <div style={{ marginBottom: '1rem' }}>
                  <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', marginBottom: '0.5rem' }}>Search Query</label>
                  <input
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '1px solid #d1d5db',
                      borderRadius: '6px',
                      fontSize: '0.875rem'
                    }}
                    placeholder="Enter search terms..."
                    value={tweetForm.query}
                    onChange={(e) => setTweetForm({...tweetForm, query: e.target.value})}
                  />
                </div>
                
                <div style={{ marginBottom: '1rem' }}>
                  <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', marginBottom: '0.5rem' }}>Quick Topics</label>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
                    {trendingTopics.map((category) => (
                      <div key={category.category} style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                        <h4 style={{ fontWeight: '500', fontSize: '0.875rem' }}>{category.category}</h4>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                          {category.queries.map((query, idx) => (
                            <button
                              key={idx}
                              style={{
                                width: '100%',
                                textAlign: 'left',
                                padding: '0.5rem',
                                border: '1px solid #d1d5db',
                                borderRadius: '4px',
                                background: 'white',
                                cursor: 'pointer',
                                fontSize: '0.75rem'
                              }}
                              onClick={() => setTweetForm({...tweetForm, query})}
                            >
                              {query.split(' ').slice(0, 4).join(' ')}...
                            </button>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <input
                    style={{
                      width: '120px',
                      padding: '0.75rem',
                      border: '1px solid #d1d5db',
                      borderRadius: '6px',
                      fontSize: '0.875rem'
                    }}
                    type="number"
                    placeholder="Max results"
                    min="5"
                    max="50"
                    value={tweetForm.max_results}
                    onChange={(e) => setTweetForm({...tweetForm, max_results: parseInt(e.target.value)})}
                  />
                  <button
                    onClick={fetchTrendingTweets}
                    disabled={loading}
                    style={{
                      flex: 1,
                      padding: '0.75rem',
                      background: loading ? '#9ca3af' : '#4f8cff',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      fontSize: '1rem',
                      cursor: loading ? 'not-allowed' : 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '0.5rem'
                    }}
                  >
                    <FaChartLine />
                    {loading ? 'Searching...' : 'Search Tweets'}
                  </button>
                </div>
              </div>

              {/* Tweets Results */}
              {tweets && (
                <div style={{ background: 'white', borderRadius: '12px', padding: '2rem', boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                    <h3 style={{ fontSize: '1.25rem', fontWeight: '600', margin: 0 }}>Educational Tweets</h3>
                    {tweets.fallback && (
                      <span style={{ background: '#fef3c7', color: '#92400e', padding: '0.25rem 0.75rem', borderRadius: '12px', fontSize: '0.75rem' }}>
                        📡 Sample Data
                      </span>
                    )}
                  </div>
                  
                  <p style={{ fontSize: '0.875rem', color: '#666', marginBottom: '1.5rem' }}>
                    {(() => {
                      const tweetArray = tweets.data?.data?.data || tweets.data?.data || tweets.data || [];
                      return `Showing ${Array.isArray(tweetArray) ? tweetArray.length : 0} educational tweets`;
                    })()} {tweets.fallback ? 'from our curated collection' : 'from Twitter'}
                  </p>
                  
                  <div style={{ display: 'grid', gap: '1.5rem' }}>
                    {(() => {
                      const tweetArray = tweets.data?.data?.data || tweets.data?.data || tweets.data || [];
                      return Array.isArray(tweetArray) ? tweetArray : [];
                    })().map((tweet, index) => (
                      <div key={tweet.id} style={{ 
                        border: '1px solid #e5e7eb', 
                        borderRadius: '12px', 
                        padding: '1.5rem', 
                        background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
                        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                        transition: 'transform 0.2s ease, box-shadow 0.2s ease'
                      }}>
                        {/* Tweet Header */}
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
                          <div style={{ 
                            width: '40px', 
                            height: '40px', 
                            borderRadius: '50%', 
                            background: `linear-gradient(135deg, ${['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6'][index % 5]} 0%, ${['#1d4ed8', '#dc2626', '#059669', '#d97706', '#7c3aed'][index % 5]} 100%)`,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: 'white',
                            fontWeight: 'bold',
                            fontSize: '0.875rem'
                          }}>
                            {['🤖', '📚', '💡', '🚀', '🔥'][index % 5]}
                          </div>
                          <div>
                            <div style={{ fontWeight: '600', fontSize: '0.875rem', color: '#374151' }}>EduTech Insights</div>
                            <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>{formatDate(tweet.created_at)}</div>
                          </div>
                        </div>
                        
                        {/* Tweet Content */}
                        <div style={{ marginBottom: '1rem' }}>
                          <p style={{ 
                            fontSize: '0.95rem', 
                            lineHeight: '1.6', 
                            margin: 0, 
                            color: '#1f2937',
                            fontWeight: '400'
                          }}>
                            {tweet.text}
                          </p>
                        </div>
                        
                        {/* Tweet Metrics */}
                        <div style={{ 
                          display: 'flex', 
                          justifyContent: 'space-between', 
                          alignItems: 'center',
                          padding: '0.75rem 0',
                          borderTop: '1px solid #e5e7eb',
                          marginTop: '1rem'
                        }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#ef4444' }}>
                              <FaHeart style={{ width: '14px', height: '14px' }} />
                              <span style={{ fontSize: '0.875rem', fontWeight: '500' }}>{tweet.public_metrics?.like_count || 0}</span>
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#3b82f6' }}>
                              <FaComment style={{ width: '14px', height: '14px' }} />
                              <span style={{ fontSize: '0.875rem', fontWeight: '500' }}>{tweet.public_metrics?.reply_count || 0}</span>
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#10b981' }}>
                              <FaRetweet style={{ width: '14px', height: '14px' }} />
                              <span style={{ fontSize: '0.875rem', fontWeight: '500' }}>{tweet.public_metrics?.retweet_count || 0}</span>
                            </div>
                          </div>
                          
                          <button
                            style={{
                              padding: '0.5rem 1rem',
                              border: tweets.fallback ? '1px solid #d1d5db' : '1px solid #3b82f6',
                              borderRadius: '8px',
                              background: tweets.fallback ? '#f9fafb' : '#3b82f6',
                              color: tweets.fallback ? '#6b7280' : 'white',
                              cursor: tweets.fallback ? 'not-allowed' : 'pointer',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '0.5rem',
                              fontSize: '0.875rem',
                              fontWeight: '500',
                              transition: 'all 0.2s ease'
                            }}
                            onClick={() => {
                              if (tweets.fallback) {
                                alert('🔗 This is sample educational content. Connect your Twitter account to view real tweets!');
                              } else {
                                window.open(`https://twitter.com/i/web/status/${tweet.id}`, '_blank');
                              }
                            }}
                            onMouseOver={(e) => {
                              if (!tweets.fallback) {
                                e.target.style.background = '#2563eb';
                                e.target.style.transform = 'translateY(-1px)';
                              }
                            }}
                            onMouseOut={(e) => {
                              if (!tweets.fallback) {
                                e.target.style.background = '#3b82f6';
                                e.target.style.transform = 'translateY(0)';
                              }
                            }}
                          >
                            <FaExternalLinkAlt style={{ width: '12px', height: '12px' }} />
                            {tweets.fallback ? 'Sample Content' : 'View on Twitter'}
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                  
                  {tweets.fallback && (
                    <div style={{ 
                      marginTop: '2rem', 
                      padding: '1rem', 
                      background: '#f0f9ff', 
                      borderRadius: '8px', 
                      border: '1px solid #bfdbfe',
                      textAlign: 'center'
                    }}>
                      <p style={{ margin: 0, fontSize: '0.875rem', color: '#1e40af' }}>
                        💡 <strong>Connect Twitter:</strong> Link your Twitter account to see real-time educational tweets and trending content!
                      </p>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default Subplans;