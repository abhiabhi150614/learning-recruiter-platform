import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import RecruiterChatbot from './RecruiterChatbot';
import { 
  FiHome, 
  FiBriefcase, 
  FiUsers, 
  FiMail, 
  FiUser, 
  FiLogOut,
  FiPlus,
  FiBell,
  FiMenu,
  FiX,
  FiCalendar
} from 'react-icons/fi';

const RecruiterLayout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    localStorage.removeItem('recruiter_token');
    localStorage.removeItem('recruiter_user');
    navigate('/recruiter/login');
  };

  const menuItems = [
    { icon: FiHome, label: 'Dashboard', path: '/recruiter', active: location.pathname === '/recruiter' },
    { icon: FiBriefcase, label: 'My Jobs', path: '/recruiter/jobs', active: location.pathname.startsWith('/recruiter/jobs') },
    { icon: FiUsers, label: 'Candidates', path: '/recruiter/candidates', active: location.pathname.startsWith('/recruiter/candidate') },
    { icon: FiCalendar, label: 'Interviews', path: '/recruiter/interviews', active: location.pathname === '/recruiter/interviews' },
    { icon: FiMail, label: 'Messages', path: '/recruiter/emails', active: location.pathname === '/recruiter/emails' },
    { icon: FiUser, label: 'Profile', path: '/recruiter/profile', active: location.pathname === '/recruiter/profile' }
  ];

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: '#f8fafc' }}>
      {/* Sidebar */}
      <motion.div
        initial={false}
        animate={{ width: sidebarOpen ? '280px' : '80px' }}
        style={{
          background: 'white',
          borderRight: '1px solid #e2e8f0',
          display: 'flex',
          flexDirection: 'column',
          position: 'relative',
          zIndex: 10
        }}
      >
        {/* Logo & Toggle */}
        <div style={{
          padding: '20px',
          borderBottom: '1px solid #e2e8f0',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <motion.div
            animate={{ opacity: sidebarOpen ? 1 : 0 }}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px'
            }}
          >
            <div style={{
              width: '40px',
              height: '40px',
              background: 'linear-gradient(135deg, #4f8cff, #6366f1)',
              borderRadius: '12px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              fontWeight: '700',
              fontSize: '18px'
            }}>
              R
            </div>
            {sidebarOpen && (
              <div>
                <h2 style={{ margin: 0, fontSize: '18px', fontWeight: '700', color: '#1a202c' }}>
                  Recruiter
                </h2>
                <p style={{ margin: 0, fontSize: '12px', color: '#718096' }}>
                  Talent Platform
                </p>
              </div>
            )}
          </motion.div>
          
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            style={{
              padding: '8px',
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              borderRadius: '6px',
              color: '#718096'
            }}
          >
            {sidebarOpen ? <FiX size={20} /> : <FiMenu size={20} />}
          </button>
        </div>

        {/* Quick Action */}
        <div style={{ padding: '20px' }}>
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => navigate('/recruiter/post-job')}
            style={{
              width: '100%',
              padding: sidebarOpen ? '12px 16px' : '12px',
              background: 'linear-gradient(135deg, #4f8cff, #6366f1)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontWeight: '600',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: sidebarOpen ? 'flex-start' : 'center',
              gap: '8px',
              boxShadow: '0 4px 12px rgba(79, 140, 255, 0.3)'
            }}
          >
            <FiPlus size={16} />
            {sidebarOpen && 'Post Job'}
          </motion.button>
        </div>

        {/* Navigation */}
        <nav style={{ flex: 1, padding: '0 20px' }}>
          {menuItems.map((item, index) => (
            <motion.button
              key={item.path}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => navigate(item.path)}
              style={{
                width: '100%',
                padding: sidebarOpen ? '12px 16px' : '12px',
                background: item.active ? '#f0f9ff' : 'transparent',
                border: item.active ? '1px solid #bae6fd' : '1px solid transparent',
                borderRadius: '8px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: sidebarOpen ? 'flex-start' : 'center',
                gap: '12px',
                marginBottom: '8px',
                color: item.active ? '#0369a1' : '#718096',
                fontWeight: item.active ? '600' : '500',
                transition: 'all 0.2s ease'
              }}
            >
              <item.icon size={20} />
              {sidebarOpen && (
                <span style={{ fontSize: '14px' }}>{item.label}</span>
              )}
            </motion.button>
          ))}
        </nav>

        {/* Logout */}
        <div style={{ padding: '20px', borderTop: '1px solid #e2e8f0' }}>
          <button
            onClick={handleLogout}
            style={{
              width: '100%',
              padding: sidebarOpen ? '12px 16px' : '12px',
              background: 'none',
              border: '1px solid #fed7d7',
              borderRadius: '8px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: sidebarOpen ? 'flex-start' : 'center',
              gap: '12px',
              color: '#dc2626',
              fontWeight: '500',
              fontSize: '14px'
            }}
          >
            <FiLogOut size={16} />
            {sidebarOpen && 'Logout'}
          </button>
        </div>
      </motion.div>

      {/* Main Content */}
      <div style={{ flex: 1, overflow: 'auto' }}>
        {children}
      </div>
      
      {/* Chatbot - Available on all recruiter pages */}
      <RecruiterChatbot />
    </div>
  );
};

export default RecruiterLayout;