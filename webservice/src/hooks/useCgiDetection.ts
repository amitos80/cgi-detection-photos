import { useState, useCallback } from 'react';
import { useMutation } from '@tanstack/react-query';
import { analyzeImage, reportIncorrectResult, type PredictionResult, type AnalysisResponse, type ReportResponse } from '../api';

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
  selectedFile: File | null;
  imagePreviewUrl: string | null;
  analysisResult: PredictionResult | null;
  analysisFilename: string | null;
  progressBarVisible: boolean;
  progressText: string;
  currentProgress: number;
  reportStatus: string;
  analyzeMutation: ReturnType<typeof useMutation<AnalysisResponse, Error, File>>;
  reportMutation: ReturnType<typeof useMutation<ReportResponse, Error, { file: File; userCorrection: 'false_cgi' | 'false_real'; originalPrediction: PredictionResult }>>;
  handleFileSelect: (file: File) => void;
  handleClearImage: () => void;
  handleAnalyze: () => void;
  handleReportSubmit: (correctionType: 'false_cgi' | 'false_real') => void;
}

export function useCgiDetection(): UseCgiDetection {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [imagePreviewUrl, setImagePreviewUrl] = useState<string | null>(null);
  const [analysisResult, setAnalysisResult] = useState<PredictionResult | null>(null);
  const [analysisFilename, setAnalysisFilename] = useState<string | null>(null);
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
    (window as any).progressInterval = interval;
  };

  const stopProgressSimulator = () => {
    clearInterval((window as any).progressInterval);
    setCurrentProgress(100);
    setProgressText("Analysis Complete!");
    setTimeout(() => {
      setProgressBarVisible(false);
    }, 1000);
  };

  const analyzeMutation = useMutation<AnalysisResponse, Error, File>({
    mutationFn: analyzeImage,
    onMutate: () => {
      setProgressBarVisible(true);
      setProgressText(analysisSteps[0]);
      setCurrentProgress(0);
      setAnalysisResult(null);
      setAnalysisFilename(null);
      setReportStatus("");
      startProgressSimulator();
    },
          onSuccess: (data: AnalysisResponse) => { // Explicitly type data as AnalysisResponse
            console.log('Analysis successful, received data:', data);
            console.log('data.prediction:', data?.prediction);
            console.log('data.filename:', data?.filename);

            // Construct the PredictionResult object from the flattened data
            const predictionResult: PredictionResult = {
              prediction: data?.prediction,
              confidence: data?.confidence,
              analysis_duration: data?.analysis_duration,
              analysis_breakdown: data?.analysis_breakdown,
              // Include other fields from API if they exist and are relevant for PredictionResult state
              rambino_raw_score: data?.rambino_raw_score,
              rambino_features: data?.rambino_features,
            };

            stopProgressSimulator();
            setAnalysisResult(predictionResult); // Set the correctly structured result
            setAnalysisFilename(data?.filename ?? null);
          },    onError: (error) => {
      stopProgressSimulator();
      setAnalysisResult(null); // Clear previous results
      setAnalysisFilename(null);
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

  const handleFileSelect = useCallback((file: File) => {
    setSelectedFile(file);
    const reader = new FileReader();
    reader.onload = (e) => {
      setImagePreviewUrl(e.target?.result as string);
    };
    reader.readAsDataURL(file);
    // Clear previous results
    setAnalysisResult(null);
    setAnalysisFilename(null);
    setReportStatus("");
  }, []);

  const handleClearImage = useCallback(() => {
    console.log('Clearing image and analysis results.');
    setSelectedFile(null);
    setImagePreviewUrl(null);
    setAnalysisResult(null);
    setAnalysisFilename(null);
    setProgressBarVisible(false);
    setCurrentProgress(0);
    setProgressText("");
    setReportStatus("");
    if ((window as any).progressInterval) {
      clearInterval((window as any).progressInterval);
      console.log('Progress simulator cleared.');
    }
  }, []);

  const handleAnalyze = useCallback(() => {
    if (selectedFile) {
      analyzeMutation.mutate(selectedFile);
    }
  }, [selectedFile, analyzeMutation]);

  const handleReportSubmit = useCallback((correctionType: 'false_cgi' | 'false_real') => {
    if (selectedFile && analysisResult) {
      reportMutation.mutate({ file: selectedFile, userCorrection: correctionType, originalPrediction: analysisResult });
    } else {
      setReportStatus("Error: No analysis result or file to report.");
    }
  }, [selectedFile, analysisResult, reportMutation]);

  return {
    selectedFile,
    imagePreviewUrl,
    analysisResult,
    analysisFilename,
    progressBarVisible,
    progressText,
    currentProgress,
    reportStatus,
    analyzeMutation,
    reportMutation,
    handleFileSelect,
    handleClearImage,
    handleAnalyze,
    handleReportSubmit,
  };
}