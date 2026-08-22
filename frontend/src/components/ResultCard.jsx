function valueOf(value, fallback = 'Not provided') {
  if (Array.isArray(value)) return value.join(', ')
  return value || fallback
}

function ResultCard({ result }) {
  const category = result.category || 'unknown'
  if (category === 'non_grape') return <article className="card result-card"><h2>Image not recognised</h2><p>This image does not appear to contain a grape disease or pest.</p></article>
  if (category === 'uncertain') return <article className="card result-card"><h2>Uncertain result</h2><p>The AI could not confidently determine the image category. Please try another clear grape leaf image.</p></article>
  const treatment = result.treatment || {}
  return <article className="card result-card"><span className="eyebrow">Analysis complete</span><h2>{valueOf(result.prediction, 'No prediction')}</h2><div className="result-meta"><span className="pill">{category.replace('_', ' ')}</span><span className="pill">{result.confidence != null ? `${(Number(result.confidence) * 100).toFixed(2)}% confidence` : 'Confidence unavailable'}</span></div><div className="result-sections"><div><h3>Description</h3><p>{valueOf(treatment.description)}</p></div><div><h3>Symptoms</h3><p>{valueOf(treatment.symptoms)}</p></div><div><h3>Management</h3><p>{valueOf(treatment.management)}</p></div><div><h3>Prevention</h3><p>{valueOf(treatment.prevention)}</p></div><div><h3>Treatment note</h3><p>{valueOf(treatment.treatment || treatment.treatment_note)}</p></div></div><div className="xai"><h3>AI Explanation</h3><p>Grad-CAM highlights image regions that influenced the model's prediction.</p>{result.xai?.available ? <p>{valueOf(result.xai.message || result.xai.explanation, 'An explanation was generated for this prediction.')} The heatmap path is available on the backend filesystem and is not displayed as a browser image.</p> : <p>XAI information is not available for this result.</p>}</div></article>
}

export default ResultCard
