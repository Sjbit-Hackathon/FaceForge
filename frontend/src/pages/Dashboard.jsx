import React, { useState, useEffect } from 'react';
import { Folder, Activity, FileCheck, Plus, X, Loader2 } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import './Dashboard.css';

const API_BASE = 'http://127.0.0.1:8000';

const Dashboard = () => {
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newCaseNumber, setNewCaseNumber] = useState('');
  const [newCaseTitle, setNewCaseTitle] = useState('');
  const [sessions, setSessions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${API_BASE}/sessions`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (res.ok) {
        const data = await res.json();
        setSessions(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateSession = async (e) => {
    e.preventDefault();
    if (!newCaseNumber || !newCaseTitle) return;
    setIsCreating(true);
    
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${API_BASE}/sessions/create`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          case_number: newCaseNumber,
          title: newCaseTitle,
          notes: ''
        })
      });
      
      if (res.ok) {
        const data = await res.json();
        navigate(`/session/${data.id}`);
      }
    } catch (err) {
      console.error(err);
      setIsCreating(false);
    }
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1 className="page-title">Officer Dashboard</h1>
        <button className="btn-primary" onClick={() => setIsModalOpen(true)}>
          <Plus size={16} /> New Case Session
        </button>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <Folder size={20} className="stat-icon" />
          <div className="stat-content">
            <div className="stat-label">Total Sessions</div>
            <div className="stat-value">{sessions.length}</div>
          </div>
        </div>
        <div className="stat-card">
          <FileCheck size={20} className="stat-icon text-success" />
          <div className="stat-content">
            <div className="stat-label">Exported Cases</div>
            <div className="stat-value">{sessions.filter(s => s.status === 'Exported' || s.status === 'closed').length}</div>
          </div>
        </div>
        <div className="stat-card">
          <Activity size={20} className="stat-icon text-primary" />
          <div className="stat-content">
            <div className="stat-label">Active Sessions</div>
            <div className="stat-value">{sessions.filter(s => s.status === 'active').length}</div>
          </div>
        </div>
      </div>

      <div className="sessions-panel">
        <h2 className="panel-title">Recent Sessions</h2>
        
        {isLoading ? (
          <div className="empty-state">
            <Loader2 className="spinner" size={24} />
          </div>
        ) : sessions.length === 0 ? (
          <div className="empty-state">
            <p>No sessions yet — start your first case</p>
          </div>
        ) : (
          <table className="sessions-table">
            <thead>
              <tr>
                <th>Case #</th>
                <th>Title</th>
                <th>Date</th>
                <th>Versions</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {sessions.map(s => (
                <tr key={s.id}>
                  <td className="mono">{s.case_number}</td>
                  <td>{s.title}</td>
                  <td className="mono">{new Date(s.created_at).toLocaleDateString()}</td>
                  <td>{s.versions ? s.versions.length : 0}</td>
                  <td>
                    <span className={`status-badge ${s.status.toLowerCase()}`}>
                      {s.status}
                    </span>
                  </td>
                  <td>
                    <Link to={`/session/${s.id}`} className="btn-secondary action-btn">
                      {s.status === 'active' ? 'Continue' : 'View'}
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {isModalOpen && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>New Case Session</h3>
              <button className="icon-btn" onClick={() => setIsModalOpen(false)}><X size={16} /></button>
            </div>
            <form onSubmit={handleCreateSession}>
              <div className="form-group">
                <label>Case Number</label>
                <input 
                  type="text" 
                  value={newCaseNumber}
                  onChange={(e) => setNewCaseNumber(e.target.value)}
                  placeholder="e.g. CASE-2026-003"
                  className="login-input"
                  required
                />
              </div>
              <div className="form-group">
                <label>Case Title</label>
                <input 
                  type="text" 
                  value={newCaseTitle}
                  onChange={(e) => setNewCaseTitle(e.target.value)}
                  placeholder="e.g. Downtown Assault"
                  className="login-input"
                  required
                />
              </div>
              <div className="modal-actions">
                <button type="button" className="btn-secondary" onClick={() => setIsModalOpen(false)}>Cancel</button>
                <button type="submit" className="btn-primary" disabled={isCreating}>
                  {isCreating ? <Loader2 size={16} className="spinner" /> : "Create Session"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
