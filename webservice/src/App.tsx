import ImageUpload from './components/ImageUpload';
import ImagePreview from './components/ImagePreview';
import ProgressBar from './components/ProgressBar';
import AnalysisResults from './components/AnalysisResults';
import ReportForm from './components/ReportForm';
import { useCgiDetection } from './hooks/useCgiDetection';

/**
 * The main application component that orchestrates the CGI detection process.
 * It handles file selection, image preview, analysis, result display, and reporting.
 * @returns {JSX.Element} The main App component.
 */
function App() {
  const {
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
  } = useCgiDetection();

  return (
    <div className="min-h-screen bg-light dark:bg-dark flex items-center justify-center p-4">
      <div className="bg-white dark:bg-dark-800 p-8 rounded-xl shadow-lg max-w-2xl w-full">
        <h1 className="text-3xl font-bold text-primary-dark mb-8 text-center">CGI Detection</h1>
        {!imagePreviewUrl ? (
          <ImageUpload onFileSelect={handleFileSelect} />
        ) : (
          <>
            <ImagePreview imageUrl={imagePreviewUrl} onClear={handleClearImage} />
            <button
              onClick={handleAnalyze}
              disabled={analyzeMutation.isPending}
              className="w-full px-4 py-2 font-semibold rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:ring-opacity-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
              style={{ backgroundColor: 'var(--primary-DEFAULT)', color: 'white' }}
            >
              {analyzeMutation.isPending ? 'Analyzing...' : 'Analyze Image'}
            </button>
          </>
        )}

        <ProgressBar isVisible={progressBarVisible} progress={currentProgress} text={progressText} />

        {analysisResult && (
          <AnalysisResults filename={analysisFilename || 'Unknown File'} result={analysisResult} />
        )}

        {analysisResult && selectedFile && (
          <ReportForm onReportSubmit={handleReportSubmit} reportStatus={reportStatus} />
        )}

        {reportMutation.isError && <p className="text-accent-danger mt-2">Error reporting result: {reportMutation.error?.message}</p>}

      </div>
    </div>
  );
}

export default App;
