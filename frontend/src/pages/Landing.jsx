import { Link } from "react-router-dom";
import heroImage from "../assets/hero.png";

function Landing() {
  return (
    <main className="landing-page">

      {/* HERO */}
      <section className="hero-section">

        {/* Left Content */}
        <div className="hero-content">

          <div className="hero-badge">
            <span className="badge-icon">🍃</span>
            AI FOR HEALTHIER VINEYARDS
          </div>

          <h1 className="hero-title">
            Protect every leaf.
            <br />
            <span>Grow a healthier</span>
            <br />
            vineyard.
          </h1>

          <p className="hero-description">
            GrapeGuard AI uses machine learning to identify grape diseases
            and pests from leaf images and provide intelligent management
            and prevention guidance.
          </p>

          {/* Buttons */}
          <div className="hero-buttons">

            <Link to="/detection" className="primary-button">
              <span>Start Detection</span>
              <span className="button-arrow">→</span>
            </Link>

            <Link to="/dashboard" className="secondary-button">
              <span className="dashboard-icon">▮▮</span>
              <span>Explore Dashboard</span>
            </Link>

          </div>

          {/* Feature highlights */}
          <div className="hero-features">

            <div className="hero-feature">
              <div className="feature-icon">
                🍃
              </div>

              <div>
                <strong>AI Powered</strong>
                <span>Detection</span>
              </div>
            </div>

            <div className="feature-divider"></div>

            <div className="hero-feature">
              <div className="feature-icon">
                🎯
              </div>

              <div>
                <strong>24 Classes</strong>
                <span>Covered</span>
              </div>
            </div>

            <div className="feature-divider"></div>

            <div className="hero-feature">
              <div className="feature-icon">
                🛡️
              </div>

              <div>
                <strong>Smart Guidance</strong>
                <span>& Prevention</span>
              </div>
            </div>

          </div>
        </div>

        {/* Right Visual */}
        <div className="hero-visual">

          <div className="hero-image-wrapper">

            <img
  src={heroImage}
  alt="Healthy grape leaves and grapes"
  className="hero-image"
/>

          </div>

        </div>

      </section>

    </main>
  );
}

export default Landing;