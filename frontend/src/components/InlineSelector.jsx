import React, { useState, useRef, useEffect } from 'react';
import './InlineSelector.css';

const LockIcon = ({ isLocked }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="16"
    height="16"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={`lock-icon ${isLocked ? 'locked' : 'unlocked'}`}
  >
    {isLocked ? (
      <>
        <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
        <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
      </>
    ) : (
      <>
        <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
        <path d="M7 11V7a5 5 0 0 1 9.9-1"></path>
      </>
    )}
  </svg>
);

const ToggleSwitch = ({ isOn, onToggle }) => (
  <button 
    className={`toggle-switch ${isOn ? 'on' : 'off'}`} 
    onClick={(e) => {
      e.stopPropagation();
      onToggle();
    }}
    role="switch"
    aria-checked={isOn}
    aria-label="Toggle lock"
  >
    <span className="toggle-thumb" />
  </button>
);

export const InlineSelector = ({ group, attributes, onChange }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isLocked, setIsLocked] = useState(false);
  const [selections, setSelections] = useState({});
  const containerRef = useRef(null);

  // Close when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen]);

  const handleSelect = (attribute, value) => {
    const newSelections = { ...selections, [attribute]: value };
    setSelections(newSelections);
    if (onChange) {
      onChange({ group, value: `${attribute}: ${value}`, selections: newSelections });
    }
  };

  const toggleLock = () => {
    setIsLocked(!isLocked);
  };

  return (
    <div className={`inline-selector-container ${isOpen ? 'open' : ''}`} ref={containerRef}>
      <button 
        className="selector-header" 
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
      >
        <div className="header-left">
          <LockIcon isLocked={isLocked} />
          <span className="group-name">{group}</span>
        </div>
        <ToggleSwitch isOn={isLocked} onToggle={toggleLock} />
      </button>

      {isOpen && (
        <div className="selector-dropdown">
          <div className="attributes-row">
            {Object.entries(attributes).map(([attrName, options]) => (
              <div key={attrName} className="attribute-group">
                <span className="attribute-label">{attrName}:</span>
                <div className="options-list" role="radiogroup" aria-label={attrName}>
                  {options.map((option) => {
                    const isActive = selections[attrName] === option;
                    return (
                      <button
                        key={option}
                        className={`chip ${isActive ? 'active' : ''}`}
                        onClick={() => handleSelect(attrName, option)}
                        role="radio"
                        aria-checked={isActive}
                      >
                        {option}
                      </button>
                    );
                  })}
                </div>
                <div className="divider" />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
