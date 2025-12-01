import React from 'react';

interface ImagePreviewProps {
  imageUrl: string;
  onClear: () => void;
}

/**
 * Displays a preview of the selected image with a clear button.
 * @param {ImagePreviewProps} props - The props for the ImagePreview component.
 * @returns {JSX.Element} The ImagePreview component.
 */
const ImagePreview: React.FC<ImagePreviewProps> = ({ imageUrl, onClear }) => {
  return (
    <div className="relative w-full h-64 mb-6 rounded-xl overflow-hidden shadow-md border border-light flex items-center justify-center bg-gray-50 dark:bg-dark-700">
      <img src={imageUrl} alt="Image Preview" className="max-h-full max-w-full object-contain" />
      <button
        onClick={onClear}
        className="absolute top-3 right-3 bg-accent-danger text-white rounded-full w-8 h-8 flex items-center justify-center text-xl font-semibold opacity-90 hover:opacity-100 transition-opacity duration-200 focus:outline-none focus:ring-2 focus:ring-accent-danger"
        aria-label="Clear image"
      >
        &times;
      </button>
    </div>
  );
};

export default ImagePreview;
