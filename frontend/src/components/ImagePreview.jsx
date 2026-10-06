export default function ImagePreview({ imageUrl, fileName, onAnalyze, onRemove, isLoading, t }) {
  return (
    <div className="preview-panel">
      <div className="preview-header">{t.preview}</div>
      <div className="preview-box">
        <img src={imageUrl} alt={fileName || 'Preview'} />
      </div>
      <div className="preview-meta">{fileName || 'uploaded image'}</div>
      <div className="action-row">
        <button className="primary-button" onClick={onAnalyze} disabled={isLoading}>
          {isLoading ? t.analyzing : t.analyze}
        </button>
        <button className="secondary-button" onClick={onRemove}>
          {t.remove}
        </button>
      </div>
    </div>
  );
}
