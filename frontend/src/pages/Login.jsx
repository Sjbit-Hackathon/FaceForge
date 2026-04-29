import React, { useState } from 'react';
import { Shield, Eye, EyeOff, Loader2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import './Login.css';

const API_BASE = 'http://127.0.0.1:8000';

const Login = () => {
  const navigate = useNavigate();
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('test@example.com');
  const [password, setPassword] = useState('password');
  const [fullName, setFullName] = useState('Detective Smith');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    
    try {
      const endpoint = isLogin ? '/auth/login' : '/auth/register';
      const payload = isLogin 
        ? { email: username, password }
        : { email: username, password, full_name: fullName, badge_id: '1234', role: 'detective' };

      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || data.message || 'Authentication failed');
      }

      localStorage.setItem('token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));

      if (data.user.role === 'admin') {
        navigate('/audit');
      } else {
        navigate('/dashboard');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-header">
        <Shield size={32} className="login-logo-icon" />
        <h1 className="login-title">FaceForge</h1>
        <p className="login-subtitle">FORENSIC SUITE</p>
      </div>

      <div className="login-card">
        <form onSubmit={handleSubmit} className="login-form">
          {error && <div className="error-message" style={{ color: '#ff6b6b', marginBottom: '1rem', fontSize: '0.9rem' }}>{error}</div>}
          
          {!isLogin && (
            <div className="form-group">
              <input 
                type="text" 
                placeholder="Full Name"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="login-input" 
                required
              />
            </div>
          )}

          <div className="form-group">
            <input 
              type="text" 
              placeholder="Email / Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="login-input" 
              required
            />
          </div>

          <div className="form-group password-group">
            <input 
              type={showPassword ? "text" : "password"} 
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="login-input" 
              required
            />
            <button 
              type="button" 
              className="toggle-password"
              onClick={() => setShowPassword(!showPassword)}
            >
              {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>

          <button type="submit" className="btn-primary login-btn" disabled={isLoading}>
            {isLoading ? <Loader2 size={16} className="spinner" /> : (isLogin ? "Sign In" : "Register")}
          </button>

          <p style={{ textAlign: 'center', marginTop: '1rem', color: '#888', fontSize: '0.9rem', cursor: 'pointer' }} onClick={() => setIsLogin(!isLogin)}>
            {isLogin ? "Need an account? Register" : "Already have an account? Sign In"}
          </p>
        </form>
      </div>
    </div>
  );
};

export default Login;
