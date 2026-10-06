export default function ImagePreview({
  imageUrl,
  fileName,
  onAnalyze,
  onRemove,
  isLoading,
  canAnalyze,
  storageConsent,
  onStorageConsentChange,
  storedImageUrl,
  t,
}) {
  return (
    <div className="preview-panel">
      <div className="preview-header">{t.preview}</div>
      <div className="preview-box">
        <img src={imageUrl} alt={fileName || 'Preview'} />
      </div>
      <div className="preview-meta">{fileName || 'uploaded image'}</div>
      <label className="storage-consent">
        <input
          type="checkbox"
          checked={storageConsent}
          onChange={(event) => onStorageConsentChange(event.target.checked)}
          disabled={isLoading || Boolean(storedImageUrl)}
        />
        <span>{t.storageConsent}</span>
      </label>
      {storedImageUrl && (
        <p className="stored-image-link">
          {t.storageUrlLabel}{' '}
          <a href={storedImageUrl} target="_blank" rel="noreferrer">{storedImageUrl}</a>
        </p>
      )}
      <div className="action-row">
        <button className="primary-button" onClick={onAnalyze} disabled={isLoading || !canAnalyze}>
          {isLoading ? t.analyzing : storedImageUrl ? t.retryAnalysis : t.analyze}
        </button>
        <button className="secondary-button" onClick={onRemove}>
          {t.remove}
        </button>
      </div>
    </div>
  );
}
