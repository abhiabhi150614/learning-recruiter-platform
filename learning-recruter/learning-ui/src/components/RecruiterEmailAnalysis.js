import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { recruiterAuthenticatedFetch } from '../api';
import { motion, AnimatePresence } from 'framer-motion';
import RecruiterLayout from './RecruiterLayout';
import { 
  FiMail, 
  FiSearch, 
  FiFilter, 
  FiRefreshCw,
  FiCheckCircle,
  FiClock,
  FiUser,
  FiCalendar,
  FiEye,
  FiTrash2,
  FiStar,
  FiDownload,
  FiCornerUpLeft,
  FiShare,
  FiPlus
} from 'react-icons/fi';

const RecruiterEmailAnalysis = () => {
  const [emails, setEmails] = useState([]);
  const [filteredEmails, setFilteredEmails] = useState([]);
  const [loading, setLoading] = useState(false);
  const [emailsLoading, setEmailsLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [error, setError] = useState('');
  const [summarizing, setSummarizing] = useState(false);
  const [emailSummary, setEmailSummary] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Load emails after component mounts
    setTimeout(() => loadEmails(), 100);
  }, []);

  useEffect(() => {
    filterEmails();
  }, [emails, searchTerm, filterStatus]);

  const loadEmails = async () => {
    try {
      setEmailsLoading(true);
      setError('');
      const response = await recruiterAuthenticatedFetch('/recruiter/emails/recent');
      setEmails(response.emails || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setEmailsLoading(false);
    }
  };

  const refreshEmails = async () => {
    setRefreshing(true);
    await loadEmails();
    setRefreshing(false);
  };

  const filterEmails = () => {
    let filtered = emails;

    if (searchTerm) {
      filtered = filtered.filter(email => 
        email.sender_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        email.sender_email.toLowerCase().includes(searchTerm.toLowerCase()) ||
        email.subject.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (filterStatus !== 'all') {
      filtered = filtered.filter(email => {
        if (filterStatus === 'unread') return !email.processed;
        if (filterStatus === 'read') return email.processed;
        if (filterStatus === 'matched') return email.student_matched;
        return true;
      });
    }

    setFilteredEmails(filtered);
  };

  const markAsRead = async (emailId) => {
    try {
      await recruiterAuthenticatedFetch(`/recruiter/emails/${emailId}/mark-read`, {
        method: 'POST'
      });
      
      setEmails(emails.map(email => 
        email.id === emailId ? { ...email, processed: true } : email
      ));
    } catch (err) {
      console.error('Failed to mark email as read:', err);
    }
  };

  const handleSendMeetLink = async (email) => {
    try {
      // Get current time + 1 hour as default
      const defaultTime = new Date();
      defaultTime.setHours(defaultTime.getHours() + 1);
      
      const interviewTime = prompt(
        `Schedule interview with ${email.sender_name}\n\nEnter date and time (YYYY-MM-DD HH:MM):`,
        defaultTime.toISOString().slice(0, 16).replace('T', ' ')
      );
      
      if (!interviewTime) return;
      
      const response = await recruiterAuthenticatedFetch('/recruiter/emails/send-meet-link', {
        method: 'POST',
        body: JSON.stringify({
          candidate_email: email.sender_email,
          candidate_name: email.sender_name,
          interview_datetime: new Date(interviewTime).toISOString(),
          job_title: 'Interview',
          duration_minutes: 60
        })
      });
      
      if (response.success) {
        alert(`✅ Google Meet link sent to ${email.sender_name}!\n\nMeet Link: ${response.meet_link}`);
      } else {
        alert(`❌ Failed to send meet link: ${response.error}`);
      }
    } catch (err) {
      alert(`Failed to send meet link: ${err.message}`);
    }
  };

  const handleAddToShortlist = async (email, jobId = null) => {
    try {
      if (!jobId) {
        // Get available jobs
        const jobsResponse = await recruiterAuthenticatedFetch('/recruiter/jobs/for-shortlist');
        const jobs = jobsResponse.jobs || [];
        
        if (jobs.length === 0) {
          alert('Please create a job posting first before shortlisting candidates.');
          return;
        }
        
        // Simple job selection (you can make this a proper modal)
        const jobOptions = jobs.map((job, index) => `${index + 1}. ${job.title}`).join('\n');
        const selection = prompt(`Select job to shortlist for:\n\n${jobOptions}\n\nEnter number:`);
        
        if (!selection) return;
        
        const selectedIndex = parseInt(selection) - 1;
        if (selectedIndex < 0 || selectedIndex >= jobs.length) {
          alert('Invalid selection');
          return;
        }
        
        jobId = jobs[selectedIndex].id;
      }
      
      const response = await recruiterAuthenticatedFetch(`/recruiter/emails/${email.id}/add-to-shortlist`, {
        method: 'POST',
        body: JSON.stringify({
          sender_email: email.sender_email,
          sender_name: email.sender_name,
          content: email.full_content || email.content,
          job_id: jobId,
          summary: emailSummary?.summary || '',
          skills: emailSummary?.skills || []
        })
      });
      
      // Update email status
      setEmails(emails.map(e => 
        e.id === email.id ? { ...e, in_watchlist: true, student_matched: true } : e
      ));
      
      alert(`✅ ${email.sender_name} added to shortlist successfully!`);
    } catch (err) {
      alert(`Failed to add to shortlist: ${err.message}`);
    }
  };

  const handleSummarizeEmail = async (email) => {
    try {
      setSummarizing(true);
      const response = await recruiterAuthenticatedFetch(`/recruiter/emails/${email.id}/summarize`, {
        method: 'POST',
        body: JSON.stringify({
          content: email.content,
          full_content: email.full_content || email.content,
          sender_name: email.sender_name,
          sender_email: email.sender_email,
          subject: email.subject,
          attachments: email.attachments || []
        })
      });
      
      setEmailSummary({
        email: email,
        summary: response.summary,
        skills: response.skills_extracted || []
      });
    } catch (err) {
      alert(`Failed to summarize: ${err.message}`);
    } finally {
      setSummarizing(false);
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return '#e53e3e';
      case 'medium': return '#d69e2e';
      case 'low': return '#38a169';
      default: return '#718096';
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return 'Today';
    if (diffDays === 2) return 'Yesterday';
    if (diffDays <= 7) return `${diffDays - 1} days ago`;
    return date.toLocaleDateString();
  };



  return (
    <RecruiterLayout>
      {/* Header */}
      <div style={{
        background: 'white',
        borderRadius: '16px',
        padding: '32px',
        margin: '32px',
        marginBottom: '24px',
        boxShadow: '0 4px 6px rgba(0,0,0,0.05)',
        border: '1px solid #e2e8f0'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <div>
            <h1 style={{
              fontSize: '32px',
              fontWeight: '700',
              color: '#1a202c',
              margin: '0 0 8px'
            }}>
              Messages & Applications
            </h1>
            <p style={{
              color: '#718096',
              margin: 0,
              fontSize: '16px'
            }}>
              Manage candidate applications and communications
            </p>
          </div>

          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={refreshEmails}
            disabled={refreshing}
            style={{
              padding: '12px 20px',
              background: refreshing ? '#f7fafc' : 'linear-gradient(135deg, #4f8cff, #6366f1)',
              border: 'none',
              borderRadius: '12px',
              cursor: refreshing ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              fontWeight: '600',
              color: refreshing ? '#718096' : 'white',
              boxShadow: refreshing ? 'none' : '0 8px 25px rgba(79, 140, 255, 0.3)'
            }}
          >
            <FiRefreshCw 
              size={16} 
              style={{
                animation: refreshing ? 'spin 1s linear infinite' : 'none'
              }}
            />
            {refreshing ? 'Refreshing...' : 'Refresh'}
          </motion.button>
        </div>
      </div>

      <div style={{ padding: '24px' }}>
        {/* Search and Filters */}
        <div style={{
          background: 'white',
          borderRadius: '12px',
          padding: '20px',
          marginBottom: '20px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          border: '1px solid #e2e8f0'
        }}>
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr auto auto',
            gap: '16px',
            alignItems: 'center'
          }}>
            <div style={{ position: 'relative' }}>
              <FiSearch style={{
                position: 'absolute',
                left: '12px',
                top: '50%',
                transform: 'translateY(-50%)',
                color: '#a0aec0',
                fontSize: '18px'
              }} />
              <input
                type="text"
                placeholder="Search emails by name, email, or subject..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                style={{
                  width: '100%',
                  padding: '12px 16px 12px 44px',
                  border: '2px solid #e2e8f0',
                  borderRadius: '8px',
                  fontSize: '14px',
                  boxSizing: 'border-box',
                  outline: 'none'
                }}
                onFocus={(e) => e.target.style.borderColor = '#4f8cff'}
                onBlur={(e) => e.target.style.borderColor = '#e2e8f0'}
              />
            </div>

            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              style={{
                padding: '12px 16px',
                border: '2px solid #e2e8f0',
                borderRadius: '8px',
                fontSize: '14px',
                background: 'white',
                cursor: 'pointer',
                outline: 'none'
              }}
            >
              <option value="all">All Emails</option>
              <option value="unread">Unread</option>
              <option value="read">Read</option>
              <option value="matched">Matched Candidates</option>
            </select>

            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              color: '#718096',
              fontSize: '14px'
            }}>
              <FiMail size={16} />
              {filteredEmails.length} emails
            </div>
          </div>
        </div>

        {error && (
          <div style={{
            background: '#fed7d7',
            color: '#c53030',
            padding: '12px 16px',
            borderRadius: '8px',
            marginBottom: '20px',
            border: '1px solid #feb2b2'
          }}>
            {error}
          </div>
        )}

        {/* Email List */}
        <div style={{
          background: 'white',
          borderRadius: '12px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          border: '1px solid #e2e8f0',
          overflow: 'hidden'
        }}>
          {emailsLoading ? (
            <div style={{
              padding: '60px 20px',
              textAlign: 'center',
              color: '#718096'
            }}>
              <div style={{
                width: '40px',
                height: '40px',
                border: '4px solid #e2e8f0',
                borderTop: '4px solid #4f8cff',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite',
                margin: '0 auto 16px'
              }} />
              <p style={{ margin: 0, fontSize: '14px' }}>Loading emails...</p>
            </div>
          ) : filteredEmails.length === 0 ? (
            <div style={{
              padding: '60px 20px',
              textAlign: 'center',
              color: '#718096'
            }}>
              <FiMail size={48} style={{ marginBottom: '16px' }} />
              <h3 style={{ margin: '0 0 8px', fontSize: '18px', fontWeight: '600' }}>
                {searchTerm || filterStatus !== 'all' ? 'No matching emails' : 'No emails yet'}
              </h3>
              <p style={{ margin: 0, fontSize: '14px' }}>
                {searchTerm || filterStatus !== 'all' 
                  ? 'Try adjusting your search or filter criteria'
                  : 'Email applications will appear here when candidates reach out'
                }
              </p>
            </div>
          ) : (
            <div>
              {filteredEmails.map((email, index) => (
                <motion.div
                  key={email.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  draggable
                  onDragStart={(e) => {
                    e.dataTransfer.setData('text/plain', JSON.stringify({
                      id: email.id,
                      sender_name: email.sender_name,
                      sender_email: email.sender_email,
                      subject: email.subject,
                      content: email.content,
                      attachments: email.attachments
                    }));
                  }}
                  style={{
                    padding: '20px',
                    borderBottom: index < filteredEmails.length - 1 ? '1px solid #e2e8f0' : 'none',
                    cursor: 'grab',
                    background: email.processed ? 'white' : '#fef5e7',
                    transition: 'all 0.3s ease'
                  }}
                  whileHover={{ backgroundColor: '#f8fafc' }}
                  onClick={() => {
                    setSelectedEmail(email);
                    if (!email.processed) {
                      markAsRead(email.id);
                    }
                  }}
                >
                  <div style={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '16px'
                  }}>
                    <div style={{
                      width: '48px',
                      height: '48px',
                      borderRadius: '50%',
                      background: 'linear-gradient(135deg, #4f8cff, #6366f1)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: 'white',
                      fontWeight: '600',
                      fontSize: '18px'
                    }}>
                      {email.sender_name.charAt(0).toUpperCase()}
                    </div>

                    <div style={{ flex: 1 }}>
                      <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '12px',
                        marginBottom: '8px'
                      }}>
                        <h3 style={{
                          margin: 0,
                          fontSize: '16px',
                          fontWeight: '600',
                          color: '#1a202c'
                        }}>
                          {email.sender_name}
                        </h3>
                        
                        {!email.processed && (
                          <span style={{
                            width: '8px',
                            height: '8px',
                            background: '#e53e3e',
                            borderRadius: '50%'
                          }} />
                        )}
                        
                        {email.priority && (
                          <span style={{
                            padding: '2px 8px',
                            background: `${getPriorityColor(email.priority)}20`,
                            color: getPriorityColor(email.priority),
                            borderRadius: '12px',
                            fontSize: '11px',
                            fontWeight: '600',
                            textTransform: 'uppercase'
                          }}>
                            {email.priority}
                          </span>
                        )}
                        
                        {email.in_watchlist && (
                          <span style={{
                            padding: '2px 8px',
                            background: '#d1fae5',
                            color: '#065f46',
                            borderRadius: '12px',
                            fontSize: '11px',
                            fontWeight: '600'
                          }}>
                            In Watchlist
                          </span>
                        )}
                      </div>

                      <p style={{
                        margin: '0 0 8px',
                        fontSize: '14px',
                        fontWeight: '600',
                        color: '#2d3748',
                        lineHeight: '1.4'
                      }}>
                        {email.subject}
                      </p>

                      <p style={{
                        margin: '0 0 12px',
                        fontSize: '14px',
                        color: '#718096',
                        lineHeight: '1.5'
                      }}>
                        {email.content}
                      </p>

                      <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '16px',
                        fontSize: '12px',
                        color: '#a0aec0'
                      }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                          <FiUser size={12} />
                          {email.sender_email}
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                          <FiCalendar size={12} />
                          {formatDate(email.received_at)}
                        </div>
                      </div>
                    </div>

                    <div style={{
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '8px',
                      alignItems: 'flex-end'
                    }}>
                      <div style={{
                        display: 'flex',
                        gap: '8px'
                      }}>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedEmail(email);
                          }}
                          style={{
                            padding: '6px',
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
                          onClick={(e) => {
                            e.stopPropagation();
                            handleSummarizeEmail(email);
                          }}
                          title="Summarize with AI"
                          style={{
                            padding: '8px 12px',
                            background: '#f59e0b',
                            color: 'white',
                            border: 'none',
                            borderRadius: '6px',
                            cursor: 'pointer',
                            fontSize: '12px',
                            fontWeight: '600'
                          }}
                        >
                          Summarize
                        </button>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Email Detail Modal */}
      <AnimatePresence>
        {selectedEmail && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: 'rgba(0,0,0,0.5)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 1000,
              padding: '20px'
            }}
            onClick={() => setSelectedEmail(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              style={{
                background: 'white',
                borderRadius: '16px',
                width: '100%',
                maxWidth: '600px',
                maxHeight: '80vh',
                overflow: 'hidden',
                boxShadow: '0 20px 40px rgba(0,0,0,0.15)'
              }}
              onClick={(e) => e.stopPropagation()}
            >
              <div style={{
                padding: '24px',
                borderBottom: '1px solid #e2e8f0',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}>
                <h2 style={{
                  margin: 0,
                  fontSize: '20px',
                  fontWeight: '600',
                  color: '#1a202c'
                }}>
                  Email Details
                </h2>
                <button
                  onClick={() => setSelectedEmail(null)}
                  style={{
                    padding: '8px',
                    background: '#f7fafc',
                    border: '1px solid #e2e8f0',
                    borderRadius: '8px',
                    cursor: 'pointer'
                  }}
                >
                  ✕
                </button>
              </div>

              <div style={{
                padding: '24px',
                maxHeight: 'calc(80vh - 120px)',
                overflowY: 'auto'
              }}>
                <div style={{ marginBottom: '20px' }}>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    marginBottom: '16px'
                  }}>
                    <div style={{
                      width: '48px',
                      height: '48px',
                      borderRadius: '50%',
                      background: 'linear-gradient(135deg, #4f8cff, #6366f1)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: 'white',
                      fontWeight: '600',
                      fontSize: '18px'
                    }}>
                      {selectedEmail.sender_name.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <h3 style={{
                        margin: 0,
                        fontSize: '18px',
                        fontWeight: '600',
                        color: '#1a202c'
                      }}>
                        {selectedEmail.sender_name}
                      </h3>
                      <p style={{
                        margin: '2px 0 0',
                        fontSize: '14px',
                        color: '#718096'
                      }}>
                        {selectedEmail.sender_email}
                      </p>
                    </div>
                  </div>

                  <div style={{
                    background: '#f8fafc',
                    padding: '16px',
                    borderRadius: '8px',
                    marginBottom: '20px'
                  }}>
                    <h4 style={{
                      margin: '0 0 8px',
                      fontSize: '16px',
                      fontWeight: '600',
                      color: '#1a202c'
                    }}>
                      {selectedEmail.subject}
                    </h4>
                    <p style={{
                      margin: 0,
                      fontSize: '12px',
                      color: '#718096'
                    }}>
                      Received {formatDate(selectedEmail.received_at)}
                    </p>
                  </div>

                  <div style={{
                    fontSize: '14px',
                    lineHeight: '1.6',
                    color: '#2d3748',
                    whiteSpace: 'pre-wrap'
                  }}>
                    {selectedEmail.content}
                  </div>
                </div>

                <div style={{
                  display: 'flex',
                  gap: '12px',
                  paddingTop: '20px',
                  borderTop: '1px solid #e2e8f0'
                }}>
                  <button
                    style={{
                      flex: 1,
                      padding: '12px',
                      background: '#4f8cff',
                      color: 'white',
                      border: 'none',
                      borderRadius: '8px',
                      fontWeight: '600',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '8px'
                    }}
                  >
                    <FiCornerUpLeft size={16} />
                    Reply
                  </button>
                  <button
                    style={{
                      flex: 1,
                      padding: '12px',
                      background: '#10b981',
                      color: 'white',
                      border: 'none',
                      borderRadius: '8px',
                      fontWeight: '600',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '8px'
                    }}
                  >
                    <FiShare size={16} />
                    Forward
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Email Summary Modal */}
      <AnimatePresence>
        {emailSummary && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: 'rgba(0,0,0,0.5)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 1001,
              padding: '20px'
            }}
            onClick={() => setEmailSummary(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              style={{
                background: 'white',
                borderRadius: '16px',
                width: '100%',
                maxWidth: '700px',
                maxHeight: '80vh',
                overflow: 'hidden',
                boxShadow: '0 20px 40px rgba(0,0,0,0.15)'
              }}
              onClick={(e) => e.stopPropagation()}
            >
              <div style={{
                padding: '24px',
                borderBottom: '1px solid #e2e8f0',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}>
                <h2 style={{
                  margin: 0,
                  fontSize: '20px',
                  fontWeight: '600',
                  color: '#1a202c'
                }}>
                  Email Summary - {emailSummary.email.sender_name}
                </h2>
                <button
                  onClick={() => setEmailSummary(null)}
                  style={{
                    padding: '8px',
                    background: '#f7fafc',
                    border: '1px solid #e2e8f0',
                    borderRadius: '8px',
                    cursor: 'pointer'
                  }}
                >
                  ✕
                </button>
              </div>

              <div style={{
                padding: '24px',
                maxHeight: 'calc(80vh - 120px)',
                overflowY: 'auto'
              }}>
                <div style={{
                  background: '#f8fafc',
                  padding: '16px',
                  borderRadius: '8px',
                  marginBottom: '20px'
                }}>
                  <h4 style={{
                    margin: '0 0 8px',
                    fontSize: '16px',
                    fontWeight: '600',
                    color: '#1a202c'
                  }}>
                    {emailSummary.email.subject}
                  </h4>
                  <p style={{
                    margin: 0,
                    fontSize: '12px',
                    color: '#718096'
                  }}>
                    From: {emailSummary.email.sender_email}
                  </p>
                </div>

                <div style={{
                  fontSize: '14px',
                  lineHeight: '1.6',
                  color: '#2d3748',
                  whiteSpace: 'pre-wrap'
                }}>
                  {emailSummary.summary}
                </div>

                <div style={{
                  display: 'flex',
                  gap: '12px',
                  paddingTop: '20px',
                  borderTop: '1px solid #e2e8f0',
                  marginTop: '20px'
                }}>
                  <button
                    onClick={async () => {
                      await handleSendMeetLink(emailSummary.email);
                    }}
                    style={{
                      flex: 1,
                      padding: '12px',
                      background: '#10b981',
                      color: 'white',
                      border: 'none',
                      borderRadius: '8px',
                      fontWeight: '600',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '8px'
                    }}
                  >
                    <FiCalendar size={16} />
                    Send Meet Link
                  </button>
                  <button
                    onClick={async () => {
                      await handleAddToShortlist(emailSummary.email);
                      setEmailSummary(null);
                    }}
                    style={{
                      flex: 1,
                      padding: '12px',
                      background: '#f59e0b',
                      color: 'white',
                      border: 'none',
                      borderRadius: '8px',
                      fontWeight: '600',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '8px'
                    }}
                  >
                    <FiPlus size={16} />
                    Add to Shortlist
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Loading overlay for summarizing */}
      {summarizing && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0,0,0,0.3)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1002
        }}>
          <div style={{
            background: 'white',
            padding: '24px',
            borderRadius: '12px',
            display: 'flex',
            alignItems: 'center',
            gap: '16px',
            boxShadow: '0 10px 25px rgba(0,0,0,0.15)'
          }}>
            <div style={{
              width: '24px',
              height: '24px',
              border: '3px solid #e2e8f0',
              borderTop: '3px solid #4f8cff',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite'
            }} />
            <span style={{ fontSize: '14px', fontWeight: '600' }}>Generating summary...</span>
          </div>
        </div>
      )}

      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </RecruiterLayout>
  );
};

export default RecruiterEmailAnalysis;