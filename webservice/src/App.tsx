import ImageUpload from './components/ImageUpload';
import ImagePreview from './components/ImagePreview';
import ProgressBar from './components/ProgressBar';
import AnalysisResults from './components/AnalysisResults';
import { useCgiDetection } from './hooks/useCgiDetection';

/**
 * The main application component that orchestrates the CGI detection process.
 * It handles file selection, image preview, analysis, result display, and reporting.
 * @returns {JSX.Element} The main App component.
 */
function App() {
  const {
    selectedFiles, // Add selectedFiles
    imagePreviewUrls,
    analysisResults,
    analysisFilenames,
    progressBarVisible,
    progressText,
    currentProgress,
    reportStatus, // Add reportStatus
    analyzeMutation,
    reportMutation, // Add reportMutation
    handleFileSelect,
    handleClearImage,
    handleAnalyze,
  } = useCgiDetection();

  return (
    <div className="min-h-screen bg-light dark:bg-dark flex items-center justify-center p-4">
      <div className="bg-white dark:bg-dark-800 p-8 rounded-xl shadow-lg max-w-2xl w-full">
        <h1 className="text-3xl font-bold text-primary-dark mb-8 text-center">AI Generated Images Detection</h1>
        {!imagePreviewUrls.length ? (
          <ImageUpload onFileSelect={handleFileSelect} />
        ) : (
          <div className="space-y-4">
            {imagePreviewUrls.map((url, index) => (
              <ImagePreview key={index} imageUrl={url} onClear={handleClearImage} />
            ))}
            <button
              onClick={handleAnalyze}
              disabled={analyzeMutation.isPending}
              className="w-full px-4 py-2 font-semibold rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:ring-opacity-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
              style={{ backgroundColor: 'var(--primary-DEFAULT)', color: 'white' }}
            >
              {analyzeMutation.isPending ? 'Analyzing...' : 'Analyze Images'}
            </button>
          </div>
        )}

        <ProgressBar isVisible={progressBarVisible} progress={currentProgress} text={progressText} />

        {analysisResults.length > 0 && (
          <div className="space-y-4">
            {analysisResults.map((result, index) => (
              <AnalysisResults
                key={index}
                filename={analysisFilenames[index] || 'Unknown File'}
                result={result}
                file={selectedFiles[index]} // Pass the File object
                onReportSubmit={reportMutation.mutate} // Pass the mutate function
                reportStatus={reportStatus} // Pass reportStatus
              />
            ))}
          </div>
        )}

        {/* {analysisResults.length > 0 && selectedFiles.length > 0 && (
          <ReportForm onReportSubmit={handleReportSubmit} reportStatus={reportStatus} />
        )} */}

        {/* {reportMutation.isError && <p className="text-accent-danger mt-2">Error reporting result: {reportMutation.error?.message}</p>} */}

      </div>
    </div>
  );
}

export default App;
