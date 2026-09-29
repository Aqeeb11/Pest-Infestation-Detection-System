import { useState, useEffect, useRef } from "react";
import { Link } from "react-router-dom";

function Detection() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [inputMode, setInputMode] = useState("upload");
  const [cameraPanelOpen, setCameraPanelOpen] = useState(false);
  const [cameraReview, setCameraReview] = useState(false);
  const [cameraStream, setCameraStream] = useState(null);
  const [cameraStarting, setCameraStarting] = useState(false);
  const [cameraError, setCameraError] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const cameraRequestId = useRef(0);

  const stopCamera = (closePanel = false) => {
    cameraRequestId.current += 1;

    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }

    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }

    setCameraStream(null);
    setCameraStarting(false);

    if (closePanel) {
      setCameraPanelOpen(false);
    }
  };

  const getCameraErrorMessage = (cameraError) => {
    if (cameraError?.name === "NotAllowedError" || cameraError?.name === "SecurityError") {
      return "Camera permission was denied. Allow camera access in your browser settings and try again.";
    }

    if (cameraError?.name === "NotFoundError" || cameraError?.name === "DevicesNotFoundError") {
      return "No camera was found on this device.";
    }

    if (cameraError?.name === "NotReadableError" || cameraError?.name === "TrackStartError") {
      return "The camera is unavailable or already in use by another app.";
    }

    if (cameraError?.name === "AbortError") {
      return "The camera could not start. It may already be in use by another app.";
    }

    if (cameraError?.name === "OverconstrainedError") {
      return "The requested camera is unavailable. Try another camera or upload an image instead.";
    }

    return "Unable to access the camera. Check that a camera is connected and available, or upload an image instead.";
  };

  const startCamera = async () => {
    setCameraPanelOpen(true);
    setCameraReview(false);
    setCameraError("");

    if (!navigator.mediaDevices?.getUserMedia) {
      setCameraError("This browser does not support camera access. Upload an image instead.");
      return;
    }

    const requestId = ++cameraRequestId.current;
    setCameraStarting(true);

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: false,
        video: { facingMode: { ideal: "environment" } },
      });

      if (requestId !== cameraRequestId.current) {
        stream.getTracks().forEach((track) => track.stop());
        return;
      }

      streamRef.current = stream;
      setCameraStream(stream);
    } catch (cameraFailure) {
      if (requestId === cameraRequestId.current) {
        setCameraError(getCameraErrorMessage(cameraFailure));
      }
    } finally {
      if (requestId === cameraRequestId.current) {
        setCameraStarting(false);
      }
    }
  };

  const handleUseCamera = () => {
    stopCamera(true);

    if (preview) {
      URL.revokeObjectURL(preview);
    }

    setSelectedFile(null);
    setPreview(null);
    setResult(null);
    setError("");
    setInputMode("camera");
    startCamera();
  };

  const handleUseUpload = () => {
    stopCamera(true);
    setCameraReview(false);
    setCameraError("");
    setInputMode("upload");
  };

  const handleCapturePhoto = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;

    if (!video || !canvas || !video.videoWidth || !video.videoHeight) {
      setCameraError("The camera is not ready yet. Wait for the preview, then try again.");
      return;
    }

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const context = canvas.getContext("2d");

    if (!context) {
      setCameraError("Unable to capture this photo. Please try again or upload an image.");
      return;
    }

    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const requestId = cameraRequestId.current;
    canvas.toBlob((blob) => {
      if (requestId !== cameraRequestId.current) {
        return;
      }

      if (!blob) {
        setCameraError("Unable to capture this photo. Please try again or upload an image.");
        stopCamera();
        return;
      }

      const photoFile = new File([blob], `grape-leaf-${Date.now()}.jpg`, {
        type: "image/jpeg",
      });

      if (preview) {
        URL.revokeObjectURL(preview);
      }

      setSelectedFile(photoFile);
      setPreview(URL.createObjectURL(photoFile));
      setResult(null);
      setError("");
      setCameraError("");
      setCameraReview(true);
      stopCamera();
    }, "image/jpeg", 0.92);
  };

  const handleRetakePhoto = () => {
    if (preview) {
      URL.revokeObjectURL(preview);
    }

    setSelectedFile(null);
    setPreview(null);
    setResult(null);
    setCameraReview(false);
    startCamera();
  };

  const handleUsePhoto = () => {
    stopCamera(true);
    setCameraReview(false);
    setCameraError("");
    setInputMode("upload");
  };

  // =========================================================
  // CONVERT IMAGE TO PERSISTENT DATA URL
  // =========================================================

  const imageToDataUrl = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();

      reader.onload = () => {
        const image = new Image();

        image.onload = () => {
          try {
            const maxSize = 1000;

            let width = image.width;
            let height = image.height;

            if (width > maxSize || height > maxSize) {
              if (width > height) {
                height = Math.round((height * maxSize) / width);
                width = maxSize;
              } else {
                width = Math.round((width * maxSize) / height);
                height = maxSize;
              }
            }

            const canvas = document.createElement("canvas");

            canvas.width = width;
            canvas.height = height;

            const ctx = canvas.getContext("2d");

            if (!ctx) {
              reject(
                new Error("Unable to prepare image for history.")
              );
              return;
            }

            ctx.drawImage(image, 0, 0, width, height);

            const dataUrl = canvas.toDataURL(
              "image/jpeg",
              0.78
            );

            resolve(dataUrl);
          } catch (err) {
            reject(err);
          }
        };

        image.onerror = () => {
          reject(
            new Error("Unable to process uploaded image.")
          );
        };

        image.src = reader.result;
      };

      reader.onerror = () => {
        reject(
          new Error("Unable to read uploaded image.")
        );
      };

      reader.readAsDataURL(file);
    });
  };

  // =========================================================
  // SAVE DETECTION TO HISTORY
  // =========================================================

  const saveDetectionHistory = async (predictionResult) => {
    if (!predictionResult) {
      return;
    }

    try {
      let historyImage = null;

      if (selectedFile) {
        historyImage = await imageToDataUrl(selectedFile);
      }

      const historyItem = {
        id:
          Date.now() +
          "-" +
          Math.random().toString(36).slice(2, 9),

        image: historyImage,

        fileName:
          selectedFile?.name || "Uploaded image",

        category:
          predictionResult.category || null,

        prediction:
          predictionResult.prediction || null,

        confidence:
          predictionResult.confidence ?? null,

        router:
          predictionResult.router || null,

        xai:
          predictionResult.xai || null,

        treatment:
          predictionResult.treatment || null,

        createdAt:
          new Date().toISOString(),
      };

      const existingHistory = JSON.parse(
        localStorage.getItem("grapeGuardHistory") || "[]"
      );

      const safeHistory = Array.isArray(existingHistory)
        ? existingHistory
        : [];

      const updatedHistory = [
        historyItem,
        ...safeHistory,
      ];

      const limitedHistory = updatedHistory.slice(0, 20);

      try {
        localStorage.setItem(
          "grapeGuardHistory",
          JSON.stringify(limitedHistory)
        );
      } catch (storageError) {
        console.warn(
          "History storage limit reached. Retrying with fewer records.",
          storageError
        );

        const smallerHistory =
          limitedHistory.slice(0, 10);

        try {
          localStorage.setItem(
            "grapeGuardHistory",
            JSON.stringify(smallerHistory)
          );
        } catch (secondError) {
          console.error(
            "Unable to save detection history:",
            secondError
          );
        }
      }

      window.dispatchEvent(
        new Event("grapeGuardHistoryUpdated")
      );
    } catch (err) {
      console.error(
        "Unable to save detection history:",
        err
      );
    }
  };

  // =========================================================
  // FILE SELECTION
  // =========================================================

  const handleFileChange = (event) => {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    if (!file.type.startsWith("image/")) {
      setError("Please select a valid image file.");
      return;
    }

    if (file.size > 15 * 1024 * 1024) {
      setError(
        "Please select an image smaller than 15 MB."
      );
      return;
    }

    if (preview) {
      URL.revokeObjectURL(preview);
    }

    setSelectedFile(file);

    setPreview(
      URL.createObjectURL(file)
    );

    setResult(null);
    setError("");
  };

  // =========================================================
  // ANALYZE IMAGE
  // =========================================================

  const handleAnalyze = async () => {
    if (!selectedFile) {
      setError(
        "Please upload a grape leaf image first."
      );
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const formData = new FormData();

      formData.append(
        "file",
        selectedFile
      );

      const response = await fetch(
        "http://127.0.0.1:8000/predict",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error(
          `Backend error: ${response.status}`
        );
      }

      const data = await response.json();

      if (!data.success) {
        throw new Error(
          data.message ||
            "Prediction failed."
        );
      }

      setResult(data);

      await saveDetectionHistory(data);
    } catch (err) {
      console.error(
        "Prediction error:",
        err
      );

      setError(
        err.message ||
          "Unable to connect to the GrapeGuard AI backend."
      );
    } finally {
      setLoading(false);
    }
  };

  // =========================================================
  // REMOVE / RESET CURRENT DETECTION
  // =========================================================

  const handleRemove = () => {
    stopCamera(true);

    if (preview) {
      URL.revokeObjectURL(preview);
    }

    setSelectedFile(null);
    setPreview(null);
    setInputMode("upload");
    setCameraReview(false);
    setCameraError("");
    setResult(null);
    setError("");
    setLoading(false);
  };

  // =========================================================
  // CLEAN PREVIEW URL
  // =========================================================

  useEffect(() => {
    if (!cameraStream || !cameraPanelOpen || cameraReview) {
      return;
    }

    const video = videoRef.current;

    if (!video) {
      return;
    }

    video.srcObject = cameraStream;
    video.play().catch(() => {
      setCameraError("The camera preview could not start. Try again or upload an image instead.");
    });

    return () => {
      video.srcObject = null;
    };
  }, [cameraStream, cameraPanelOpen, cameraReview]);

  useEffect(() => () => {
    cameraRequestId.current += 1;

    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
  }, []);

  useEffect(() => {
    return () => {
      if (preview) {
        URL.revokeObjectURL(preview);
      }
    };
  }, [preview]);

  // =========================================================
  // RENDER
  // =========================================================

  return (
    <main className="detection-page">

      <div className="detection-container">

        {/* =================================================
            HEADER
        ================================================= */}

        <section className="detection-header">

          <p className="section-eyebrow">
            AI LEAF ANALYSIS
          </p>

          <h1>
            Check your grape leaf.
          </h1>

          <p>
            Upload a clear grape leaf image and
            GrapeGuard AI will identify possible
            diseases or pests using machine learning.
          </p>

        </section>


        {/* =================================================
            DETECTION WORKSPACE
        ================================================= */}

        <section className="detection-workspace">

          {/* =================================================
              UPLOAD CARD
          ================================================= */}

          <div className="upload-card">

            <div className="upload-card-header">

              <span className="step-label">
                01 / UPLOAD
              </span>

              <h2>
                Choose a leaf image
              </h2>

              <p>
                Use a clear image where the grape leaf
                is visible.
              </p>

            </div>


            <div className="input-mode-switch" role="group" aria-label="Choose image input method">
              <button
                type="button"
                className={inputMode === "upload" ? "input-mode-button active" : "input-mode-button"}
                aria-pressed={inputMode === "upload"}
                onClick={handleUseUpload}
              >
                Upload Image
              </button>
              <button
                type="button"
                className={inputMode === "camera" ? "input-mode-button active" : "input-mode-button"}
                aria-pressed={inputMode === "camera"}
                onClick={handleUseCamera}
              >
                Use Camera
              </button>
            </div>


            {/* UPLOAD */}

            {inputMode === "camera" && cameraPanelOpen && !cameraReview ? (
              <div className="camera-capture">
                <div className="camera-frame">
                  {cameraStream ? (
                    <video
                      ref={videoRef}
                      autoPlay
                      muted
                      playsInline
                      aria-label="Live camera preview"
                    />
                  ) : (
                    <div className="camera-status" role="status">
                      {cameraStarting ? "Starting camera..." : "Camera preview is unavailable."}
                    </div>
                  )}
                </div>
                <canvas ref={canvasRef} className="camera-canvas" aria-hidden="true" />
                {cameraError && (
                  <div className="detection-error" role="alert" aria-live="assertive">
                    {cameraError}
                  </div>
                )}
                <button
                  type="button"
                  className="capture-button"
                  onClick={handleCapturePhoto}
                  disabled={!cameraStream || cameraStarting}
                  aria-label="Capture photo from camera"
                >
                  Capture Photo
                </button>
              </div>
            ) : !preview ? (

              <label className="upload-zone">

                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileChange}
                  hidden
                />

                <div className="upload-icon">
                  ↑
                </div>

                <h3>
                  Drop your image here
                </h3>

                <p>
                  or click to browse from your computer
                </p>

                <span>
                  JPG, JPEG, PNG or WEBP
                </span>

              </label>

            ) : (

              <div className="preview-area">

                <img
                  src={preview}
                  alt="Selected grape leaf"
                  className="leaf-preview"
                />

                <div className="preview-info">

                  <div>

                    <strong>
                      {selectedFile?.name}
                    </strong>

                    <p>
                      {(
                        selectedFile?.size /
                        1024 /
                        1024
                      ).toFixed(2)}{" "}
                      MB
                    </p>

                  </div>

                  <button
                    type="button"
                    onClick={handleRemove}
                    className="remove-image"
                  >
                    Remove
                  </button>

                </div>

                {cameraReview && (
                  <div className="camera-review-actions">
                    <button
                      type="button"
                      className="camera-secondary-button"
                      onClick={handleRetakePhoto}
                      aria-label="Retake photo"
                    >
                      Retake
                    </button>
                    <button
                      type="button"
                      className="camera-confirm-button"
                      onClick={handleUsePhoto}
                      aria-label="Use captured photo"
                    >
                      Use Photo
                    </button>
                  </div>
                )}

              </div>

            )}


            {/* ERROR */}

            {error && (
              <div className="detection-error">
                {error}
              </div>
            )}


            {/* ANALYZE BUTTON */}

            <button
              type="button"
              className="analyze-button"
              onClick={handleAnalyze}
              disabled={
                !selectedFile ||
                loading
              }
            >

              {loading
                ? "Analyzing..."
                : "Analyze Image →"}

            </button>

          </div>


          {/* =================================================
              INFORMATION CARD
          ================================================= */}

          <aside className="detection-info-card">

            <span className="step-label">
              02 / ANALYZE
            </span>

            <h2>
              What happens next?
            </h2>

            <div className="analysis-step">

              <span>
                01
              </span>

              <div>

                <strong>
                  Image routing
                </strong>

                <p>
                  The system determines whether the image
                  is associated with grape disease, grape
                  pest or a non-grape image.
                </p>

              </div>

            </div>

            <div className="analysis-step">

              <span>
                02
              </span>

              <div>

                <strong>
                  AI classification
                </strong>

                <p>
                  The appropriate machine-learning model
                  identifies the predicted disease or pest.
                </p>

              </div>

            </div>

            <div className="analysis-step">

              <span>
                03
              </span>

              <div>

                <strong>
                  Actionable result
                </strong>

                <p>
                  Results include confidence, management
                  guidance, prevention information and
                  AI explanation.
                </p>

              </div>

            </div>

            <div className="detection-note">

              <strong>
                Tip
              </strong>

              <p>
                For better results, use a well-lit image
                with the grape leaf clearly visible.
              </p>

            </div>

          </aside>

        </section>


        {/* =================================================
            RESULT
        ================================================= */}

        {result && (

          <section className="detection-result">

            {/* =================================================
                RESULT HEADER
            ================================================= */}

            <div className="result-header">

              <div>

                <p className="section-eyebrow">
                  03 / RESULT
                </p>

                <h2>
                  Analysis Result
                </h2>

              </div>

              <span
                className={`result-category ${result.category}`}
              >

                {result.category ===
                "grape_disease"
                  ? "GRAPE DISEASE"
                  : result.category ===
                    "grape_pest"
                  ? "GRAPE PEST"
                  : result.category ===
                    "uncertain"
                  ? "UNCERTAIN"
                  : "NON-GRAPE IMAGE"}

              </span>

            </div>


            {/* =================================================
                NON-GRAPE
            ================================================= */}

            {result.category ===
              "non_grape" && (

              <div className="non-grape-result">

                <div className="non-grape-icon">
                  !
                </div>

                <div>

                  <h3>
                    Image not recognized as a grape image
                  </h3>

                  <p>
                    Please upload a clear image of a
                    grape leaf for disease or pest detection.
                  </p>

                </div>

              </div>

            )}


            {/* =================================================
                UNCERTAIN
            ================================================= */}

            {result.category ===
              "uncertain" && (

              <div className="non-grape-result">

                <div className="non-grape-icon">
                  ?
                </div>

                <div>

                  <h3>
                    The image could not be classified confidently
                  </h3>

                  <p>
                    Please upload a clearer grape leaf image
                    with better lighting and visibility.
                  </p>

                </div>

              </div>

            )}


            {/* =================================================
                DISEASE / PEST
            ================================================= */}

            {result.category !==
              "non_grape" &&
              result.category !==
                "uncertain" && (

              <>

                {/* =================================================
                    PREDICTION
                ================================================= */}

                <div className="prediction-card">

                  <div className="prediction-main">

                    <div className="prediction-icon">

                      {result.category ===
                      "grape_disease"
                        ? "🍃"
                        : "🐞"}

                    </div>

                    <div>

                      <span className="prediction-label">
                        DETECTED
                      </span>

                      <h3>
                        {result.prediction}
                      </h3>

                      <p>
                        {result.category ===
                        "grape_pest"
                          ? "Grape pest"
                          : "Grape disease"}
                      </p>

                    </div>

                  </div>


                  {/* CONFIDENCE */}

                  <div className="confidence-box">

                    <span>
                      CONFIDENCE
                    </span>

                    <strong>

                      {result.confidence !==
                        null &&
                      result.confidence !==
                        undefined
                        ? `${(
                            result.confidence *
                            100
                          ).toFixed(2)}%`
                        : "N/A"}

                    </strong>

                    {result.confidence !==
                      null &&
                      result.confidence !==
                        undefined && (

                        <div className="confidence-bar">

                          <div
                            style={{
                              width: `${Math.min(
                                result.confidence *
                                  100,
                                100
                              )}%`,
                            }}
                          />

                        </div>

                      )}

                  </div>

                </div>


                {/* =================================================
                    MANAGEMENT GUIDANCE
                ================================================= */}

                {result.treatment && (

                  <div className="result-guidance">

                    <div className="guidance-header">

                      <span>
                        🌿
                      </span>

                      <div>

                        <p className="guidance-label">
                          MANAGEMENT GUIDANCE
                        </p>

                        <h3>
                          What you can do
                        </h3>

                      </div>

                    </div>


                    {result.treatment.description && (

                      <p className="treatment-description">
                        {result.treatment.description}
                      </p>

                    )}


                    <div className="guidance-columns">

                      {/* SYMPTOMS */}

                      {result.treatment
                        .symptoms?.length >
                        0 && (

                        <div className="guidance-block">

                          <h4>
                            Symptoms
                          </h4>

                          <ul>

                            {result.treatment.symptoms.map(
                              (
                                item,
                                index
                              ) => (

                                <li
                                  key={index}
                                >
                                  {item}
                                </li>

                              )
                            )}

                          </ul>

                        </div>

                      )}


                      {/* MANAGEMENT */}

                      {result.treatment
                        .management?.length >
                        0 && (

                        <div className="guidance-block">

                          <h4>
                            Management
                          </h4>

                          <ul>

                            {result.treatment.management.map(
                              (
                                item,
                                index
                              ) => (

                                <li
                                  key={index}
                                >
                                  {item}
                                </li>

                              )
                            )}

                          </ul>

                        </div>

                      )}


                      {/* PREVENTION */}

                      {result.treatment
                        .prevention?.length >
                        0 && (

                        <div className="guidance-block">

                          <h4>
                            Prevention
                          </h4>

                          <ul>

                            {result.treatment.prevention.map(
                              (
                                item,
                                index
                              ) => (

                                <li
                                  key={index}
                                >
                                  {item}
                                </li>

                              )
                            )}

                          </ul>

                        </div>

                      )}

                    </div>


                    {/* IMPORTANT NOTE */}

                    {result.treatment
                      .treatment_note && (

                      <div className="treatment-note">

                        <strong>
                          Important
                        </strong>

                        <p>
                          {
                            result.treatment
                              .treatment_note
                          }
                        </p>

                      </div>

                    )}

                  </div>

                )}


                {/* =================================================
                    XAI / GRAD-CAM
                ================================================= */}

                {result.xai?.available && (

                  <div className="xai-result">

                    {/* XAI HEADER */}

                    <div className="xai-result-header">

                      <div className="xai-explanation-text">

                        <p className="guidance-label">
                          AI EXPLANATION
                        </p>

                        <h3>
                          Why the model made this prediction
                        </h3>

                        <p>
                          Compare the original leaf with the
                          Grad-CAM heatmap to see which regions
                          contributed most to the prediction.
                        </p>

                      </div>

                      <div className="xai-status">
                        <span>✓</span>
                        Grad-CAM Available
                      </div>

                    </div>


                    {/* ORIGINAL + HEATMAP */}

                    {result.xai.heatmap_path && (

                      <>

                        <div className="xai-comparison">

                          {/* ORIGINAL IMAGE */}

                          <div className="xai-image-card">

                            <div className="xai-image-title">

                              <span>01</span>

                              <div>
                                <strong>
                                  Original Image
                                </strong>

                                <p>
                                  Uploaded grape leaf
                                </p>
                              </div>

                            </div>

                            {preview ? (

                              <img
                                src={preview}
                                alt="Original uploaded grape leaf"
                                className="comparison-image"
                              />

                            ) : (

                              <div className="comparison-image-fallback">
                                Original image unavailable
                              </div>

                            )}

                          </div>


                          {/* AI HEATMAP */}

                          <div className="xai-image-card">

                            <div className="xai-image-title">

                              <span>02</span>

                              <div>
                                <strong>
                                  AI Heatmap
                                </strong>

                                <p>
                                  Grad-CAM explanation
                                </p>
                              </div>

                            </div>

                            <img
                              src={`http://127.0.0.1:8000${result.xai.heatmap_path}`}
                              alt={`Grad-CAM explanation for ${result.prediction}`}
                              className="comparison-image"
                              onError={(event) => {
                                event.currentTarget.style.display = "none";

                                const fallback =
                                  event.currentTarget.parentElement?.querySelector(
                                    ".heatmap-image-fallback"
                                  );

                                if (fallback) {
                                  fallback.style.display = "flex";
                                }
                              }}
                            />

                            <div
                              className="heatmap-image-fallback"
                              style={{ display: "none" }}
                            >
                              Heatmap could not be loaded
                            </div>

                          </div>

                        </div>


                        {/* =================================================
                            ANALYZE ANOTHER IMAGE
                            CENTERED BELOW BOTH IMAGES
                        ================================================= */}

                        <div className="analyze-again-section">

                          <button
                            type="button"
                            className="analyze-again-button"
                            onClick={handleRemove}
                          >

                            <span className="analyze-again-icon">
                              🍃
                            </span>

                            <span>
                              Analyze Another Image
                            </span>

                            <span className="analyze-again-arrow">
                              →
                            </span>

                          </button>

                        </div>

                      </>

                    )}


                    {/* =================================================
                        HEATMAP EXPLANATION
                    ================================================= */}

                    <div className="heatmap-description">

                      <strong>
                        How to read this:
                      </strong>

                      <p>
                        The highlighted regions indicate areas
                        that contributed most to the model's
                        prediction. This visualization helps
                        you understand where the model focused
                        when making its decision.
                      </p>

                    </div>

                  </div>

                )}

                {/* =================================================
                    ANALYZE AGAIN
                    FALLBACK WHEN XAI IS NOT AVAILABLE
                ================================================= */}

                {!result.xai?.available && (

                  <div className="analyze-again-section">

                    <button
                      type="button"
                      className="analyze-again-button"
                      onClick={handleRemove}
                    >

                      <span className="analyze-again-icon">
                        🍃
                      </span>

                      <span>
                        Analyze Another Image
                      </span>

                      <span className="analyze-again-arrow">
                        →
                      </span>

                    </button>

                  </div>

                )}


              </>

            )}

          </section>

        )}


        {/* =================================================
            BACK TO DASHBOARD
        ================================================= */}

        <div className="back-dashboard">

          <Link to="/dashboard">
            ← Back to Dashboard
          </Link>

        </div>

      </div>

    </main>
  );
}

export default Detection;