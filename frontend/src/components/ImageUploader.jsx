import { useRef, useState } from 'react';

export default function ImageUploader({ onFileSelected, onCameraClick, disabled, t }) {
  const inputRef = useRef(null);
  const [isDragOver, setIsDragOver] = useState(false);

  const handleFiles = (fileList) => {
    if (!fileList || fileList.length === 0) return;
    onFileSelected(fileList[0]);
  };

  return (
    <div
      className={`upload-box ${isDragOver ? 'drag-over' : ''}`}
      onDragOver={(event) => {
        event.preventDefault();
        if (!disabled) setIsDragOver(true);
      }}
      onDragLeave={() => setIsDragOver(false)}
      onDrop={(event) => {
        event.preventDefault();
        setIsDragOver(false);
        if (!disabled) handleFiles(event.dataTransfer.files);
      }}
      role="group"
      aria-label={t.selectImage}
    >
      <div className="source-options">
        <label
          className={`source-option ${disabled ? 'source-option-disabled' : ''}`}
          role="button"
          tabIndex={disabled ? -1 : 0}
          onKeyDown={(event) => {
            if (event.key === 'Enter' || event.key === ' ') {
              event.preventDefault();
              inputRef.current?.click();
            }
          }}
        >
          <input
            ref={inputRef}
            type="file"
            accept=".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp"
            hidden
            disabled={disabled}
            onChange={(event) => {
              handleFiles(event.target.files);
              event.target.value = '';
            }}
          />
          <span className="upload-icon" aria-hidden="true">↑</span>
          <strong>{t.upload}</strong>
          <span>{t.dragDrop}</span>
          <span className="subtle">{t.browse}</span>
          <span className="file-types">{t.fileTypes}</span>
        </label>
        <button
          className="source-option"
          type="button"
          onClick={onCameraClick}
          disabled={disabled}
        >
          <span className="upload-icon camera-icon" aria-hidden="true">◎</span>
          <strong>{t.takePhoto}</strong>
          <span>{t.cameraDescription}</span>
          <span className="subtle">{t.cameraHint}</span>
        </button>
      </div>
    </div>
  );
}
