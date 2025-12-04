export interface Metric {
  feature: string;
  score: number;
  insight: string;
  normal_range: [number, number];
  url: string;
}

// This interface represents the frontend state for prediction results.
// It's kept separate in case the API returns more data than what's directly needed for the state.
export interface PredictionResult {
  prediction: 'cgi' | 'real' | undefined | null;
  confidence: number | undefined | null;
  analysis_duration?: number;
  analysis_breakdown?: Metric[];
  rambino_raw_score?: number;
  rambino_features?: unknown[];
}

// This interface represents the actual flat structure returned by the backend API.
export interface AnalysisResponse {
  filename: string | undefined | null;
  prediction: {
    prediction: 'cgi' | 'real';
    confidence: number;
    analysis_duration?: number;
    analysis_breakdown?: Metric[];
    rambino_raw_score?: number;
    rambino_features?: unknown[];
    // Add any other properties the backend might send within this nested object
  };
}

export interface ReportResponse {
  message: string;
  feedback: unknown; // Adjust this type based on actual feedback structure
}

export const analyzeImage = async (files: File[]): Promise<AnalysisResponse[]> => {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append('files', file);
  });

  const response = await fetch('/analyze', {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.indexOf('application/json') !== -1) {
      const errorData = await response.json();
      throw new Error(errorData.details || 'Unknown error from server');
    } else {
      throw new Error(response.statusText);
    }
  }

  // The response.json() will be of type AnalysisResponse based on our updated interface.
  return response.json();
};

interface ReportPayload {
  file: File;
  userCorrection: 'false_cgi' | 'false_real';
  originalPrediction: PredictionResult;
}

export const reportIncorrectResult = async (payload: ReportPayload): Promise<ReportResponse> => {
  const formData = new FormData();
  formData.append('file', payload.file);
  formData.append('userCorrection', payload.userCorrection);
  formData.append('originalPrediction', JSON.stringify(payload.originalPrediction));

  const response = await fetch('/report', {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.details || 'Failed to submit report');
  }

  return response.json();
};