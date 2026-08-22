function FeatureCard({ icon, title, children }) {
  return <article className="card"><div className="feature-icon" aria-hidden="true">{icon}</div><h3>{title}</h3><p>{children}</p></article>
}

export default FeatureCard
