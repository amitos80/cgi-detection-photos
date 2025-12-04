import { useState, useCallback } from 'react';
import { useMutation } from '@tanstack/react-query';
import { analyzeImage, reportIncorrectResult, type PredictionResult, type AnalysisResponse, type ReportResponse } from '../api';

declare global {
  interface Window {
    progressInterval?: NodeJS.Timeout;
  }
}

const analysisSteps = [
  "Initializing Analysis...",
  "Running Error Level Analysis (ELA)",
  "Analyzing Color Filter Array (CFA)",
  "Calculating Wavelet Statistics (HOS)",
  "Scanning for JPEG Ghost Artifacts",
  "Executing RAMBiNo Statistical Analysis",
  "Checking 3D Geometric Consistency",
  "Verifying Scene Lighting Consistency",
  "Applying Specialized CGI/AIGC Detectors",
  "Finalizing Report..."
];

interface UseCgiDetection {
  selectedFiles: File[];
  imagePreviewUrls: string[];
  analysisResults: PredictionResult[];
  analysisFilenames: string[];
  progressBarVisible: boolean;
  progressText: string;
  currentProgress: number;
  reportStatus: string;
  analyzeMutation: ReturnType<typeof useMutation<AnalysisResponse[], Error, File[]>>;
  reportMutation: ReturnType<typeof useMutation<ReportResponse, Error, { file: File; userCorrection: 'false_cgi' | 'false_real'; originalPrediction: PredictionResult }>>;
  handleFileSelect: (files: File[]) => void;
  handleClearImage: () => void;
  handleAnalyze: () => void;
  // handleReportSubmit: (correctionType: 'false_cgi' | 'false_real') => void; // Temporarily disable reporting for multiple files
}

export function useCgiDetection(): UseCgiDetection {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [imagePreviewUrls, setImagePreviewUrls] = useState<string[]>([]);
  const [analysisResults, setAnalysisResults] = useState<PredictionResult[]>([]);
  const [analysisFilenames, setAnalysisFilenames] = useState<string[]>([]);
  const [progressBarVisible, setProgressBarVisible] = useState(false);
  const [progressText, setProgressText] = useState("");
  const [currentProgress, setCurrentProgress] = useState(0);
  const [reportStatus, setReportStatus] = useState("");

  const startProgressSimulator = () => {
    let step = 0;
    const interval = setInterval(() => {
      step++;
      const progressPercentage = Math.min(95, (step / analysisSteps.length) * 100); // Don't go to 100%
      setCurrentProgress(progressPercentage);
      if (step < analysisSteps.length) {
        setProgressText(`Step ${step}/${analysisSteps.length - 1}: ${analysisSteps[step]}`);
      } else {
        setProgressText("Waiting for final server response...");
      }
      if (analyzeMutation.isSuccess || analyzeMutation.isError) {
        clearInterval(interval);
      }
    }, 1000); // Update every 1 second

    // Store interval ID to clear it later
    window.progressInterval = interval;
  };

  const stopProgressSimulator = () => {
    clearInterval(window.progressInterval);
    setCurrentProgress(100);
    setProgressText("Analysis Complete!");
    setTimeout(() => {
      setProgressBarVisible(false);
    }, 1000);
  };

  const analyzeMutation = useMutation<AnalysisResponse[], Error, File[]>({
    mutationFn: analyzeImage,
    onMutate: () => {
      setProgressBarVisible(true);
      setProgressText(analysisSteps[0]);
      setCurrentProgress(0);
      setAnalysisResults([]);
      setAnalysisFilenames([]);
      setReportStatus("");
      startProgressSimulator();
    },
    onSuccess: (data: AnalysisResponse[] | AnalysisResponse) => {
      stopProgressSimulator();
      const results: PredictionResult[] = [];
      const filenames: string[] = [];
      const dataArray = Array.isArray(data) ? data : [data]; // Ensure data is an array

      dataArray.forEach((item, index) => {
        const { prediction: predictionDetails } = item;
        results.push({
          prediction: predictionDetails?.prediction,
          confidence: predictionDetails?.confidence,
          analysis_duration: predictionDetails?.analysis_duration,
          analysis_breakdown: predictionDetails?.analysis_breakdown,
          rambino_raw_score: predictionDetails?.rambino_raw_score,
          rambino_features: predictionDetails?.rambino_features,
          imagePreviewUrl: imagePreviewUrls[index], // Associate image preview URL
        });
        filenames.push(item.filename ?? 'Unknown');
      });
      setAnalysisResults(results);
      setAnalysisFilenames(filenames);
    },
    onError: (error) => {
      stopProgressSimulator();
      setAnalysisResults([]);
      setAnalysisFilenames([]);
      setReportStatus(`Error: ${error.message}`);
      console.error('Error during analysis:', error);
    },
  });

  const reportMutation = useMutation<ReportResponse, Error, { file: File; userCorrection: 'false_cgi' | 'false_real'; originalPrediction: PredictionResult }>({
    mutationFn: reportIncorrectResult,
    onMutate: () => {
      setReportStatus("Submitting report...");
    },
    onSuccess: (data) => {
      setReportStatus("Thank you for your feedback!");
      console.log('Report submitted:', data);
    },
    onError: (error) => {
      setReportStatus(`Error: ${error.message}`);
      console.error('Error submitting report:', error);
    },
  });

  const handleFileSelect = useCallback((files: File[]) => {
    setSelectedFiles(files);
    const urls: string[] = [];
    files.forEach(file => {
      const reader = new FileReader();
      reader.onload = (e) => {
        urls.push(e.target?.result as string);
        if (urls.length === files.length) {
          setImagePreviewUrls(urls);
        }
      };
      reader.readAsDataURL(file);
    });
    // Clear previous results
    setAnalysisResults([]);
    setAnalysisFilenames([]);
    setReportStatus("");
  }, []);

  const handleClearImage = useCallback(() => {
    console.log('Clearing images and analysis results.');
    setSelectedFiles([]);
    setImagePreviewUrls([]);
    setAnalysisResults([]);
    setAnalysisFilenames([]);
    setProgressBarVisible(false);
    setCurrentProgress(0);
    setProgressText("");
    setReportStatus("");
    if (window.progressInterval) {
      clearInterval(window.progressInterval);
      console.log('Progress simulator cleared.');
    }
  }, []);

  const handleAnalyze = useCallback(() => {
    if (selectedFiles.length > 0) {
      analyzeMutation.mutate(selectedFiles);
    }
  }, [selectedFiles, analyzeMutation]);

  // const handleReportSubmit = useCallback((correctionType: 'false_cgi' | 'false_real') => {
  //   if (selectedFile && analysisResult) {
  //     reportMutation.mutate({ file: selectedFile, userCorrection: correctionType, originalPrediction: analysisResult });
  //   } else {
  //     setReportStatus("Error: No analysis result or file to report.");
  //   }
  // }, [selectedFile, analysisResult, reportMutation]);

  return {
    selectedFiles,
    imagePreviewUrls,
    analysisResults,
    analysisFilenames,
    progressBarVisible,
    progressText,
    currentProgress,
    reportStatus,
    analyzeMutation,
    reportMutation,
    handleFileSelect,
    handleClearImage,
    handleAnalyze,
    // handleReportSubmit,
  };
}