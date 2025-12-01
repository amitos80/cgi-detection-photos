import React, { useCallback, useState } from 'react';

interface ImageUploadProps {
  onFileSelect: (file: File) => void;
}

/**
 * @deprecated Please use `ImageUploadV2` instead. This component is being refactored.
 * @param {ImageUploadProps} props - The props for the ImageUpload component.
 * @returns {JSX.Element} The ImageUpload component.
 */
const ImageUpload: React.FC<ImageUploadProps> = ({ onFileSelect }) => {
  const [isDragOver, setIsDragOver] = useState(false);

  const handleDragOver = useCallback((event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragOver(false);
    const files = event.dataTransfer.files;
    if (files.length > 0) {
      onFileSelect(files[0]);
    }
  }, [onFileSelect]);

  const handleFileInputChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      onFileSelect(files[0]);
    }
  }, [onFileSelect]);

  return (
    <div
      id="drop-zone"
      className={`flex flex-col items-center justify-center h-48 border-2 border-dashed rounded-xl mb-6 transition-all duration-300 ease-in-out cursor-pointer
        ${isDragOver ? 'border-primary-dark bg-primary-light text-primary-dark shadow-lg' : 'border-gray-300 bg-light hover:border-primary-light'}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={() => document.getElementById('file-input')?.click()}
    >
      <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 0115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
      </svg>
      <p className="text-lg text-dark mt-2">Drag & drop an image here</p>
      <p className="text-sm text-gray-500 mt-1">or click to <span className="text-primary font-medium">browse</span></p>
      <input
        id="file-input"
        type="file"
        accept="image/*"
        className="hidden"
        onChange={handleFileInputChange}
      />
    </div>
  );
};

export default ImageUpload;
