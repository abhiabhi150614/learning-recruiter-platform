import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FiLinkedin, FiGithub, FiCheck, FiX, FiExternalLink, FiUser, FiMapPin, FiBriefcase } from 'react-icons/fi';
import { FaTwitter } from 'react-icons/fa';
import { authenticatedFetch } from '../api';

const SocialConnections = () => {
  const [connections, setConnections] = useState({
    linkedin: { connected: false, profile: null },
    github: { connected: false, profile: null },
    twitter: { connected: false, profile: null }
  });
  const [loading, setLoading] = useState({ linkedin: false, github: false, twitter: false });
  const [error, setError] = useState('');

  useEffect(() => {
    loadConnections();
  }, []);

  const loadConnections = async () => {
    try {
      const response = await authenticatedFetch('/profile/social-connections');
      setConnections(response);
    } catch (err) {
      setError('Failed to load social connections');
    }
  };

  const connectLinkedIn = async () => {
    setLoading(prev => ({ ...prev, linkedin: true }));
    try {
      const response = await authenticatedFetch('/auth/linkedin/connect', {
        method: 'POST'
      });
      
      console.log('LinkedIn connect response:', response);
      
      if (response.error) {
        setError(`LinkedIn connection failed: ${response.error}`);
        setLoading(prev => ({ ...prev, linkedin: false }));
        return;
      }
      
      // If already connected, update state directly
      if (response.status === 'connected' && response.profile) {
        await loadConnections();
        setLoading(prev => ({ ...prev, linkedin: false }));
        return;
      }
      
      if (response.authUrl) {
        // Open LinkedIn auth in new window
        const authWindow = window.open(response.authUrl, 'linkedin-auth', 'width=600,height=600,scrollbars=yes,resizable=yes');
        
        // Poll for connection status
        const pollInterval = setInterval(async () => {
          try {
            // Check if window is closed
            if (authWindow.closed) {
              clearInterval(pollInterval);
              
              // Wait a bit then verify connection
              setTimeout(async () => {
                try {
                  const verifyResponse = await authenticatedFetch('/auth/linkedin/verify', {
                    method: 'POST'
                  });
                  
                  console.log('LinkedIn verify response:', verifyResponse);
                  
                  if (verifyResponse.status === 'connected') {
                    await loadConnections();
                  } else {
                    setError('LinkedIn connection was not completed');
                  }
                } catch (err) {
                  setError('Failed to verify LinkedIn connection');
                }
                setLoading(prev => ({ ...prev, linkedin: false }));
              }, 2000);
            }
          } catch (err) {
            // Continue polling
          }
        }, 1000);
        
        // Stop polling after 5 minutes
        setTimeout(() => {
          clearInterval(pollInterval);
          if (!authWindow.closed) {
            authWindow.close();
          }
          setLoading(prev => ({ ...prev, linkedin: false }));
        }, 300000);
      } else {
        setError('No authentication URL received');
        setLoading(prev => ({ ...prev, linkedin: false }));
      }
    } catch (err) {
      setError(`Failed to connect LinkedIn: ${err.message}`);
      setLoading(prev => ({ ...prev, linkedin: false }));
    }
  };

  const connectGitHub = async () => {
    setLoading(prev => ({ ...prev, github: true }));
    try {
      const response = await authenticatedFetch('/auth/github/connect', {
        method: 'POST'
      });
      
      console.log('GitHub connect response:', response);
      
      if (response.error) {
        setError(`GitHub connection failed: ${response.error}`);
        setLoading(prev => ({ ...prev, github: false }));
        return;
      }
      
      // If already connected, update state directly
      if (response.status === 'connected' && response.profile) {
        await loadConnections();
        setLoading(prev => ({ ...prev, github: false }));
        return;
      }
      
      if (response.authUrl) {
        // Open GitHub auth in new window
        const authWindow = window.open(response.authUrl, 'github-auth', 'width=600,height=600,scrollbars=yes,resizable=yes');
        
        // Poll for connection status
        const pollInterval = setInterval(async () => {
          try {
            // Check if window is closed
            if (authWindow.closed) {
              clearInterval(pollInterval);
              
              // Wait a bit then verify connection
              setTimeout(async () => {
                try {
                  const verifyResponse = await authenticatedFetch('/auth/github/verify', {
                    method: 'POST'
                  });
                  
                  console.log('GitHub verify response:', verifyResponse);
                  
                  if (verifyResponse.status === 'connected') {
                    await loadConnections();
                  } else {
                    setError('GitHub connection was not completed');
                  }
                } catch (err) {
                  setError('Failed to verify GitHub connection');
                }
                setLoading(prev => ({ ...prev, github: false }));
              }, 2000);
            }
          } catch (err) {
            // Continue polling
          }
        }, 1000);
        
        // Stop polling after 5 minutes
        setTimeout(() => {
          clearInterval(pollInterval);
          if (!authWindow.closed) {
            authWindow.close();
          }
          setLoading(prev => ({ ...prev, github: false }));
        }, 300000);
      } else {
        setError('No authentication URL received');
        setLoading(prev => ({ ...prev, github: false }));
      }
    } catch (err) {
      setError(`Failed to connect GitHub: ${err.message}`);
      setLoading(prev => ({ ...prev, github: false }));
    }
  };

  const disconnectLinkedIn = async () => {
    try {
      await authenticatedFetch('/auth/linkedin/disconnect', { method: 'DELETE' });
      await loadConnections();
    } catch (err) {
      setError('Failed to disconnect LinkedIn');
    }
  };

  const disconnectGitHub = async () => {
    try {
      await authenticatedFetch('/auth/github/disconnect', { method: 'DELETE' });
      await loadConnections();
    } catch (err) {
      setError('Failed to disconnect GitHub');
    }
  };

  const connectTwitter = async () => {
    setLoading(prev => ({ ...prev, twitter: true }));
    try {
      const response = await authenticatedFetch('/auth/twitter/connect', {
        method: 'POST'
      });
      
      if (response.error) {
        setError(`Twitter connection failed: ${response.error}`);
        setLoading(prev => ({ ...prev, twitter: false }));
        return;
      }
      
      if (response.status === 'connected' && response.profile) {
        await loadConnections();
        setLoading(prev => ({ ...prev, twitter: false }));
        return;
      }
      
      if (response.authUrl) {
        const authWindow = window.open(response.authUrl, 'twitter-auth', 'width=600,height=600,scrollbars=yes,resizable=yes');
        
        const pollInterval = setInterval(async () => {
          try {
            if (authWindow.closed) {
              clearInterval(pollInterval);
              
              setTimeout(async () => {
                try {
                  const verifyResponse = await authenticatedFetch('/auth/twitter/verify', {
                    method: 'POST'
                  });
                  
                  if (verifyResponse.status === 'connected') {
                    await loadConnections();
                  } else {
                    setError('Twitter connection was not completed');
                  }
                } catch (err) {
                  setError('Failed to verify Twitter connection');
                }
                setLoading(prev => ({ ...prev, twitter: false }));
              }, 2000);
            }
          } catch (err) {
            // Continue polling
          }
        }, 1000);
        
        setTimeout(() => {
          clearInterval(pollInterval);
          if (!authWindow.closed) {
            authWindow.close();
          }
          setLoading(prev => ({ ...prev, twitter: false }));
        }, 300000);
      } else {
        setError('No authentication URL received');
        setLoading(prev => ({ ...prev, twitter: false }));
      }
    } catch (err) {
      setError(`Failed to connect Twitter: ${err.message}`);
      setLoading(prev => ({ ...prev, twitter: false }));
    }
  };

  const disconnectTwitter = async () => {
    try {
      await authenticatedFetch('/auth/twitter/disconnect', { method: 'DELETE' });
      await loadConnections();
    } catch (err) {
      setError('Failed to disconnect Twitter');
    }
  };

  return (
    <div style={{ padding: '24px' }}>
      <h2 style={{ fontSize: '24px', fontWeight: '700', marginBottom: '8px', color: '#1a202c' }}>
        Social Connections
      </h2>
      <p style={{ color: '#718096', marginBottom: '32px' }}>
        Connect your LinkedIn, Twitter, and GitHub accounts to enhance your profile
      </p>

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

      <div style={{ display: 'grid', gap: '24px', maxWidth: '800px' }}>
        {/* LinkedIn Connection */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          style={{
            background: 'white',
            borderRadius: '16px',
            padding: '24px',
            border: '1px solid #e2e8f0',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{
                width: '48px',
                height: '48px',
                background: '#0077b5',
                borderRadius: '12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <FiLinkedin size={24} color="white" />
              </div>
              <div>
                <h3 style={{ margin: 0, fontSize: '18px', fontWeight: '600', color: '#1a202c' }}>
                  LinkedIn
                </h3>
                <p style={{ margin: 0, fontSize: '14px', color: '#718096' }}>
                  Professional networking platform
                </p>
              </div>
            </div>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              {connections.linkedin.connected ? (
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <FiCheck size={16} color="#10b981" />
                  <span style={{ color: '#10b981', fontSize: '14px', fontWeight: '600' }}>
                    Connected
                  </span>
                </div>
              ) : (
                <span style={{ color: '#718096', fontSize: '14px' }}>
                  Not connected
                </span>
              )}
              
              {connections.linkedin.connected ? (
                <button
                  onClick={disconnectLinkedIn}
                  style={{
                    padding: '8px 16px',
                    background: '#fed7d7',
                    color: '#c53030',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    fontSize: '14px',
                    fontWeight: '600'
                  }}
                >
                  Disconnect
                </button>
              ) : (
                <button
                  onClick={connectLinkedIn}
                  disabled={loading.linkedin}
                  style={{
                    padding: '8px 16px',
                    background: loading.linkedin ? '#e2e8f0' : '#0077b5',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: loading.linkedin ? 'not-allowed' : 'pointer',
                    fontSize: '14px',
                    fontWeight: '600'
                  }}
                >
                  {loading.linkedin ? 'Connecting...' : 'Connect'}
                </button>
              )}
            </div>
          </div>

          {connections.linkedin.connected && connections.linkedin.profile && (
            <div style={{
              background: '#f8fafc',
              borderRadius: '12px',
              padding: '16px',
              border: '1px solid #e2e8f0'
            }}>
              <h4 style={{ margin: '0 0 12px', fontSize: '16px', fontWeight: '600', color: '#1a202c' }}>
                Profile Information
              </h4>
              {(() => {
                const profile = connections.linkedin.profile;
                const responseDict = profile?.data?.response_dict || profile?.response_dict || profile;
                
                return (
                  <div style={{ display: 'grid', gap: '8px' }}>
                    {responseDict?.name && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <FiUser size={14} color="#718096" />
                        <span style={{ fontSize: '14px', color: '#1a202c', fontWeight: '500' }}>
                          {responseDict.name}
                        </span>
                      </div>
                    )}
                    {responseDict?.email && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ fontSize: '12px', color: '#718096' }}>📧</span>
                        <span style={{ fontSize: '14px', color: '#1a202c' }}>
                          {responseDict.email}
                        </span>
                        {responseDict?.email_verified && (
                          <span style={{ fontSize: '12px', color: '#10b981', background: '#d1fae5', padding: '2px 6px', borderRadius: '4px' }}>
                            ✓ Verified
                          </span>
                        )}
                      </div>
                    )}
                    {responseDict?.locale && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <FiMapPin size={14} color="#718096" />
                        <span style={{ fontSize: '14px', color: '#1a202c' }}>
                          {responseDict.locale.country}, {responseDict.locale.language?.toUpperCase()}
                        </span>
                      </div>
                    )}
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '8px' }}>
                      <FiExternalLink size={14} color="#718096" />
                      <a
                        href={`https://linkedin.com/in/${responseDict?.sub || ''}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{ fontSize: '14px', color: '#4f8cff', textDecoration: 'none' }}
                      >
                        View LinkedIn Profile
                      </a>
                    </div>
                  </div>
                );
              })()}
            </div>
          )}
        </motion.div>

        {/* Twitter Connection */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          style={{
            background: 'white',
            borderRadius: '16px',
            padding: '24px',
            border: '1px solid #e2e8f0',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{
                width: '48px',
                height: '48px',
                background: '#1da1f2',
                borderRadius: '12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <FaTwitter size={24} color="white" />
              </div>
              <div>
                <h3 style={{ margin: 0, fontSize: '18px', fontWeight: '600', color: '#1a202c' }}>
                  Twitter
                </h3>
                <p style={{ margin: 0, fontSize: '14px', color: '#718096' }}>
                  Social media and networking platform
                </p>
              </div>
            </div>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              {connections.twitter.connected ? (
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <FiCheck size={16} color="#10b981" />
                  <span style={{ color: '#10b981', fontSize: '14px', fontWeight: '600' }}>
                    Connected
                  </span>
                </div>
              ) : (
                <span style={{ color: '#718096', fontSize: '14px' }}>
                  Not connected
                </span>
              )}
              
              {connections.twitter.connected ? (
                <button
                  onClick={disconnectTwitter}
                  style={{
                    padding: '8px 16px',
                    background: '#fed7d7',
                    color: '#c53030',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    fontSize: '14px',
                    fontWeight: '600'
                  }}
                >
                  Disconnect
                </button>
              ) : (
                <button
                  onClick={connectTwitter}
                  disabled={loading.twitter}
                  style={{
                    padding: '8px 16px',
                    background: loading.twitter ? '#e2e8f0' : '#1da1f2',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: loading.twitter ? 'not-allowed' : 'pointer',
                    fontSize: '14px',
                    fontWeight: '600'
                  }}
                >
                  {loading.twitter ? 'Connecting...' : 'Connect'}
                </button>
              )}
            </div>
          </div>

          {connections.twitter.connected && connections.twitter.profile && (
            <div style={{
              background: '#f8fafc',
              borderRadius: '12px',
              padding: '16px',
              border: '1px solid #e2e8f0'
            }}>
              <h4 style={{ margin: '0 0 12px', fontSize: '16px', fontWeight: '600', color: '#1a202c' }}>
                Profile Information
              </h4>
              
              <div style={{
                background: '#f8fafc',
                border: '1px solid #e2e8f0',
                borderRadius: '8px',
                padding: '12px',
                fontSize: '12px',
                fontFamily: 'monospace',
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-all',
                maxHeight: '200px',
                overflow: 'auto'
              }}>
                {JSON.stringify(connections.twitter.profile, null, 2)}
              </div>
            </div>
          )}
        </motion.div>

        {/* GitHub Connection */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          style={{
            background: 'white',
            borderRadius: '16px',
            padding: '24px',
            border: '1px solid #e2e8f0',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{
                width: '48px',
                height: '48px',
                background: '#24292e',
                borderRadius: '12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <FiGithub size={24} color="white" />
              </div>
              <div>
                <h3 style={{ margin: 0, fontSize: '18px', fontWeight: '600', color: '#1a202c' }}>
                  GitHub
                </h3>
                <p style={{ margin: 0, fontSize: '14px', color: '#718096' }}>
                  Code repository and collaboration platform
                </p>
              </div>
            </div>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              {connections.github.connected ? (
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <FiCheck size={16} color="#10b981" />
                  <span style={{ color: '#10b981', fontSize: '14px', fontWeight: '600' }}>
                    Connected
                  </span>
                </div>
              ) : (
                <span style={{ color: '#718096', fontSize: '14px' }}>
                  Not connected
                </span>
              )}
              
              {connections.github.connected ? (
                <button
                  onClick={disconnectGitHub}
                  style={{
                    padding: '8px 16px',
                    background: '#fed7d7',
                    color: '#c53030',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    fontSize: '14px',
                    fontWeight: '600'
                  }}
                >
                  Disconnect
                </button>
              ) : (
                <button
                  onClick={connectGitHub}
                  disabled={loading.github}
                  style={{
                    padding: '8px 16px',
                    background: loading.github ? '#e2e8f0' : '#24292e',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: loading.github ? 'not-allowed' : 'pointer',
                    fontSize: '14px',
                    fontWeight: '600'
                  }}
                >
                  {loading.github ? 'Connecting...' : 'Connect'}
                </button>
              )}
            </div>
          </div>

          {connections.github.connected && connections.github.profile && (
            <div style={{
              background: '#f8fafc',
              borderRadius: '12px',
              padding: '16px',
              border: '1px solid #e2e8f0'
            }}>
              <h4 style={{ margin: '0 0 12px', fontSize: '16px', fontWeight: '600', color: '#1a202c' }}>
                Profile Information
              </h4>
              {(() => {
                const profile = connections.github.profile;
                const details = profile?.data?.details || profile?.details || [];
                const firstRepo = details[0];
                const owner = firstRepo?.owner;
                
                return (
                  <div style={{ display: 'grid', gap: '12px' }}>
                    {owner && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <img 
                          src={owner.avatar_url} 
                          alt={owner.login}
                          style={{ width: '40px', height: '40px', borderRadius: '50%' }}
                        />
                        <div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <FiUser size={14} color="#718096" />
                            <span style={{ fontSize: '16px', color: '#1a202c', fontWeight: '600' }}>
                              {owner.login}
                            </span>
                          </div>
                          <div style={{ fontSize: '14px', color: '#718096' }}>
                            {details.length} repositories
                          </div>
                        </div>
                      </div>
                    )}
                    
                    {details.length > 0 && (
                      <div>
                        <h5 style={{ margin: '0 0 8px', fontSize: '14px', fontWeight: '600', color: '#1a202c' }}>
                          Recent Repositories
                        </h5>
                        <div style={{ display: 'grid', gap: '8px' }}>
                          {details.slice(0, 3).map((repo, index) => (
                            <div key={index} style={{
                              background: 'white',
                              padding: '12px',
                              borderRadius: '8px',
                              border: '1px solid #e2e8f0'
                            }}>
                              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                                <span style={{ fontSize: '14px', fontWeight: '500', color: '#1a202c' }}>
                                  {repo.name}
                                </span>
                                {repo.language && (
                                  <span style={{
                                    fontSize: '12px',
                                    color: '#718096',
                                    background: '#f1f5f9',
                                    padding: '2px 6px',
                                    borderRadius: '4px'
                                  }}>
                                    {repo.language}
                                  </span>
                                )}
                              </div>
                              {repo.description && (
                                <div style={{ fontSize: '12px', color: '#718096', marginBottom: '6px' }}>
                                  {repo.description.length > 60 ? repo.description.substring(0, 60) + '...' : repo.description}
                                </div>
                              )}
                              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '12px', color: '#718096' }}>
                                <span>⭐ {repo.stargazers_count}</span>
                                <span>🍴 {repo.forks_count}</span>
                                <a href={repo.html_url} target="_blank" rel="noopener noreferrer" style={{ color: '#4f8cff', textDecoration: 'none' }}>
                                  View →
                                </a>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {owner && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '8px' }}>
                        <FiExternalLink size={14} color="#718096" />
                        <a
                          href={owner.html_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{ fontSize: '14px', color: '#4f8cff', textDecoration: 'none' }}
                        >
                          View GitHub Profile
                        </a>
                      </div>
                    )}
                  </div>
                );
              })()}
            </div>
          )}
        </motion.div>
      </div>

      <div style={{
        background: '#f0f9ff',
        border: '1px solid #bae6fd',
        borderRadius: '12px',
        padding: '16px',
        marginTop: '24px',
        maxWidth: '800px'
      }}>
        <h4 style={{ margin: '0 0 8px', fontSize: '16px', fontWeight: '600', color: '#0369a1' }}>
          Why connect your accounts?
        </h4>
        <ul style={{ margin: 0, paddingLeft: '20px', color: '#0369a1', fontSize: '14px' }}>
          <li>Enhanced profile visibility for recruiters</li>
          <li>Automatic skill extraction from your repositories and experience</li>
          <li>Better job matching based on your professional background</li>
          <li>Showcase your projects and contributions</li>
        </ul>
      </div>
    </div>
  );
};

export default SocialConnections;