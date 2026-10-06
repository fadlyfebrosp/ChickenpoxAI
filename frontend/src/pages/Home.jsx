import { useState } from 'react';
import Disclaimer from '../components/Disclaimer';
import ImagePreview from '../components/ImagePreview';
import ImageUploader from '../components/ImageUploader';
import PredictionResult from '../components/PredictionResult';
import { analyzeImage } from '../services/api';

const translations = {
  id: {
    language: 'Bahasa',
    navHome: 'Beranda',
    navAbout: 'Tentang',
    navTechnology: 'Teknologi',
    navFeatures: 'Fitur',
    navEvaluation: 'Evaluasi',
    navPredict: 'Prediksi',
    navCta: 'Mulai Screening',
    badge: 'COMPUTER VISION • GENAI LOKAL',
    heroTitleStart: 'Kenali pola gambar kulit dengan',
    heroAccent: 'AI yang lebih informatif',
    heroDescription:
      'Unggah gambar untuk melihat tebakan visual dari model AI. Dirancang untuk pembelajaran dan demonstrasi, bukan diagnosis medis.',
    start: 'Mulai Screening',
    howItWorks: 'Cara Kerja',
    statusTitle: 'Analisis visual berbasis AI',
    statusReady: 'Siap menerima gambar',
    statusDescription: 'Hasil hanya muncul setelah Anda memilih gambar dan memulai analisis.',
    localLabel: 'Pemrosesan lokal',
    localDescription: 'Gambar diproses di perangkat ini melalui Ollama.',
    classesLabel: 'Label demonstrasi',
    classesDescription: 'Healthy Skin dan Chickenpox',
    aboutEyebrow: 'TENTANG CHICKENPOXAI',
    aboutTitle: 'Membantu memahami cara kerja AI pada gambar',
    aboutBody:
      'ChickenpoxAI adalah prototipe edukasi yang menunjukkan bagaimana model vision-language menghasilkan tebakan label dan pengamatan visual singkat. Hasil dapat keliru, terutama untuk gambar buram, pencahayaan buruk, atau kondisi yang tidak dikenal model.',
    aboutNote: 'AI membantu eksplorasi — bukan pengganti pemeriksaan tenaga kesehatan.',
    technologyEyebrow: 'TEKNOLOGI',
    technologyTitle: 'Dari Machine Learning ke Generative AI',
    technologyIntro:
      'Deep Learning merupakan bagian dari Machine Learning. Model vision-language GenAI juga menggunakan Deep Learning; ini bukan tahapan yang otomatis meningkatkan akurasi.',
    mlTitle: 'Machine Learning',
    mlBody: 'Fondasi untuk belajar pola dari contoh data.',
    dlTitle: 'Deep Learning',
    dlBody: 'Bagian dari ML yang menggunakan jaringan saraf berlapis untuk memahami gambar.',
    genTitle: 'Generative AI',
    genBody: 'MedGemma lokal menghasilkan tebakan label dan deskripsi visual dari gambar.',
    featureEyebrow: 'FITUR',
    featureTitle: 'Alur screening yang sederhana dan transparan',
    featureUpload: 'Unggah gambar',
    featureUploadBody: 'Pratinjau gambar sebelum analisis, dengan format umum yang didukung.',
    featureAnalyze: 'Analisis lokal',
    featureAnalyzeBody: 'Gambar dikirim ke model lokal Ollama, bukan layanan AI cloud.',
    featureResult: 'Hasil yang mudah dipahami',
    featureResultBody: 'Tampilkan label tebakan, pengamatan visual, dan batasan hasil.',
    evaluationEyebrow: 'EVALUASI & BATASAN',
    evaluationTitle: 'Tidak mengklaim angka akurasi yang belum diukur',
    evaluationBody:
      'GenAI aktif menghasilkan tebakan kualitatif dan tidak menyediakan confidence terkalibrasi. Karena itu halaman ini tidak menampilkan angka akurasi atau persentase tebakan. Benchmark harus diuji pada dataset independen dengan label yang tervalidasi.',
    evaluationPointOne: 'Model dapat salah mengklasifikasikan gambar.',
    evaluationPointTwo: 'Tampilan kulit serupa dapat berasal dari penyebab berbeda.',
    evaluationPointThree: 'Hasil bukan diagnosis dan bukan saran pengobatan.',
    predictEyebrow: 'MULAI ANALISIS',
    predictTitle: 'Unggah gambar untuk melihat tebakan model',
    predictDescription:
      'Gunakan gambar yang jelas dengan pencahayaan cukup. Hindari menyertakan informasi pribadi yang tidak diperlukan.',
    preview: 'PRATINJAU GAMBAR',
    analyze: 'Analisis Gambar',
    analyzing: 'Sedang menganalisis...',
    remove: 'Hapus Gambar',
    loadingTitle: 'Menganalisis Gambar...',
    loadingMessage: 'Model lokal sedang memproses gambar. Mohon tunggu.',
    result: 'Perkiraan GenAI (bukan diagnosis)',
    guessPrefix: 'Tebakan teratas model:',
    observation: 'Pengamatan visual model',
    modelLabel: 'Model lokal',
    healthy: 'Gambar tersebut tampak normal',
    chickenpox: 'Gambar tersebut terdeteksi ChickenPox',
    another: 'Analisis Gambar Lain',
    apiError: 'Gambar tidak dapat dianalisis. Silakan coba lagi.',
    disclaimerTitle: 'Disclaimer:',
    disclaimer:
      'ChickenpoxAI dikembangkan untuk penelitian dan pembelajaran. Hasil hanya berdasarkan pola visual, bukan diagnosis medis. Kondisi kulit yang berbeda dapat terlihat serupa. Konsultasikan dengan tenaga kesehatan untuk evaluasi klinis.',
    limitation:
      'Ini adalah tebakan model AI untuk demonstrasi, bukan diagnosis atau jaminan akurasi. Tampilan bintik saja tidak dapat memastikan penyebabnya.',
    footer: 'Proyek edukasi computer vision. Bukan alat diagnosis medis.',
  },
  en: {
    language: 'Language',
    navHome: 'Home',
    navAbout: 'About',
    navTechnology: 'Technology',
    navFeatures: 'Features',
    navEvaluation: 'Evaluation',
    navPredict: 'Prediction',
    navCta: 'Start screening',
    badge: 'COMPUTER VISION • LOCAL GENAI',
    heroTitleStart: 'Explore skin-image patterns with',
    heroAccent: 'more informative AI',
    heroDescription:
      'Upload an image to see an AI model’s visual guess. Built for learning and demonstration, not medical diagnosis.',
    start: 'Start screening',
    howItWorks: 'How it works',
    statusTitle: 'AI-powered visual analysis',
    statusReady: 'Ready for an image',
    statusDescription: 'A result appears only after you select an image and start the analysis.',
    localLabel: 'Local processing',
    localDescription: 'Images are processed on this device through Ollama.',
    classesLabel: 'Demo labels',
    classesDescription: 'Healthy Skin and Chickenpox',
    aboutEyebrow: 'ABOUT CHICKENPOXAI',
    aboutTitle: 'Explore how AI works with images',
    aboutBody:
      'ChickenpoxAI is an educational prototype demonstrating how a vision-language model generates a label guess and a short visual observation. Results can be wrong, especially with blurry images, poor lighting, or conditions the model has not learned.',
    aboutNote: 'AI supports exploration — it does not replace professional medical evaluation.',
    technologyEyebrow: 'TECHNOLOGY',
    technologyTitle: 'From Machine Learning to Generative AI',
    technologyIntro:
      'Deep Learning is a subset of Machine Learning. Vision-language GenAI also uses Deep Learning; these are not sequential steps that automatically improve accuracy.',
    mlTitle: 'Machine Learning',
    mlBody: 'The foundation for learning patterns from examples.',
    dlTitle: 'Deep Learning',
    dlBody: 'A part of ML that uses layered neural networks to understand images.',
    genTitle: 'Generative AI',
    genBody: 'Local MedGemma produces a label guess and visual description from an image.',
    featureEyebrow: 'FEATURES',
    featureTitle: 'A simple and transparent screening flow',
    featureUpload: 'Image upload',
    featureUploadBody: 'Preview the image before analysis, using supported common formats.',
    featureAnalyze: 'Local analysis',
    featureAnalyzeBody: 'Images are sent to local Ollama, not a cloud AI service.',
    featureResult: 'Understandable results',
    featureResultBody: 'See the model’s label guess, visual observation, and limitations.',
    evaluationEyebrow: 'EVALUATION & LIMITATIONS',
    evaluationTitle: 'No accuracy claims without measurement',
    evaluationBody:
      'The active GenAI produces qualitative guesses and does not provide calibrated confidence. This page therefore does not show accuracy or guess percentages. A benchmark must be tested on an independent dataset with verified labels.',
    evaluationPointOne: 'The model may misclassify images.',
    evaluationPointTwo: 'Similar-looking skin appearances can have different causes.',
    evaluationPointThree: 'Results are not a diagnosis or treatment advice.',
    predictEyebrow: 'START ANALYSIS',
    predictTitle: 'Upload an image to see the model’s guess',
    predictDescription:
      'Use a clear image with sufficient lighting. Avoid including unnecessary personal information.',
    preview: 'IMAGE PREVIEW',
    analyze: 'Analyze Image',
    analyzing: 'Analyzing...',
    remove: 'Remove Image',
    loadingTitle: 'Analyzing Image...',
    loadingMessage: 'The local model is processing the image. Please wait.',
    result: 'GenAI Estimate (not a diagnosis)',
    guessPrefix: 'Model’s top guess:',
    observation: 'Model visual observation',
    modelLabel: 'Local model',
    healthy: 'The image appears normal',
    chickenpox: 'The image was classified by the model as Chickenpox',
    another: 'Analyze Another Image',
    apiError: 'Unable to analyze this image. Please try again.',
    disclaimerTitle: 'Disclaimer:',
    disclaimer:
      'ChickenpoxAI is developed for research and education. Results are based solely on visual patterns and are not a medical diagnosis. Different skin conditions may look similar. Consult a qualified healthcare professional for clinical evaluation.',
    limitation:
      'This is an AI model guess for demonstration, not a diagnosis or accuracy guarantee. Spots alone cannot confirm their cause.',
    footer: 'An educational computer vision project. Not a medical diagnostic tool.',
  },
};

