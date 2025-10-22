import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { recruiterAuthenticatedFetch } from '../api';

const RecruiterAuthCheck = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('recruiter_token');
      if (!token) {
        navigate('/recruiter/login');
        return;
      }

      try {
        // Verify token by making a test request
        await recruiterAuthenticatedFetch('/recruiter/profile');
        setIsAuthenticated(true);
      } catch (error) {
        console.error('Auth check failed:', error);
        localStorage.removeItem('recruiter_token');
        localStorage.removeItem('recruiter_user');
        navigate('/recruiter/login');
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, [navigate]);

  if (loading) {
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

  if (!isAuthenticated) {
    return null;
  }

  return children;
};

export default RecruiterAuthCheck;