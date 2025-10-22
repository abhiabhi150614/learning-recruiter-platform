import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FaGoogle, FaSpinner } from 'react-icons/fa';
import { useNavigate } from 'react-router-dom';

const RecruiterGoogleAuth = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleGoogleLogin = async () => {
    setLoading(true);
    setError('');
    
    try {
      // Initialize Composio Google OAuth
      const response = await fetch('http://localhost:8000/api/recruiter/auth/google/init', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      const data = await response.json();
      
      if (data.auth_url) {
        // Redirect to Google OAuth
        window.location.href = data.auth_url;
      } else {
        setError('Failed to initialize Google authentication');
      }
    } catch (error) {
      setError('Authentication failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Handle OAuth callback
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    const state = urlParams.get('state');
    
    if (code && state) {
      handleOAuthCallback(code, state);
    }
  }, []);

  const handleOAuthCallback = async (code, state) => {
    setLoading(true);
    
    try {
      const response = await fetch('http://localhost:8000/api/recruiter/auth/google/callback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code, state }),
      });
      
      const data = await response.json();
      
      if (data.access_token) {
        localStorage.setItem('recruiter_token', data.access_token);
        localStorage.setItem('recruiter_user', JSON.stringify(data.user));
        navigate('/recruiter');
      } else {
        setError('Authentication failed');
      }
    } catch (error) {
      setError('Authentication callback failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md"
      >
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">Recruiter Portal</h1>
          <p className="text-gray-600">Sign in with your Google account</p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={handleGoogleLogin}
          disabled={loading}
          className="w-full bg-white border-2 border-gray-300 text-gray-700 py-3 px-4 rounded-lg font-medium hover:bg-gray-50 hover:border-gray-400 transition-all duration-200 flex items-center justify-center space-x-3 disabled:opacity-50"
        >
          {loading ? (
            <FaSpinner className="animate-spin text-xl" />
          ) : (
            <>
              <FaGoogle className="text-xl text-red-500" />
              <span>Continue with Google</span>
            </>
          )}
        </motion.button>

        <div className="mt-6 text-center">
          <p className="text-sm text-gray-500">
            By signing in, you agree to our Terms of Service and Privacy Policy
          </p>
        </div>
      </motion.div>
    </div>
  );
};

export default RecruiterGoogleAuth;