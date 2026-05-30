import React, { useEffect, useState } from 'react';

export default function RiskGauge({ score = 0, size = 180 }) {
  const [animatedScore, setAnimatedScore] = useState(0);

  useEffect(() => {
    // Basic smooth transition on render
    const timer = setTimeout(() => {
      setAnimatedScore(score);
    }, 100);
    return () => clearTimeout(timer);
  }, [score]);

  // Calculations for circular path
  const radius = size * 0.4;
  const strokeWidth = size * 0.08;
  const normalizedRadius = radius - strokeWidth / 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  
  // Clean representation of score (0-10)
  const displayScore = Number(score || 0).toFixed(1);
  const percent = Math.min(Math.max(score / 10, 0), 1);
  const strokeDashoffset = circumference - percent * circumference;

  // Determine color based on risk tier
  let colorVar = 'var(--risk-low)';
  let riskLevel = 'Low Risk';

  if (score >= 7.0) {
    colorVar = 'var(--risk-critical)';
    riskLevel = 'Critical Risk';
  } else if (score >= 5.0) {
    colorVar = 'var(--risk-high)';
    riskLevel = 'High Risk';
  } else if (score >= 3.0) {
    colorVar = 'var(--risk-medium)';
    riskLevel = 'Medium Risk';
  }

  return (
    <div className="risk-gauge-container" style={{ width: size, height: size + 40 }}>
      <svg
        height={size}
        width={size}
        className="risk-gauge-svg"
      >
        {/* Background track */}
        <circle
          stroke="rgba(255, 255, 255, 0.03)"
          fill="transparent"
          strokeWidth={strokeWidth}
          r={normalizedRadius}
          cx={size / 2}
          cy={size / 2}
        />
        {/* Colored progress arc */}
        <circle
          stroke={colorVar}
          fill="transparent"
          strokeWidth={strokeWidth}
          strokeDasharray={circumference + ' ' + circumference}
          style={{ strokeDashoffset, transition: 'stroke-dashoffset 1s ease-in-out' }}
          strokeLinecap="round"
          r={normalizedRadius}
          cx={size / 2}
          cy={size / 2}
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
        />
      </svg>
      <div className="risk-gauge-inner">
        <span className="risk-gauge-number" style={{ color: colorVar }}>
          {displayScore}
        </span>
        <span className="risk-gauge-label" style={{ color: 'var(--text-secondary)' }}>
          {riskLevel}
        </span>
      </div>
    </div>
  );
}
