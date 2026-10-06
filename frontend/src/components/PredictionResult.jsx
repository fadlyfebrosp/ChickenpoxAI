export default function PredictionResult({ result, t }) {
  if (!result) return null;

  const isChickenpox = result.prediction === 'Chickenpox';

  return (
    <div className="result-card">
      <div className="result-title">{t.result}</div>
      <div className="confidence-value">{t.guessPrefix}</div>
      <div className="prediction-name">
        {isChickenpox ? t.chickenpox : t.healthy}
      </div>
      <div className="observation-block">
        <strong>{t.observation}</strong>
        <p>{result.visual_observation}</p>
      </div>
      <div className="model-caption">{t.modelLabel}: {result.model}</div>
      <p className="probability-note">{t.limitation}</p>
    </div>
  );
}
