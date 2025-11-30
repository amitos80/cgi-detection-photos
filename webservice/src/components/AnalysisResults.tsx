import React from 'react';
import type { PredictionResult } from '../api';

interface AnalysisResultsProps {
  filename: string;
  result: PredictionResult | null;
}

const AnalysisResults: React.FC<AnalysisResultsProps> = ({ filename, result }) => {
  if (!result) return null;

  const predictionTextClass = result.prediction === 'cgi' ? 'text-red-600' : 'text-green-600';
  // Safely calculate confidence, providing a fallback if result.confidence is null/undefined
  const confidence = result.confidence !== null && result.confidence !== undefined ? (result.confidence * 100).toFixed(2) : 'N/A';

  return (
    <div className="mt-8 p-6 bg-white rounded-xl shadow-lg border border-gray-100">
      <h2 className="text-2xl font-bold text-gray-800 mb-5 border-b pb-3">Analysis Report for <span className="text-blue-700">{filename || 'Unknown File'}</span>:</h2>
      
      <div className="flex items-center justify-between mb-5 p-4 bg-blue-50 rounded-lg">
        <p className="text-xl font-semibold">
          Prediction: <span className={`${predictionTextClass} text-2xl`}>{result.prediction ? result.prediction.toUpperCase() : 'N/A'}</span>
        </p>
        <p className="text-xl font-semibold text-gray-700">
          Confidence: <span className="text-blue-600">{confidence}%</span>
        </p>
      </div>

      {result.analysis_duration && (
        <p className="mb-5 p-3 bg-green-100 text-green-800 rounded-lg font-medium text-center shadow-sm">
          Backend analysis completed in: <span className="font-bold">{result.analysis_duration} seconds</span>.
        </p>
      )}

      {result.analysis_breakdown && (
        <div className="mt-8">
          <h3 className="text-xl font-bold text-gray-800 mb-4">Forensic Analysis Breakdown</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full bg-white border border-gray-200 rounded-lg">
              <thead className="bg-gray-100">
                <tr>
                  <th className="py-3 px-4 text-left text-sm font-semibold text-gray-600 uppercase tracking-wider">Feature</th>
                  <th className="py-3 px-4 text-left text-sm font-semibold text-gray-600 uppercase tracking-wider">Score</th>
                  <th className="py-3 px-4 text-left text-sm font-semibold text-gray-600 uppercase tracking-wider">Insight</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {result.analysis_breakdown.map((metric) => {
                  const [min, max] = metric.normal_range;
                  
                  const featureExplanations: { [key: string]: string } = {
                    'ELA': 'Error Level Analysis (ELA) detects differences in compression levels within an image. A high score suggests that parts of the image were added or modified, which is common in CGI.',
                    'CFA': 'Color Filter Array (CFA) analysis looks for the specific sensor pattern that digital cameras leave on photos. A low score or absence of this pattern is a strong indicator of a CGI image.',
                    'HOS': 'Higher-Order Statistics (HOS) analyzes the subtle noise patterns and textures in an image. Real photos have characteristic noise, while CGI images are often too clean or have artificial noise.',
                    'JPEG Ghost': 'This method looks for artifacts from repeated JPEG compression. If an image is a composite of multiple JPEGs, it may have "ghostly" remnants of previous compressions, indicating manipulation.',
                    'JPEG Dimples': 'JPEG Dimples are subtle grid-like artifacts that can appear in authentic photos due to the JPEG compression algorithm. Their absence might suggest an image is not a real photograph.',
                    'Rambino': 'Rambino is a machine learning model trained to spot subtle artifacts and inconsistencies across a wide range of features that are often missed by individual forensic tests.',
                    'Geometric': 'This analysis checks for inconsistencies in 3D geometry, such as impossible shapes, incorrect perspective, or unnatural arrangements of objects in the scene.',
                    'Lighting': 'Lighting analysis detects inconsistencies in how light and shadows behave in the image. CGI often fails to perfectly replicate the complex lighting of a real-world scene.',
                    'Specialized': 'This refers to a set of detectors trained for very specific types of CGI or manipulation, such as spotting a particular rendering engine or a known deepfake technique.',
                    'Deepfake': 'This detector specifically looks for the known artifacts and inconsistencies produced by deepfake-generation models (e.g., GANs), such as unnatural facial expressions or blending artifacts.',
                    'Reflection': 'Reflection analysis checks if reflections in the image (e.g., in eyes or on shiny surfaces) are consistent with the rest of the scene. Inconsistent reflections are a hallmark of CGI.',
                    'Double Quantization': 'This technique detects the traces left when a JPEG image is re-saved, which often happens during manipulation. A high score indicates a higher probability of multiple compression cycles.'
                  };
                  
                  const tooltipText = featureExplanations[metric.feature] || `Normal range: ${min.toFixed(2)} - ${max.toFixed(2)}. Scores outside this range may suggest CGI or manipulation.`;
                  const scoreOutOfRange = metric.score < min || metric.score > max;
                  return (
                    <tr key={metric.feature} className="hover:bg-gray-50 transition-colors duration-150">
                      <td className="py-3 px-4 text-sm text-gray-800">
                        <a href={metric.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline font-medium">
                          {metric.feature}
                        </a>
                        <div className="relative inline-block ml-2 group">
                          <span className="inline-flex items-center justify-center w-5 h-5 rounded-full bg-blue-500 text-white text-xs font-bold cursor-pointer transition-colors duration-200">?</span>
                          <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-64 p-3 text-sm text-white bg-gray-800 rounded-lg shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300 z-20">
                            {tooltipText}
                          </span>
                        </div>
                      </td>
                      <td className={`py-3 px-4 text-sm font-medium ${scoreOutOfRange ? 'text-red-600' : 'text-green-700'}`}>{metric.score.toFixed(2)}</td>
                      <td className="py-3 px-4 text-sm text-gray-700">{metric.insight}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          <h4 className="text-xl font-bold text-gray-800 mt-8 mb-4">Visual Score Representation</h4>
          <div className="space-y-6">
            {result.analysis_breakdown.map((metric) => {
              const [min, max] = metric.normal_range;
              const isNormalized = metric.score >= 0 && metric.score <= 1 && min >= 0 && max <= 1;
              const rangeWidth = (max - min) * 100;
              const rangeLeft = min * 100;
              const scoreLeft = metric.score * 100;

              return (
                <div key={`visual-${metric.feature}`} className="bg-gray-50 p-4 rounded-lg shadow-sm border border-gray-100">
                  <p className="font-semibold text-gray-700 mb-2">{metric.feature} <span className="text-sm text-gray-500">({metric.score.toFixed(2)})</span></p>
                  <div className="h-6 w-full bg-gray-200 rounded-full relative overflow-hidden">
                    <div
                      className="absolute h-full bg-green-400 opacity-75 rounded-full"
                      style={{ left: `${rangeLeft}%`, width: `${rangeWidth}%` }}
                    ></div>
                    <div
                      className="absolute h-full w-1.5 bg-red-600 rounded-full shadow-md"
                      style={{ left: `${scoreLeft}%` }}
                    ></div>
                    {scoreLeft < rangeLeft && (
                      <span className="absolute left-1/2 -translate-x-1/2 top-1/2 -translate-y-1/2 text-xs font-bold text-red-800">Out of Range</span>
                    )}
                     {scoreLeft > (rangeLeft + rangeWidth) && (
                      <span className="absolute left-1/2 -translate-x-1/2 top-1/2 -translate-y-1/2 text-xs font-bold text-red-800">Out of Range</span>
                    )}
                  </div>
                  <p className="mt-2 text-xs text-gray-600">
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