import React, { useState } from 'react';

interface ReportFormProps {
  onReportSubmit: (correctionType: 'false_cgi' | 'false_real') => void;
  reportStatus: string;
}

const ReportForm: React.FC<ReportFormProps> = ({ onReportSubmit, reportStatus }) => {
  const [showForm, setShowForm] = useState(false);
  const [correctionType, setCorrectionType] = useState<'false_cgi' | 'false_real'>('false_cgi');

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    onReportSubmit(correctionType);
  };

  return (
    <div className="mt-8 p-6 bg-white rounded-xl shadow-lg border border-gray-100">
      <h3 className="text-xl font-bold text-gray-800 mb-4">Feedback & Reporting</h3>
      {!showForm ? (
        <button
          onClick={() => setShowForm(true)}
          className="w-full px-5 py-2.5 bg-indigo-600 text-white font-semibold rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-opacity-50 transition-colors duration-200"
        >
          Report Incorrect Result
        </button>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          <label htmlFor="correctionType" className="block text-gray-700 text-base font-medium">This image was incorrectly identified. It is actually:</label>
          <select
            name="correctionType"
            id="correctionType"
            value={correctionType}
            onChange={(e) => setCorrectionType(e.target.value as 'false_cgi' | 'false_real')}
            required
            className="mt-1 block w-full p-2.5 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
          >
            <option value="false_cgi">A real photo (falsely marked as CGI)</option>
            <option value="false_real">A CGI image (falsely marked as Real)</option>
          </select>
          <button
            type="submit"
            className="w-full px-5 py-2.5 bg-green-600 text-white font-semibold rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-opacity-50 transition-colors duration-200"
          >
            Submit Report
          </button>
        </form>
      )}
      {reportStatus && <p className="mt-4 text-center text-sm font-medium text-gray-600">{reportStatus}</p>}
    </div>
  );
};

export default ReportForm;
