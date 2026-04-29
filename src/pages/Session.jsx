import React, { useState, useRef, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Download, PenTool, ChevronDown } from 'lucide-react';
import './Session.css';

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

const FeatureDropdown = ({ group, attributes, isOpen, onToggle, selections, onSelect }) => {
  const containerRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        if (isOpen) onToggle(null);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen, onToggle]);

  return (
    <div className={`feature-dropdown-container ${isOpen ? 'open' : ''}`} ref={containerRef}>
      <button 
        className="dropdown-trigger" 
        onClick={() => onToggle(isOpen ? null : group)}
        aria-expanded={isOpen}
      >
        <span className="group-name">{group}</span>
        <ChevronDown size={14} className={`chevron ${isOpen ? 'rotated' : ''}`} />
      </button>

      {isOpen && (
        <div className="dropdown-panel">
          <div className="attributes-grid">
            {Object.entries(attributes).map(([attrName, options]) => (
              <div key={attrName} className="attribute-row">
                <span className="attribute-label">{attrName}:</span>
                <div className="options-pills">
                  {options.map((option) => {
                    const isActive = selections[group]?.[attrName] === option;
                    return (
                      <button
                        key={option}
                        className={`pill-btn ${isActive ? 'active' : ''}`}
                        onClick={() => onSelect(group, attrName, option)}
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
  );
};

const Session = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [hasSketch, setHasSketch] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  
  // Right panel states
  const [witnessInput, setWitnessInput] = useState('');
  const [refinementInput, setRefinementInput] = useState('');
  
  // Feature Controls State
  const [openDropdown, setOpenDropdown] = useState(null);
  const [featureSelections, setFeatureSelections] = useState({
    Eyes: {}, Nose: {}, Mouth: {}, Jaw: {}
  });

  const handleSelectFeature = (group, attrName, value) => {
    setFeatureSelections(prev => ({
      ...prev,
      [group]: {
        ...prev[group],
        [attrName]: value
      }
    }));
  };

  const handleGenerate = () => {
    setIsGenerating(true);
    setTimeout(() => {
      setIsGenerating(false);
      setHasSketch(true);
    }, 2000);
  };

  const handleRefine = () => {
    setIsGenerating(true);
    setTimeout(() => {
      setIsGenerating(false);
      setRefinementInput('');
    }, 1500);
  };

  return (
    <div className="session-layout">
      {/* LEFT PANEL - HD Suspect Visualizer */}
      <div className="session-panel left-panel">
        <div className="panel-header">
          <div className="header-left">
            <h2>HD Suspect Visualizer</h2>
            <span className="case-badge mono">{id || 'CASE-001'}</span>
            <span className="pulse-indicator"></span>
          </div>
          <button 
            className="btn-success export-btn" 
            disabled={!hasSketch}
            onClick={() => navigate(`/session/${id}/export`)}
          >
            <Download size={14} /> Generate Forensic Report
          </button>
        </div>

        <div className="canvas-wrapper">
          <div className="canvas-container">
            {hasSketch ? (
              <div className="sketch-image fade-in">
                <div className="dummy-sketch">HD SKETCH</div>
              </div>
            ) : (
              <div className="wireframe-placeholder">
                SVG WIREFRAME PLACEHOLDER
              </div>
            )}

            {isGenerating && (
              <div className="pipeline-overlay">
                <div className="progress-bar">
                  <div className="progress-fill animated-fill"></div>
                </div>
                <p>Synthesizing forensic features...</p>
              </div>
            )}
          </div>
        </div>

        {/* Feature Controls replacing Locks */}
        <div className="horizontal-feature-controls">
          {Object.entries(featureGroups).map(([group, attributes]) => (
            <FeatureDropdown 
              key={group}
              group={group}
              attributes={attributes}
              isOpen={openDropdown === group}
              onToggle={setOpenDropdown}
              selections={featureSelections}
              onSelect={handleSelectFeature}
            />
          ))}
        </div>

        {/* Version History Strip */}
        <div className="version-history-container">
          <h4 className="section-subtitle">Version History</h4>
          <div className="version-strip">
            <div className="version-thumb active"><span className="v-badge mono">v3</span></div>
            <div className="version-thumb"><span className="v-badge mono">v2</span></div>
            <div className="version-thumb"><span className="v-badge mono">v1</span></div>
          </div>
        </div>
      </div>

      {/* RIGHT PANEL - AI Interrogator */}
      <div className="session-panel right-panel">
        <div className="panel-header">
          <h2>AI Interrogator</h2>
          <span className="gemini-badge">Gemini 2.0 Flash</span>
        </div>

        <div className="interrogator-content">
          <div className="input-section">
            <label className="section-label">Witness Description</label>
            <textarea 
              className="interrogator-textarea primary-input"
              placeholder="Describe the suspect in detail (e.g. Male, late 30s, short dark brown hair...)"
              value={witnessInput}
              onChange={(e) => setWitnessInput(e.target.value)}
            />
            <button 
              className="btn-primary full-width" 
              onClick={handleGenerate} 
              disabled={!witnessInput || isGenerating}
            >
              <PenTool size={16} /> Generate HD Sketch
            </button>
          </div>

          <div className="divider-line"></div>

          <div className="input-section">
            <label className="section-label">Refine Sketch</label>
            <textarea 
              className="interrogator-textarea secondary-input"
              placeholder="Add a small correction (e.g. Make the nose narrower with a slight bump)"
              value={refinementInput}
              onChange={(e) => setRefinementInput(e.target.value)}
              disabled={!hasSketch}
            />
            <button 
              className="btn-secondary full-width" 
              onClick={handleRefine} 
              disabled={!hasSketch || !refinementInput || isGenerating}
            >
              Refine Sketch
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Session;
