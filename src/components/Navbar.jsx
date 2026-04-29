import React from 'react';
import { Shield, List, Plus, LogOut } from 'lucide-react';
import { Link } from 'react-router-dom';
import './Navbar.css';

const Navbar = () => {
  return (
    <nav className="navbar">
      <div className="navbar-left">
        <Link to="/" className="brand-logo">
          <Shield className="brand-icon" size={24} />
          <span className="brand-title">FaceForge</span>
          <span className="brand-subtitle">Forensic Sketch Console</span>
        </Link>
        <div className="nav-links">
          <Link to="/dashboard" className="nav-link active">
            <List size={16} />
            Cases
          </Link>
          <Link to="#" className="nav-link">
            <Plus size={16} />
            New Case
          </Link>
        </div>
      </div>
      <div className="navbar-right">
        <div className="user-info">
          <div className="user-name">Detective Sarah Chen</div>
          <div className="user-badge">Badge B-4271 • <span className="user-role">OFFICER</span></div>
        </div>
        <Link to="/login" className="sign-out-btn">
          <LogOut size={16} />
          Sign out
        </Link>
      </div>
    </nav>
  );
};

export default Navbar;
