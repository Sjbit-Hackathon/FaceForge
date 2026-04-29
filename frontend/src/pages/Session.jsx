import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { PenTool, ChevronDown, Loader2, Download } from 'lucide-react';
import SpeechInput from '../components/SpeechInput';
import './Session.css';

const API_BASE = 'http://127.0.0.1:8000';

const featureGroups = {
  Eyes: {
    Size: ["Small", "Medium", "Large", "Wider"],
    Shape: ["Round", "Almond", "Narrow"],
    Spacing: ["Close", "Normal", "Wide"],
    Depth: ["Deep", "Normal", "Protruding"]
  },
  Nose: {
    Width: ["Narrow", "Medium", "Broad"],
    Bridge: ["Straight", "Flat", "Curved"],
    Tip: ["Pointed", "Rounded"],
    Length: ["Short", "Medium", "Long"]
  },
  Mouth: {
    "Lip Size": ["Thin", "Medium", "Full"],
    Shape: ["Straight", "Curved", "Downturned"],
    Width: ["Narrow", "Medium", "Wide"]
  },
  Jaw: {
    Width: ["Narrow", "Medium", "Wide"],
    Jawline: ["Soft", "Defined", "Square"],
    Chin: ["Round", "Pointed", "Square"]
  }
};

const FeatureControls = ({ activeDropdown, setActiveDropdown, selections, onSelect }) => {
  return (
    <div 
      className="feature-controls-bar"
      onMouseLeave={() => setActiveDropdown(null)}
    >
      <div className="horizontal-control-pill">
        {Object.keys(featureGroups).map((group) => (
          <div 
            key={group}
            className="control-trigger-wrapper"
            onMouseEnter={() => setActiveDropdown(group)}
          >
            <button className={`control-trigger ${activeDropdown === group ? 'active' : ''}`}>
              {group} <ChevronDown size={14} className={`chevron ${activeDropdown === group ? 'rotated' : ''}`} />
            </button>
            
            {activeDropdown === group && (
              <div className="compact-dropdown-panel">
                <div className="dropdown-content">
                  {Object.entries(featureGroups[group]).map(([attrName, options]) => (
                    <div key={attrName} className="attr-row">
                      <span className="attr-label">{attrName}:</span>
                      <div className="pill-group">
                        {options.map((option) => {
                          const isActive = selections[group]?.[attrName] === option;
                          return (
                            <button
                              key={option}
                              className={`pill-btn ${isActive ? 'active' : ''}`}
                              onClick={() => {
                                onSelect(group, attrName, option);
                                setActiveDropdown(null);
                              }}
                            >
                              {option}
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

const Session = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  
  // States
  const [hasSketch, setHasSketch] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isIterating, setIsIterating] = useState(false);
  const [witnessInput, setWitnessInput] = useState('');
  const [refinementInput, setRefinementInput] = useState('');
  const [activeDropdown, setActiveDropdown] = useState(null);
  const [currentVersion, setCurrentVersion] = useState(null);
  const [apiError, setApiError] = useState('');
  
  const [featureSelections, setFeatureSelections] = useState({
    Eyes: {}, Nose: {}, Mouth: {}, Jaw: {}
  });

  const handleSelectFeature = (group, attrName, value) => {
    setFeatureSelections(prev => ({
      ...prev, [group]: { ...prev[group], [attrName]: value }
    }));
  };

  const handleGenerate = async () => {
    if (!witnessInput) return;
    setIsGenerating(true);
    setApiError('');
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${API_BASE}/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          session_id: id,
          witness_description: witnessInput,
          negative_prompt: "blurry, distorted, unrealistic"
        })
      });
      if (res.ok) {
        const data = await res.json();
        setHasSketch(true);
        setCurrentVersion(data);
      } else {
        const errorData = await res.json();
        setApiError(errorData.detail || "Failed to generate face. Please check your API keys.");
      }
    } catch (err) {
      console.error(err);
      setApiError("Network error. Is the backend running?");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleRefine = async () => {
    if (!refinementInput || !currentVersion) return;
    setIsIterating(true);
    setApiError('');
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${API_BASE}/refine`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          session_id: id,
          parent_version_id: currentVersion.version_id,
          prompt: refinementInput,
          negative_prompt: "blurry, distorted"
        })
      });
      if (res.ok) {
        const newVersion = await res.json();
        setCurrentVersion(newVersion);
        setRefinementInput('');
      } else {
        const errorData = await res.json();
        setApiError(errorData.detail || "Failed to refine face. Please check your API keys.");
      }
    } catch (err) {
      console.error(err);
      setApiError("Network error. Is the backend running?");
    } finally {
      setIsIterating(false);
    }
  };

  return (
    <div className="unified-session-layout second-picture-layout">
      
      {/* LEFT COLUMN (65%) */}
      <div className="column-left">
        <div className="card sketch-card transparent-card">
          <div className="card-header border-none align-center">
            <div className="header-meta">
              <h3 style={{ fontSize: '20px', fontWeight: '600' }}>HD Suspect Visualizer</h3>
              <span className="case-badge">CASE-2026-001</span>
              <span className="status-dot"></span>
            </div>
            <button className="btn-success btn-sm flex-gap">
              <Download size={14} /> Generate Forensic Report
            </button>
          </div>
          
          <div className="card-body canvas-body pt-0">
            <div className="canvas-viewport dark-viewport">
              {hasSketch && currentVersion ? (
                <div className="sketch-image-container">
                  <img src={currentVersion.image_url} alt="Composite Sketch" className="sketch-render" />
                </div>
              ) : (
                <div className="wireframe-placeholder">SVG WIREFRAME PLACEHOLDER</div>
              )}
            </div>
            
            <FeatureControls 
              activeDropdown={activeDropdown}
              setActiveDropdown={setActiveDropdown}
              selections={featureSelections}
              onSelect={handleSelectFeature}
            />
          </div>
        </div>
      </div>

      {/* RIGHT COLUMN (35%) */}
      <div className="column-right right-panel-spacing">
        
        {/* AI Interrogator Card */}
        <div className="card interrogator-card">
          <div className="card-header border-none pb-2">
            <h3>AI Interrogator</h3>
            <span className="gemini-badge">Gemini 2.0 Flash</span>
          </div>
          <div className="card-body pt-0">
            <label className="input-label">Witness Description</label>
            <div className="prompt-container relative mt-2">
              <textarea 
                className="ui-textarea tall-textarea"
                placeholder="Describe the suspect in detail (e.g. Male, late 30s, short dark brown hair...)"
                value={witnessInput}
                onChange={(e) => setWitnessInput(e.target.value)}
              />
              <div className="speech-input-wrapper">
                <SpeechInput onTranscript={(text) => setWitnessInput(prev => prev + (prev ? " " : "") + text)} />
              </div>
            </div>
            
            <button 
              className="btn-primary full-width mt-4" 
              onClick={handleGenerate}
              disabled={isGenerating || !witnessInput}
            >
              {isGenerating ? <Loader2 size={16} className="spinner" /> : <><PenTool size={16} /> Generate HD Sketch</>}
            </button>
            
            {apiError && (
              <div className="accuracy-alert mt-4" style={{ backgroundColor: 'rgba(239, 68, 68, 0.1)', borderColor: 'rgba(239, 68, 68, 0.3)', color: '#ef4444' }}>
                <strong>Error:</strong> {apiError}
              </div>
            )}
          </div>
        </div>

        {/* Refine Sketch Card */}
        <div className="card refine-card">
          <div className="card-header border-none pb-2">
            <h3>Refine Sketch</h3>
          </div>
          <div className="card-body pt-0">
            <textarea 
              className="ui-textarea sm mt-2"
              placeholder="Add a small correction (e.g. Make the nose narrower with a slight bump)"
              value={refinementInput}
              onChange={(e) => setRefinementInput(e.target.value)}
            />
          </div>
        </div>

      </div>
    </div>
  );
};

export default Session;
