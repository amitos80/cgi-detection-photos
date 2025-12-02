import React, { useState } from 'react';

interface ReportFormProps {
  onReportSubmit: (correctionType: 'false_cgi' | 'false_real') => void;
  reportStatus: string;
}

/**
 * A form component for users to report incorrect analysis results.
 * Allows selecting whether an image was falsely identified as CGI or Real.
 * @param {ReportFormProps} props - The props for the ReportForm component.
 * @returns {JSX.Element} The ReportForm component.
 */
const ReportForm: React.FC<ReportFormProps> = ({ onReportSubmit, reportStatus }) => {

  const [correctionType, setCorrectionType] = useState<'false_cgi' | 'false_real' | ''>('');

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
		if (correctionType === '') return;
    onReportSubmit(correctionType);
  };

  return (
    <div className="mt-8 p-6 bg-light rounded-xl shadow-lg border border-gray-200 dark:bg-dark-800 dark:border-dark-700">
      <h3 className="text-xl font-bold text-dark mb-4 dark:text-light">Report Incorrect Detection</h3>
	    <form onSubmit={handleSubmit} className="space-y-4">
		    <label htmlFor="correctionType" className="block text-dark text-base font-medium dark:text-light">This image was incorrectly identified. It is actually:</label>
		    <select
			    name="correctionType"
			    id="correctionType"
			    value={correctionType}
			    onChange={(e) => {
						console.log('onChange ', e.target.value, e.target.value as 'false_cgi' | 'false_real')
				    setCorrectionType(e.target.value as 'false_cgi' | 'false_real')
			    }}
			    required
			    className="mt-1 block w-full p-2.5 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary-dark sm:text-sm dark:bg-dark-700 dark:border-dark-600 dark:text-light"
		    >
			    <option value="false_cgi">A real photo (falsely marked as CGI)</option>
			    <option value="false_real">A CGI image (falsely marked as Real)</option>
		    </select>
		    <button
			    disabled={correctionType === ''}
			    type="submit"
			    className={`w-full px-5 py-2.5 bg-accent-success text-white font-semibold rounded-md bg-blue-600 
			    focus:outline-none focus:ring-2 focus:ring-accent-success 
			    focus:ring-opacity-50 transition-colors duration-200` }
		    >
			    Submit
		    </button>
	    </form>
      {reportStatus && <p className="mt-4 text-center text-sm font-medium text-dark-600 dark:text-light-500">{reportStatus}</p>}
    </div>
  );
};

export default ReportForm;