const navigation = [
  ['home', 'navHome'],
  ['about', 'navAbout'],
  ['technology', 'navTechnology'],
  ['features', 'navFeatures'],
  ['evaluation', 'navEvaluation'],
  ['prediction', 'navPredict'],
];

export default function Home() {
  const [language, setLanguage] = useState('id');
  const [selectedFile, setSelectedFile] = useState(null);
  const [imageUrl, setImageUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const t = translations[language];

  const scrollToPrediction = () => {
    document.getElementById('prediction')?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleFileSelection = (file) => {
    if (!file) return;
    setSelectedFile(file);
    setError('');
    setResult(null);
    if (imageUrl) URL.revokeObjectURL(imageUrl);
    setImageUrl(URL.createObjectURL(file));
  };

  const handleAnalyze = async () => {
    if (!selectedFile) return;
    setIsLoading(true);
    setError('');
    try {
      const response = await analyzeImage(selectedFile, language);
      setResult(response);
    } catch (err) {
      const detail = err?.response?.data?.detail || t.apiError;
      setError(detail);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setResult(null);
    setError('');
    if (imageUrl) URL.revokeObjectURL(imageUrl);
    setImageUrl('');
  };

  return (
    <div className="site-shell">
      <header className="site-header">
        <a className="brand-mark" href="#home" aria-label="ChickenpoxAI home">
          <span className="brand-icon" aria-hidden="true">C</span>
          <span>Chickenpox<span className="brand-accent">AI</span></span>
        </a>
        <nav className="main-nav" aria-label={t.navHome}>
          {navigation.map(([id, label]) => (
            <a href={`#${id}`} key={id}>{t[label]}</a>
          ))}
        </nav>
        <div className="header-actions">
          <div className="language-switch" role="group" aria-label={t.language}>
            <button
              type="button"
              className={language === 'id' ? 'language-button active' : 'language-button'}
              aria-pressed={language === 'id'}
              onClick={() => setLanguage('id')}
            >
              ID
            </button>
            <button
              type="button"
              className={language === 'en' ? 'language-button active' : 'language-button'}
              aria-pressed={language === 'en'}
              onClick={() => setLanguage('en')}
            >
              EN
            </button>
          </div>
          <button className="header-cta" type="button" onClick={scrollToPrediction}>
            {t.navCta}<span aria-hidden="true">↗</span>
          </button>
        </div>
      </header>

      <main>
        <section className="hero-section page-section" id="home">
          <div className="hero-copy">
            <div className="eyebrow-pill"><span />{t.badge}</div>
            <h1>{t.heroTitleStart} <span>{t.heroAccent}</span></h1>
            <p className="hero-description">{t.heroDescription}</p>
            <div className="hero-actions">
              <button className="button-primary" type="button" onClick={scrollToPrediction}>
                {t.start}<span aria-hidden="true">→</span>
              </button>
              <a className="button-secondary" href="#technology">
                <span className="play-icon" aria-hidden="true">▶</span>{t.howItWorks}
              </a>
            </div>
            <div className="hero-assurance">
              <span className="assurance-dot" />
              <span>{t.localLabel}</span>
              <span className="assurance-divider">•</span>
              <span>MedGemma 4B</span>
            </div>
          </div>

          <div className="hero-visual" aria-label={t.statusTitle}>
            <div className="visual-glow" />
            <div className="analysis-card">
              <div className="analysis-card-top">
                <div className="window-dots"><i /><i /><i /></div>
                <span className="local-badge"><span />LOCAL AI</span>
              </div>
              <div className="scan-illustration" aria-hidden="true">
                <div className="scan-orbit orbit-one" />
                <div className="scan-orbit orbit-two" />
                <div className="scan-crosshair crosshair-one" />
                <div className="scan-crosshair crosshair-two" />
                <div className="scan-core"><span>AI</span></div>
                <div className="scan-line" />
                <span className="scan-caption">IMAGE ANALYSIS</span>
              </div>
              <div className="analysis-card-content">
                <div>
                  <span className="status-overline">{t.statusTitle}</span>
                  <strong>{t.statusReady}</strong>
                </div>
                <span className="ready-indicator" aria-hidden="true">✓</span>
              </div>
              <p className="analysis-card-note">{t.statusDescription}</p>
            </div>
            <div className="floating-info floating-info-top">
              <span className="floating-icon">✳</span>
              <span><strong>MedGemma 4B</strong><small>{t.localLabel}</small></span>
            </div>
            <div className="floating-info floating-info-bottom">
              <span className="floating-icon floating-icon-blue">◉</span>
              <span><strong>2 {language === 'id' ? 'label' : 'labels'}</strong><small>{t.classesDescription}</small></span>
            </div>
          </div>
        </section>

        <section className="fact-strip" aria-label={t.classesLabel}>
          <div className="fact-item">
            <span className="fact-icon">⌂</span>
            <div><strong>{t.localLabel}</strong><span>{t.localDescription}</span></div>
          </div>
          <div className="fact-item">
            <span className="fact-icon fact-icon-violet">◈</span>
            <div><strong>{t.classesLabel}</strong><span>{t.classesDescription}</span></div>
          </div>
          <div className="fact-item">
            <span className="fact-icon fact-icon-green">◎</span>
            <div><strong>MedGemma 4B</strong><span>{language === 'id' ? 'Model vision-language' : 'Vision-language model'}</span></div>
          </div>
        </section>

        <section className="content-section about-section page-section" id="about">
          <div className="section-heading">
            <span className="section-eyebrow">{t.aboutEyebrow}</span>
            <h2>{t.aboutTitle}</h2>
            <p>{t.aboutBody}</p>
            <div className="inline-note"><span>✦</span>{t.aboutNote}</div>
          </div>
          <div className="about-side-card">
            <div className="about-card-icon">✧</div>
            <span className="status-overline">{language === 'id' ? 'TUJUAN PROYEK' : 'PROJECT PURPOSE'}</span>
            <strong>{language === 'id' ? 'Belajar dengan transparan' : 'Learn with transparency'}</strong>
            <p>{language === 'id'
              ? 'Tunjukkan tebakan AI apa adanya, termasuk batasan dan kemungkinan salah.'
              : 'Show AI guesses as they are, including limitations and the possibility of error.'}</p>
          </div>
        </section>

        <section className="content-section technology-section page-section" id="technology">
          <div className="center-heading">
            <span className="section-eyebrow">{t.technologyEyebrow}</span>
            <h2>{t.technologyTitle}</h2>
            <p>{t.technologyIntro}</p>
          </div>
          <div className="technology-grid">
            <article className="technology-card">
              <span className="technology-number">01</span>
              <div className="technology-icon icon-blue">⌘</div>
              <h3>{t.mlTitle}</h3>
              <p>{t.mlBody}</p>
            </article>
            <article className="technology-card">
              <span className="technology-number">02</span>
              <div className="technology-icon icon-violet">⠿</div>
              <h3>{t.dlTitle}</h3>
              <p>{t.dlBody}</p>
            </article>
            <article className="technology-card technology-card-highlight">
              <span className="technology-number">03</span>
              <div className="technology-icon icon-green">✳</div>
              <h3>{t.genTitle}</h3>
              <p>{t.genBody}</p>
            </article>
          </div>
        </section>

        <section className="content-section features-section page-section" id="features">
          <div className="center-heading">
            <span className="section-eyebrow">{t.featureEyebrow}</span>
            <h2>{t.featureTitle}</h2>
          </div>
          <div className="feature-grid">
            <article className="feature-card">
              <div className="feature-icon feature-blue">↑</div>
              <h3>{t.featureUpload}</h3>
              <p>{t.featureUploadBody}</p>
            </article>
            <article className="feature-card">
              <div className="feature-icon feature-purple">⌘</div>
              <h3>{t.featureAnalyze}</h3>
              <p>{t.featureAnalyzeBody}</p>
            </article>
            <article className="feature-card">
              <div className="feature-icon feature-green">✓</div>
              <h3>{t.featureResult}</h3>
              <p>{t.featureResultBody}</p>
            </article>
          </div>
        </section>

        <section className="evaluation-section page-section" id="evaluation">
          <div className="evaluation-copy">
            <span className="section-eyebrow">{t.evaluationEyebrow}</span>
            <h2>{t.evaluationTitle}</h2>
            <p>{t.evaluationBody}</p>
          </div>
          <ul className="evaluation-list">
            {[t.evaluationPointOne, t.evaluationPointTwo, t.evaluationPointThree].map((point) => (
              <li key={point}><span aria-hidden="true">!</span>{point}</li>
            ))}
          </ul>
        </section>

        <section className="prediction-section page-section" id="prediction">
          <div className="prediction-heading">
            <span className="section-eyebrow">{t.predictEyebrow}</span>
            <h2>{t.predictTitle}</h2>
            <p>{t.predictDescription}</p>
          </div>
          {!selectedFile ? (
            <ImageUploader onFileSelected={handleFileSelection} disabled={isLoading} t={t} />
          ) : (
            <ImagePreview
              imageUrl={imageUrl}
              fileName={selectedFile.name}
              onAnalyze={handleAnalyze}
              onRemove={handleReset}
              isLoading={isLoading}
              t={t}
            />
          )}

          {isLoading && (
            <div className="loading-panel">
              <div className="spinner" />
              <div><h4>{t.loadingTitle}</h4><p>{t.loadingMessage}</p></div>
            </div>
          )}
          {error && <div className="error-message" role="alert">{error}</div>}
          {result && <PredictionResult result={result} t={t} />}
          {result && (
            <button className="reset-button" type="button" onClick={handleReset}>
              {t.another}
            </button>
          )}
        </section>

        <div className="disclaimer-wrap"><Disclaimer t={t} /></div>
      </main>

      <footer className="site-footer">
        <a className="brand-mark footer-brand" href="#home">
          <span className="brand-icon" aria-hidden="true">C</span>
          <span>Chickenpox<span className="brand-accent">AI</span></span>
        </a>
        <span>{t.footer}</span>
        <a href="#home">{t.navHome} ↑</a>
      </footer>
    </div>
  );
}
