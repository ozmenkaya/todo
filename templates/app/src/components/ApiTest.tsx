import React, { useState, useEffect } from 'react';
import { Button, Typography, Box, Alert } from '@mui/material';
import { apiService } from '../services/api';

export const ApiTest: React.FC = () => {
  const [testResult, setTestResult] = useState<string>('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Test on mount
    testConnection();
  }, []);

  const testConnection = async () => {
    setLoading(true);
    setTestResult('Testing connection...');
    
    try {
      // Test the current user endpoint with detailed error info
      const response = await fetch('http://localhost:5005/api/current_user', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        mode: 'cors', // Explicitly set CORS mode
      });
      
      const data = await response.text();
      setTestResult(`✅ Direct fetch - Status: ${response.status}, CORS headers: ${response.headers.get('Access-Control-Allow-Origin')}, Response: ${data}`);
    } catch (error: any) {
      setTestResult(`❌ Direct fetch failed: ${error.message}\nError type: ${error.name}\nStack: ${error.stack}`);
    }
    
    setLoading(false);
  };

  const testApiService = async () => {
    setLoading(true);
    setTestResult('Testing API service...');
    
    try {
      const result = await apiService.getCurrentUser();
      setTestResult(`✅ API Service - Success: ${result.success}, Data: ${JSON.stringify(result, null, 2)}`);
    } catch (error: any) {
      setTestResult(`❌ API Service failed: ${error.message}\nError type: ${error.name}\nStack: ${error.stack}`);
    }
    
    setLoading(false);
  };

  const testLogin = async () => {
    setLoading(true);
    setTestResult('Testing login...');
    
    try {
      const response = await fetch('http://localhost:5005/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        mode: 'cors',
        body: JSON.stringify({ username: 'admin', password: 'admin123' }),
      });
      
      const data = await response.text();
      setTestResult(`✅ Login test - Status: ${response.status}, Response: ${data}`);
    } catch (error: any) {
      setTestResult(`❌ Login test failed: ${error.message}`);
    }
    
    setLoading(false);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        API Connection Test (Backend: localhost:5005)
      </Typography>
      
      <Box sx={{ mb: 2 }}>
        <Button 
          variant="contained" 
          onClick={testConnection}
          disabled={loading}
          sx={{ mr: 1, mb: 1 }}
          size="small"
        >
          Test Current User
        </Button>
        
        <Button 
          variant="outlined" 
          onClick={testApiService}
          disabled={loading}
          sx={{ mr: 1, mb: 1 }}
          size="small"
        >
          Test API Service
        </Button>

        <Button 
          variant="outlined" 
          onClick={testLogin}
          disabled={loading}
          sx={{ mr: 1, mb: 1 }}
          size="small"
        >
          Test Login
        </Button>
      </Box>
      
      {testResult && (
        <Alert severity={testResult.includes('✅') ? 'success' : 'info'}>
          <pre style={{ 
            whiteSpace: 'pre-wrap', 
            fontSize: '12px',
            maxHeight: '200px',
            overflow: 'auto'
          }}>
            {testResult}
          </pre>
        </Alert>
      )}
    </Box>
  );
};
