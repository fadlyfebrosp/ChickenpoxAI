import { useEffect, useRef, useState } from 'react';

export default function CameraCapture({ onCapture, onClose, t }) {
  const videoRef = useRef(null);
  const [error, setError] = useState('');
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    let cancelled = false;
    let stream;

    async function startCamera() {
      if (!navigator.mediaDevices?.getUserMedia) {
        setError(t.cameraUnavailable);
        return;
      }

      try {
        stream = await navigator.mediaDevices.getUserMedia({
          audio: false,
          video: { facingMode: { ideal: 'environment' } },
        });
        if (cancelled) {
          stream.getTracks().forEach((track) => track.stop());
          return;
        }
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
        setIsReady(true);
      } catch {
        setError(t.cameraPermissionError);
      }
    }

    startCamera();
    return () => {
      cancelled = true;
      stream?.getTracks().forEach((track) => track.stop());
    };
  }, [t.cameraPermissionError, t.cameraUnavailable]);

  const capturePhoto = () => {
    const video = videoRef.current;
    if (!video?.videoWidth || !video.videoHeight) {
      setError(t.cameraCaptureError);
      return;
    }

    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
    canvas.toBlob((blob) => {
      if (!blob) {
        setError(t.cameraCaptureError);
        return;
      }
      onCapture(new File([blob], `camera-${Date.now()}.jpg`, { type: 'image/jpeg' }));
    }, 'image/jpeg', 0.92);
  };

  return (
    <div className="camera-backdrop" role="presentation" onMouseDown={(event) => {
      if (event.target === event.currentTarget) onClose();
    }}>
      <section
        className="camera-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="camera-title"
      >
        <div className="camera-dialog-header">
          <h3 id="camera-title">{t.cameraTitle}</h3>
          <button className="camera-close" type="button" onClick={onClose} aria-label={t.close}>
            ×
          </button>
        </div>
        {error ? (
          <p className="camera-error" role="alert">{error}</p>
        ) : (
          <div className="camera-video-wrap">
            <video ref={videoRef} autoPlay playsInline muted />
            {!isReady && <p className="camera-loading">{t.cameraStarting}</p>}
          </div>
        )}
        <div className="camera-actions">
          <button className="secondary-button" type="button" onClick={onClose}>
            {t.cancel}
          </button>
          <button className="primary-button" type="button" onClick={capturePhoto} disabled={!isReady}>
            {t.capturePhoto}
          </button>
        </div>
      </section>
    </div>
  );
}
