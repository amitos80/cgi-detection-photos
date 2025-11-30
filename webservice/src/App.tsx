import ImageUpload from './components/ImageUpload';
import ImagePreview from './components/ImagePreview';
import ProgressBar from './components/ProgressBar';
import AnalysisResults from './components/AnalysisResults';
import ReportForm from './components/ReportForm';
import { useCgiDetection } from './hooks/useCgiDetection';

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
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      <div className="bg-white p-8 rounded-lg shadow-md max-w-2xl">
        <h1 className="text-3xl font-bold text-blue-700 mb-8 text-center">CGI Detection</h1>        {!imagePreviewUrl ? (
          <ImageUpload onFileSelect={handleFileSelect} />
        ) : (
          <>
            <ImagePreview imageUrl={imagePreviewUrl} onClear={handleClearImage} />
            <button
              onClick={handleAnalyze}
              disabled={analyzeMutation.isPending}
              className="w-full px-4 py-2 bg-blue-600 text-white font-semibold rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 disabled:opacity-50 disabled:cursor-not-allowed"
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

        {reportMutation.isError && <p className="text-red-500 mt-2">Error reporting result: {reportMutation.error?.message}</p>}

      </div>
    </div>
  );
}

export default App;
