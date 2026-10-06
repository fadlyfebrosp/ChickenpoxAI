export default function Disclaimer({ t }) {
  return (
    <div className="disclaimer-box">
      <strong>{t.disclaimerTitle}</strong> {t.disclaimer}
    </div>
  );
}
