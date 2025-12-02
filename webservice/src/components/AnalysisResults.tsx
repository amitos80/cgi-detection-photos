import React from 'react';
import type { PredictionResult } from '../api';

interface AnalysisResultsProps {
  filename: string;
  result: PredictionResult | null;
}

/**
 * Displays the results of the image analysis, including prediction, confidence,
 * analysis duration, and a detailed forensic analysis breakdown.
 * @param {AnalysisResultsProps} props - The props for the AnalysisResults component.
 * @returns {JSX.Element | null} The AnalysisResults component or null if no result is provided.
 */
const AnalysisResults: React.FC<AnalysisResultsProps> = ({ filename, result }) => {
  if (!result) return null;

  const predictionTextClass = result.prediction === 'cgi' ? 'text-accent-danger' : 'text-accent-success';
  const confidence = result.confidence !== null && result.confidence !== undefined ? (result.confidence * 100).toFixed(2) : 'N/A';

  return (
    <div className="mt-8 p-6 bg-light rounded-xl shadow-lg border border-gray-200 dark:bg-dark-800 dark:border-dark-700">
      <h2 className="text-2xl font-bold text-dark mb-5 border-b border-gray-200 pb-3 dark:text-light dark:border-dark-700 truncate">
        <span className="text-primary-dark">{filename || 'Unknown File'}</span>
      </h2>

      <div className="flex items-center justify-between mb-5 p-4 bg-primary-light rounded-lg dark:bg-primary-dark">
        <p className="text-xl font-semibold text-dark dark:text-light">
          Prediction: <span className={`${predictionTextClass} text-2xl`}>{result.prediction ? result.prediction.toUpperCase() : 'N/A'}</span>
        </p>
        <p className="text-xl font-semibold text-dark dark:text-light">
          Confidence: <span className="text-primary">{confidence}%</span>
        </p>
      </div>

      {result.analysis_duration && (
        <p className="mb-5 p-3 bg-accent-info text-dark rounded-lg font-medium text-center shadow-sm dark:bg-primary-dark dark:text-light">
          Backend analysis completed in: <span className="font-bold">{result.analysis_duration} seconds</span>.
        </p>
      )}

      {result.analysis_breakdown && (
        <div className="mt-8">
          <h3 className="text-xl font-bold text-dark mb-4 dark:text-light">Forensic Analysis Breakdown</h3>
          <div className="space-y-6">
            {result.analysis_breakdown.map((metric) => {
              const [min, max] = metric.normal_range;
              const isNormalized = metric.score >= 0 && metric.score <= 1 && min >= 0 && max <= 1;
              const rangeWidth = (max - min) * 100;
              const rangeLeft = min * 100;
              const scoreLeft = metric.score * 100;

              return (
                <div key={`visual-${metric.feature}`} className="bg-gray-50 p-4 rounded-lg
                shadow-sm border border-gray-100 dark:bg-dark-800 dark:border-dark-700">
                  <p className="font-semibold text-dark dark:text-light mb-2">
	                  {metric.feature}
	                  <span className="text-sm text-dark-500 dark:text-light-500">
		                  ({metric.score.toFixed(2)})
										</span></p>
                  <div className="h-6 w-full bg-gray-200 rounded-full relative overflow-hidden dark:bg-dark-700">
                    <div
                      className="absolute h-full bg-green-300 opacity-30 rounded-full"
                      style={{ left: `${rangeLeft}%`, width: `${rangeWidth}%` }}
                    ></div>
                    <div
                      className={`absolute h-full w-1 rounded-full opacity-75 
                      ${(scoreLeft >= rangeWidth || scoreLeft < rangeLeft) ?
	                      'bg-red-400' :
	                      'bg-green-500'}`}
                      style={{
												left: `${scoreLeft >= 100 ? 99 : scoreLeft}%`,
										}}
                    ></div>
                  </div>
                  <div className="relative w-full h-4 mt-1 text-xs text-dark-600 dark:text-light-600">
                    <span className="text-green-600" style={{ position: 'absolute', left: `0%`, transform: 'translateX(-50%)' }}>
                      {min}
                    </span>
                    <span className="text-green-600" style={{ position: 'absolute', left: `${max * 100}%`, transform: 'translateX(-50%)' }}>
                      {max.toFixed(2)}
                    </span>
                    <span
                      className={`font-bold ${
                        (scoreLeft > (max * 100) ||
	                        scoreLeft < (min * 100)) ?
	                        'text-red-500' :
	                        'text-green-600'
                      }`}
                      style={{
                        position: 'absolute',
                        left: `${scoreLeft}%`,
                        transform: 'translateX(-50%)',
                      }}
                    >
                      {metric.score.toFixed(2)}
                    </span>
                  </div>
                  <p className="mt-2 text-xs text-dark-600 dark:text-light-600">
                    Normal range: <span className="font-medium">{min.toFixed(2)} – {max.toFixed(2)}</span>
                    &nbsp;|&nbsp; Possible values: <span className="font-medium">0.00 – 1.00</span>
                    {isNormalized ? ' (values are normalized to [0, 1] for consistent comparison across features).' : ''}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalysisResults;
