import React from 'react';

interface ProgressBarProps {
  progress: number;
  text: string;
  isVisible: boolean;
}

const ProgressBar: React.FC<ProgressBarProps> = ({ progress, text, isVisible }) => {
  if (!isVisible) return null;

  return (
    <div className="mt-6 p-4 bg-gray-50 rounded-lg shadow-inner">
      <h4 className="text-xl font-bold text-blue-700 mb-3 text-center">Analyzing Image...</h4>
      <div className="w-full bg-gray-200 rounded-full h-4 relative overflow-hidden">
        <div
          className="bg-blue-600 h-full rounded-full text-center text-white text-xs font-semibold flex items-center justify-center transition-all duration-500 ease-out"
          style={{ width: `${progress}%` }}
        >
          {Math.round(progress) > 5 ? `${Math.round(progress)}%` : ''}
        </div>
      </div>
      <p className="text-center text-gray-600 text-sm mt-3 animate-pulse">{text}</p>
    </div>
  );
};

export default ProgressBar;
