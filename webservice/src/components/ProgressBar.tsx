import React from 'react';

interface ProgressBarProps {
  progress: number;
  text: string;
  isVisible: boolean;
}

/**
 * Displays a progress bar with dynamic text during image analysis.
 * @param {ProgressBarProps} props - The props for the ProgressBar component.
 * @returns {JSX.Element | null} The ProgressBar component or null if not visible.
 */
const ProgressBar: React.FC<ProgressBarProps> = ({ progress, text, isVisible }) => {
  if (!isVisible) return null;

  return (
    <div className="mt-6 p-4 bg-light rounded-xl shadow-md">
      <h4 className="text-xl font-bold text-primary-dark mb-3 text-center">Analyzing Image...</h4>
      <div className="w-full bg-gray-200 rounded-full h-4 relative overflow-hidden dark:bg-dark-600">
        <div
          className="bg-primary h-full rounded-full text-center text-white text-xs font-semibold flex items-center justify-center transition-all duration-500 ease-out"
          style={{ width: `${progress}%` }}
        >
          {Math.round(progress) > 5 ? `${Math.round(progress)}%` : ''}
        </div>
      </div>
      <p className="text-center text-dark-400 text-sm mt-3 animate-pulse">{text}</p>
    </div>
  );
};

export default ProgressBar;
