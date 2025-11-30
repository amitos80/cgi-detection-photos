import React from 'react';

interface ImagePreviewProps {
  imageUrl: string;
  onClear: () => void;
}

const ImagePreview: React.FC<ImagePreviewProps> = ({ imageUrl, onClear }) => {
  return (
    <div className="relative w-full h-64 mb-6 rounded-xl overflow-hidden shadow-lg border border-gray-200 flex items-center justify-center bg-gray-100">
      <img src={imageUrl} alt="Image Preview" className="max-h-full max-w-full object-contain" />
      <button
        onClick={onClear}
        className="absolute top-3 right-3 bg-red-500 text-white rounded-full w-8 h-8 flex items-center justify-center text-xl font-semibold opacity-80 hover:opacity-100 transition-opacity duration-200 focus:outline-none focus:ring-2 focus:ring-red-400"
        aria-label="Clear image"
      >
        &times;
      </button>
    </div>
  );
};

export default ImagePreview;
