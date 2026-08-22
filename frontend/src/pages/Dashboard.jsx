import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";

function Dashboard() {
  const [history, setHistory] = useState([]);
  const [selectedHistory, setSelectedHistory] = useState(null);

  // =========================================================
  // LOAD HISTORY
  // =========================================================

  const loadHistory = () => {
    try {
      const savedHistory = JSON.parse(
        localStorage.getItem("grapeGuardHistory") || "[]"
      );

      setHistory(
        Array.isArray(savedHistory) ? savedHistory : []
      );
    } catch (error) {
      console.error("Unable to load detection history:", error);
      setHistory([]);
    }
  };

  // =========================================================
  // INITIAL LOAD + LIVE UPDATE
  // =========================================================

  useEffect(() => {
    loadHistory();

    const handleHistoryUpdate = () => {
      loadHistory();
    };

    window.addEventListener("focus", handleHistoryUpdate);
    window.addEventListener(
      "grapeGuardHistoryUpdated",
      handleHistoryUpdate
    );

    return () => {
      window.removeEventListener("focus", handleHistoryUpdate);
      window.removeEventListener(
        "grapeGuardHistoryUpdated",
        handleHistoryUpdate
      );
    };
  }, []);

  // =========================================================
  // FORMAT DATE
  // =========================================================

  const formatDate = (dateString) => {
    if (!dateString) {
      return "Unknown date";
    }

    const date = new Date(dateString);

    if (Number.isNaN(date.getTime())) {
      return "Unknown date";
    }

    return date.toLocaleString([], {
      day: "numeric",
      month: "short",
      year: "numeric",
      hour: "numeric",
      minute: "2-digit",
    });
  };

  // =========================================================
  // CATEGORY LABEL
  // =========================================================

  const getCategoryLabel = (category) => {
    switch (category) {
      case "grape_disease":
        return "Disease";

      case "grape_pest":
        return "Pest";

      case "non_grape":
        return "Non-grape";

      case "uncertain":
        return "Uncertain";

      default:
        return "Analysis";
    }
  };

  // =========================================================
  // CONFIDENCE
  // =========================================================

  const getConfidence = (confidence) => {
    if (
      confidence === null ||
      confidence === undefined ||
      confidence === "" ||
      Number.isNaN(Number(confidence))
    ) {
      return "N/A";
    }

    return `${(Number(confidence) * 100).toFixed(2)}%`;
  };

  // =========================================================
  // DYNAMIC DASHBOARD STATISTICS
  // =========================================================

  const dashboardStats = useMemo(() => {
    const diseaseCount = history.filter(
      (item) => item.category === "grape_disease"
    ).length;

    const pestCount = history.filter(
      (item) => item.category === "grape_pest"
    ).length;

    const nonGrapeCount = history.filter(
      (item) => item.category === "non_grape"
    ).length;

    const confidentResults = history.filter(
      (item) =>
        item.confidence !== null &&
        item.confidence !== undefined &&
        !Number.isNaN(Number(item.confidence))
    );

    let averageConfidence = null;

    if (confidentResults.length > 0) {
      const total = confidentResults.reduce(
        (sum, item) => sum + Number(item.confidence),
        0
      );

      averageConfidence =
        (total / confidentResults.length) * 100;
    }

    return {
      total: history.length,
      disease: diseaseCount,
      pest: pestCount,
      nonGrape: nonGrapeCount,
      averageConfidence,
    };
  }, [history]);

  // =========================================================
  // CLEAR HISTORY
  // =========================================================

  const clearHistory = () => {
    const confirmed = window.confirm(
      "Are you sure you want to clear all detection history?"
    );

    if (!confirmed) {
      return;
    }

    localStorage.removeItem("grapeGuardHistory");

    setHistory([]);
    setSelectedHistory(null);

    window.dispatchEvent(
      new Event("grapeGuardHistoryUpdated")
    );
  };

  // =========================================================
  // CLOSE MODAL
  // =========================================================

  const closeHistoryDetails = () => {
    setSelectedHistory(null);
  };

  // =========================================================
  // SAFE TREATMENT VALUE
  // =========================================================

  const getTreatmentArray = (treatment, key) => {
    if (!treatment) {
      return [];
    }

    const value = treatment[key];

    if (Array.isArray(value)) {
      return value;
    }

    if (typeof value === "string" && value.trim()) {
      return [value];
    }

    return [];
  };

  // =========================================================
  // ESC KEY FOR MODAL
  // =========================================================

  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === "Escape") {
        setSelectedHistory(null);
      }
    };

    window.addEventListener("keydown", handleKeyDown);

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, []);

  // =========================================================
  // RENDER
  // =========================================================

  return (
    <main className="dashboard-page">
      <div className="dashboard-container">

        {/* =================================================
            HEADER
        ================================================= */}

        <section className="dashboard-header dashboard-header-enhanced">

          <div>
            <p className="section-eyebrow">
              WORKSPACE OVERVIEW
            </p>

            <h1>
              Make every observation count.
            </h1>

            <p className="dashboard-intro">
              Review what GrapeGuard AI can identify, then
              start a fresh analysis from one clear leaf image.
            </p>
          </div>

          <div className="dashboard-header-badge">
            <span className="dashboard-live-dot"></span>
            AI Detection Ready
          </div>

        </section>


        {/* =================================================
            SUMMARY CARDS
        ================================================= */}

        <section className="dashboard-stats">

          {/* Disease Classes */}

          <div className="dashboard-stat-card dashboard-stat-enhanced">

            <div className="stat-icon">
              🍃
            </div>

            <div>
              <strong>7</strong>

              <h3>
                Disease Classes
              </h3>

              <p>
                Supported disease classes
              </p>
            </div>

          </div>


          {/* Pest Classes */}

          <div className="dashboard-stat-card dashboard-stat-enhanced">

            <div className="stat-icon">
              🐞
            </div>

            <div>
              <strong>17</strong>

              <h3>
                Pest Classes
              </h3>

              <p>
                Supported pest classes
              </p>
            </div>

          </div>


          {/* Total Classes */}

          <div className="dashboard-stat-card dashboard-stat-enhanced">

            <div className="stat-icon">
              ▦
            </div>

            <div>
              <strong>24</strong>

              <h3>
                Total Classes
              </h3>

              <p>
                Disease + pest classes
              </p>
            </div>

          </div>


          {/* Live Analyses */}

          <div className="dashboard-stat-card dashboard-stat-enhanced dashboard-analysis-stat">

            <div className="stat-icon">
              ◉
            </div>

            <div>
              <strong>
                {dashboardStats.total}
              </strong>

              <h3>
                Total Analyses
              </h3>

              <p>
                Saved detection results
              </p>
            </div>

          </div>

        </section>


        {/* =================================================
            QUICK ACTION
        ================================================= */}

        <section className="dashboard-quick-actions">

          <div className="quick-action-content">

            <div>
              <p className="quick-action-label">
                READY TO ANALYZE?
              </p>

              <h2>
                Check a new grape leaf
              </h2>

              <p>
                Upload a clear leaf image and let GrapeGuard AI
                identify possible diseases or pests.
              </p>
            </div>

            <Link
              to="/detection"
              className="dashboard-primary-btn"
            >
              🍃 &nbsp; Start New Detection
              <span>→</span>
            </Link>

          </div>

        </section>


        {/* =================================================
            LIVE ANALYSIS OVERVIEW
        ================================================= */}

        {history.length > 0 && (

          <section className="dashboard-overview-strip">

            <div className="overview-heading">
              <div>
                <p className="section-eyebrow">
                  YOUR ACTIVITY
                </p>

                <h2>
                  Detection overview
                </h2>
              </div>

              {dashboardStats.averageConfidence !== null && (
                <div className="average-confidence">
                  <span>
                    Average confidence
                  </span>

                  <strong>
                    {dashboardStats.averageConfidence.toFixed(2)}%
                  </strong>
                </div>
              )}
            </div>


            <div className="overview-metrics">

              <div className="overview-metric">
                <span className="overview-metric-icon">
                  🔬
                </span>

                <div>
                  <strong>
                    {dashboardStats.total}
                  </strong>

                  <p>
                    Total analyses
                  </p>
                </div>
              </div>


              <div className="overview-metric">
                <span className="overview-metric-icon disease">
                  🍃
                </span>

                <div>
                  <strong>
                    {dashboardStats.disease}
                  </strong>

                  <p>
                    Disease detections
                  </p>
                </div>
              </div>


              <div className="overview-metric">
                <span className="overview-metric-icon pest">
                  🐞
                </span>

                <div>
                  <strong>
                    {dashboardStats.pest}
                  </strong>

                  <p>
                    Pest detections
                  </p>
                </div>
              </div>


              <div className="overview-metric">
                <span className="overview-metric-icon nongrape">
                  !
                </span>

                <div>
                  <strong>
                    {dashboardStats.nonGrape}
                  </strong>

                  <p>
                    Non-grape images
                  </p>
                </div>
              </div>

            </div>

          </section>

        )}


        {/* =================================================
            PERFORMANCE + SYSTEM
        ================================================= */}

        <section className="dashboard-middle-grid">

          {/* =================================================
              MODEL PERFORMANCE
          ================================================= */}

          <div className="dashboard-section">

            <div className="dashboard-section-heading">

              <div>
                <p className="section-eyebrow">
                  AI MODELS
                </p>

                <h2>
                  Model Performance
                </h2>
              </div>

              <span className="section-status">
                Verified
              </span>

            </div>


            <div className="performance-grid">

              <div className="performance-card performance-card-enhanced">

                <div className="performance-icon">
                  🍃
                </div>

                <div className="performance-card-content">

                  <h3>
                    Disease Model
                  </h3>

                  <strong>
                    99.77%
                  </strong>

                  <p>
                    Top-1 Test Accuracy
                  </p>

                  <div className="mini-progress">
                    <span
                      style={{
                        width: "99.77%",
                      }}
                    ></span>
                  </div>

                </div>

              </div>


              <div className="performance-card performance-card-enhanced">

                <div className="performance-icon">
                  🐞
                </div>

                <div className="performance-card-content">

                  <h3>
                    Pest Model
                  </h3>

                  <strong>
                    90.95%
                  </strong>

                  <p>
                    Top-1 Test Accuracy
                  </p>

                  <div className="mini-progress">
                    <span
                      style={{
                        width: "90.95%",
                      }}
                    ></span>
                  </div>

                </div>

              </div>

            </div>


            <p className="performance-note">
              ● &nbsp;
              Performance measured on the held-out test datasets.
            </p>

          </div>


          {/* =================================================
              SYSTEM STATUS
          ================================================= */}

          <div className="dashboard-section">

            <div className="dashboard-section-heading">

              <div>
                <p className="section-eyebrow">
                  SYSTEM
                </p>

                <h2>
                  System Status
                </h2>
              </div>

              <span className="section-status online">
                Online
              </span>

            </div>


            <div className="status-card status-card-enhanced">

              <div className="status-row">

                <span>
                  🖥️ &nbsp; Backend API
                </span>

                <strong>
                  <i></i>
                  Online
                </strong>

              </div>


              <div className="status-row">

                <span>
                  🍃 &nbsp; Disease Model
                </span>

                <strong>
                  <i></i>
                  Loaded
                </strong>

              </div>


              <div className="status-row">

                <span>
                  🐞 &nbsp; Pest Model
                </span>

                <strong>
                  <i></i>
                  Loaded
                </strong>

              </div>


              <div className="status-row">

                <span>
                  ▣ &nbsp; Treatment DB
                </span>

                <strong>
                  <i></i>
                  Available
                </strong>

              </div>


              <div className="status-row">

                <span>
                  ◉ &nbsp; XAI / Grad-CAM
                </span>

                <strong>
                  <i></i>
                  Available
                </strong>

              </div>

            </div>

          </div>

        </section>


        {/* =================================================
            HISTORY + HOW IT WORKS
        ================================================= */}

        <section className="dashboard-lower-grid">

          {/* =================================================
              DETECTION HISTORY
          ================================================= */}

          <div className="dashboard-section">

            <div className="dashboard-section-title-row">

              <div>
                <p className="section-eyebrow">
                  RECENT ACTIVITY
                </p>

                <h2>
                  Detection History
                </h2>
              </div>

              {history.length > 0 && (

                <div className="history-header-actions">

                  <span className="history-count">
                    {history.length}
                    {" "}
                    {history.length === 1
                      ? "analysis"
                      : "analyses"}
                  </span>

                  <button
                    type="button"
                    className="clear-history-btn"
                    onClick={clearHistory}
                  >
                    Clear History
                  </button>

                </div>

              )}

            </div>


            {/* EMPTY HISTORY */}

            {history.length === 0 ? (

              <div className="history-card history-empty-enhanced">

                <div className="history-icon">
                  ▣
                </div>

                <h3>
                  No detection history yet
                </h3>

                <p>
                  Your completed analyses will appear here
                  after you perform a detection.
                </p>

                <Link
                  to="/detection"
                  className="history-link"
                >
                  Start your first detection →
                </Link>

              </div>

            ) : (

              <div className="history-list">

                {history
                  .slice(0, 10)
                  .map((item) => (

                    <button
                      type="button"
                      className="history-item"
                      key={item.id || item.createdAt}
                      onClick={() =>
                        setSelectedHistory(item)
                      }
                    >

                      {/* IMAGE */}

                      <div className="history-image-wrapper">

                        {item.image ? (

                          <img
                            src={item.image}
                            alt={
                              item.prediction ||
                              "Detection result"
                            }
                            className="history-image"
                          />

                        ) : (

                          <div className="history-image-placeholder">
                            🍃
                          </div>

                        )}

                      </div>


                      {/* MAIN */}

                      <div className="history-main">

                        <div className="history-title-row">

                          <h3>
                            {item.prediction ||
                              "Unknown"}
                          </h3>

                          <span
                            className={`history-category ${
                              item.category || ""
                            }`}
                          >
                            {getCategoryLabel(
                              item.category
                            )}
                          </span>

                        </div>

                        <p className="history-date">
                          {formatDate(
                            item.createdAt
                          )}
                        </p>

                      </div>


                      {/* CONFIDENCE */}

                      <div className="history-confidence">

                        <span>
                          CONFIDENCE
                        </span>

                        <strong>
                          {getConfidence(
                            item.confidence
                          )}
                        </strong>

                      </div>


                      {/* ARROW */}

                      <span className="history-arrow">
                        →
                      </span>

                    </button>

                  ))}


                {history.length > 10 && (

                  <p className="history-more">
                    Showing your 10 most recent analyses.
                  </p>

                )}

              </div>

            )}

          </div>


          {/* =================================================
              HOW IT WORKS
          ================================================= */}

          <div className="dashboard-section">

            <div className="dashboard-section-heading">

              <div>
                <p className="section-eyebrow">
                  WORKFLOW
                </p>

                <h2>
                  How GrapeGuard AI Works
                </h2>
              </div>

            </div>


            <div className="workflow-grid">

              <div className="workflow-card workflow-card-enhanced">

                <span>
                  01
                </span>

                <div className="workflow-icon">
                  ☁
                </div>

                <h3>
                  Upload
                </h3>

                <p>
                  Choose a clear image of a grape leaf
                  for analysis.
                </p>

                <div className="workflow-arrow">
                  →
                </div>

              </div>


              <div className="workflow-card workflow-card-enhanced">

                <span>
                  02
                </span>

                <div className="workflow-icon">
                  ▣
                </div>

                <h3>
                  Classify
                </h3>

                <p>
                  The AI router sends the image to the
                  relevant disease or pest model.
                </p>

                <div className="workflow-arrow">
                  →
                </div>

              </div>


              <div className="workflow-card workflow-card-enhanced">

                <span>
                  03
                </span>

                <div className="workflow-icon">
                  ✓
                </div>

                <h3>
                  Respond
                </h3>

                <p>
                  Review the prediction, confidence,
                  explanation and guidance.
                </p>

              </div>

            </div>

          </div>

        </section>


        {/* =================================================
            HELP
        ================================================= */}

        <section className="dashboard-help dashboard-help-enhanced">

          <div>

            <div className="help-icon">
              ?
            </div>

            <div>

              <p className="section-eyebrow">
                SUPPORT
              </p>

              <h2>
                Help &amp; User Guide
              </h2>

              <p>
                Understand image requirements,
                confidence scores and treatment context.
              </p>

            </div>

          </div>


          <Link
            to="/help"
            className="help-button"
          >
            Go to Help Page
            <span>→</span>
          </Link>

        </section>


        {/* =================================================
            HISTORY DETAILS MODAL
        ================================================= */}

        {selectedHistory && (

          <div
            className="history-modal-overlay"
            onClick={closeHistoryDetails}
          >

            <div
              className="history-modal"
              onClick={(event) =>
                event.stopPropagation()
              }
            >

              {/* HEADER */}

              <div className="history-modal-header">

                <div>

                  <p className="section-eyebrow">
                    ANALYSIS DETAILS
                  </p>

                  <h2>
                    {selectedHistory.prediction ||
                      "Unknown"}
                  </h2>

                </div>


                <button
                  type="button"
                  className="history-modal-close"
                  onClick={closeHistoryDetails}
                  aria-label="Close"
                >
                  ×
                </button>

              </div>


              {/* SUMMARY */}

              <div className="history-detail-summary">

                <span
                  className={`history-category ${
                    selectedHistory.category || ""
                  }`}
                >
                  {getCategoryLabel(
                    selectedHistory.category
                  )}
                </span>


                <div className="history-detail-confidence">

                  <span>
                    CONFIDENCE
                  </span>

                  <strong>
                    {getConfidence(
                      selectedHistory.confidence
                    )}
                  </strong>

                </div>

              </div>


              {/* IMAGES */}

              <div className="history-detail-images">

                {/* ORIGINAL */}

                <div className="history-detail-image-card">

                  <h3>
                    Original Image
                  </h3>

                  {selectedHistory.image ? (

                    <img
                      src={selectedHistory.image}
                      alt="Original grape leaf"
                    />

                  ) : (

                    <div className="history-no-image">

                      <span>
                        🍃
                      </span>

                      <p>
                        Original image is not available
                        for this analysis.
                      </p>

                    </div>

                  )}

                </div>


                {/* GRAD-CAM */}

                {selectedHistory.xai?.heatmap_path && (

                  <div className="history-detail-image-card">

                    <h3>
                      AI Heatmap
                    </h3>

                    <img
                      src={`http://127.0.0.1:8000${selectedHistory.xai.heatmap_path}`}
                      alt="Grad-CAM explanation"
                      onError={(event) => {
                        event.currentTarget.style.display =
                          "none";
                      }}
                    />

                  </div>

                )}

              </div>


              {/* DATE */}

              <p className="history-detail-date">

                <strong>
                  Analyzed:
                </strong>{" "}
                {formatDate(
                  selectedHistory.createdAt
                )}

                {"  •  "}

                <strong>
                  Image:
                </strong>{" "}
                {selectedHistory.fileName ||
                  "Uploaded image"}

              </p>


              {/* TREATMENT */}

              {selectedHistory.treatment && (

                <div className="history-treatment">

                  <p className="guidance-label">
                    MANAGEMENT GUIDANCE
                  </p>

                  <h3>
                    Recommended information
                  </h3>


                  {selectedHistory.treatment.description && (

                    <p className="history-treatment-description">
                      {
                        selectedHistory.treatment
                          .description
                      }
                    </p>

                  )}


                  <div className="history-detail-columns">

                    {/* SYMPTOMS */}

                    {getTreatmentArray(
                      selectedHistory.treatment,
                      "symptoms"
                    ).length > 0 && (

                      <div>

                        <h3>
                          Symptoms
                        </h3>

                        <ul>

                          {getTreatmentArray(
                            selectedHistory.treatment,
                            "symptoms"
                          ).map(
                            (item, index) => (

                              <li key={index}>
                                {item}
                              </li>

                            )
                          )}

                        </ul>

                      </div>

                    )}


                    {/* MANAGEMENT */}

                    {getTreatmentArray(
                      selectedHistory.treatment,
                      "management"
                    ).length > 0 && (

                      <div>

                        <h3>
                          Management
                        </h3>

                        <ul>

                          {getTreatmentArray(
                            selectedHistory.treatment,
                            "management"
                          ).map(
                            (item, index) => (

                              <li key={index}>
                                {item}
                              </li>

                            )
                          )}

                        </ul>

                      </div>

                    )}


                    {/* PREVENTION */}

                    {getTreatmentArray(
                      selectedHistory.treatment,
                      "prevention"
                    ).length > 0 && (

                      <div>

                        <h3>
                          Prevention
                        </h3>

                        <ul>

                          {getTreatmentArray(
                            selectedHistory.treatment,
                            "prevention"
                          ).map(
                            (item, index) => (

                              <li key={index}>
                                {item}
                              </li>

                            )
                          )}

                        </ul>

                      </div>

                    )}

                  </div>


                  {selectedHistory.treatment
                    .treatment_note && (

                    <div className="history-treatment-note">

                      <strong>
                        Important
                      </strong>

                      <p>
                        {
                          selectedHistory.treatment
                            .treatment_note
                        }
                      </p>

                    </div>

                  )}

                </div>

              )}


              {/* ROUTER */}

              {selectedHistory.router && (

                <div className="history-router-info">

                  <p className="guidance-label">
                    AI ROUTER
                  </p>

                  <div className="router-probabilities">

                    <div>
                      <span>
                        Disease
                      </span>

                      <strong>
                        {selectedHistory.router
                          .grape_disease !==
                        undefined
                          ? `${(
                              selectedHistory.router
                                .grape_disease * 100
                            ).toFixed(1)}%`
                          : "N/A"}
                      </strong>
                    </div>


                    <div>
                      <span>
                        Pest
                      </span>

                      <strong>
                        {selectedHistory.router
                          .grape_pest !==
                        undefined
                          ? `${(
                              selectedHistory.router
                                .grape_pest * 100
                            ).toFixed(1)}%`
                          : "N/A"}
                      </strong>
                    </div>


                    <div>
                      <span>
                        Non-grape
                      </span>

                      <strong>
                        {selectedHistory.router
                          .non_grape !==
                        undefined
                          ? `${(
                              selectedHistory.router
                                .non_grape * 100
                            ).toFixed(1)}%`
                          : "N/A"}
                      </strong>
                    </div>

                  </div>

                </div>

              )}


              {/* FOOTER */}

              <div className="history-modal-footer">

                <button
                  type="button"
                  className="history-modal-done"
                  onClick={closeHistoryDetails}
                >
                  Close Details
                </button>

              </div>

            </div>

          </div>

        )}

      </div>
    </main>
  );
}

export default Dashboard;