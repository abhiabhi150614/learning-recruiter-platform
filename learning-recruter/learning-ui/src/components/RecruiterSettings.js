import React from 'react';
import RecruiterLayout from './RecruiterLayout';
import SocialConnections from './SocialConnections';

const RecruiterSettings = () => {
  return (
    <RecruiterLayout>
      <div style={{ padding: '32px', maxWidth: '1200px', margin: '0 auto' }}>
        <h2 style={{ fontSize: '28px', fontWeight: '700', marginBottom: '24px', color: '#1a202c' }}>
          Recruiter Settings
        </h2>
        
        <SocialConnections />
        
        <div style={{
          background: 'white',
          borderRadius: '16px',
          padding: '24px',
          marginTop: '24px',
          border: '1px solid #e2e8f0'
        }}>
          <h3 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '16px', color: '#1a202c' }}>
            Other Settings
          </h3>
          <p style={{ color: '#718096' }}>Additional recruiter settings coming soon...</p>
        </div>
      </div>
    </RecruiterLayout>
  );
};

export default RecruiterSettings;