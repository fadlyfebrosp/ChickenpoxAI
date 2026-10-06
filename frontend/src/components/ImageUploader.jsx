import { useRef, useState } from 'react';

export default function ImageUploader({ onFileSelected, disabled, t }) {
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
      onClick={() => !disabled && inputRef.current?.click()}
      role="button"
      tabIndex={0}
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
        onChange={(event) => handleFiles(event.target.files)}
      />
      <div className="upload-content">
        <div className="upload-icon">⬆</div>
        <h3>{t.upload}</h3>
        <p>{t.dragDrop}</p>
        <p className="subtle">{t.browse}</p>
        <span className="file-types">{t.fileTypes}</span>
      </div>
    </div>
  );
}
