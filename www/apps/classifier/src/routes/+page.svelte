<script>
  import { onMount, onDestroy } from 'svelte';

  let carPartsData = {};
  const displayOrder = [
    { key: 'front_right', label: 'Front Right' },
    { key: 'front_left', label: 'Front Left' },
    { key: 'rear_right', label: 'Rear Right' },
    { key: 'rear_left', label: 'Rear Left' },
    { key: 'hood', label: 'Hood' }
  ];
  let isLoading = false;
  let errorMessage = '';

  let captureIntervalId = null;
  const CAPTURE_INTERVAL_DURATION_MS = 500;


  let debugScreenshotUrl = '';

  // --- Screen Capture API related variables ---
  let mediaStream = null;
  let videoElement = null;

  // --- Cropping Configuration ---
  const CROP_TO_CENTER = true; // Set to true to enable center cropping
  const CROP_PERCENTAGE_OF_SMALLER_DIM = 0.8; // e.g., crop to 80% of the smaller dimension (width/height) of the capture

  async function startScreenCapture() {
    errorMessage = '';
    debugScreenshotUrl = '';
    if (mediaStream) {
      stopScreenCapture();
    }

    try {
      mediaStream = await navigator.mediaDevices.getDisplayMedia({
        video: {
          cursor: "never"
        },
        audio: false
      });

      videoElement = document.createElement('video');
      videoElement.autoplay = true;
      videoElement.srcObject = mediaStream;
      videoElement.style.display = 'none'; // Keep it off-screen
      document.body.appendChild(videoElement); // Needs to be in DOM

      await new Promise((resolve, reject) => {
        videoElement.onloadedmetadata = () => {
          videoElement.play().then(resolve).catch(reject);
        };
        videoElement.onerror = reject;
      });

      console.log('Screen capture started. Video dimensions:', videoElement.videoWidth, videoElement.videoHeight);
      startPeriodicFrameGrab();

      mediaStream.getVideoTracks()[0].onended = () => {
        console.log('Screen capture ended by user or browser.');
        stopScreenCapture();
        errorMessage = 'Screen capture was stopped. Click "Start Capture" to begin again.';
      };

    } catch (err) {
      console.error("Error starting screen capture:", err);
      errorMessage = `Failed to start screen capture: ${err.message}. Please grant permission and select a screen/tab.`;
      if (err.name === "NotFoundError" || err.name === "NotAllowedError") {
           errorMessage = "Screen capture permission denied or no screen selected. Please try again and grant permission.";
      }
      stopScreenCapture();
    }
  }

  function stopScreenCapture() {
    if (captureIntervalId) {
      clearInterval(captureIntervalId);
      captureIntervalId = null;
    }
    if (mediaStream) {
      mediaStream.getTracks().forEach(track => track.stop());
      mediaStream = null;
    }
    if (videoElement && videoElement.parentNode) {
      videoElement.srcObject = null;
      videoElement.parentNode.removeChild(videoElement); // Remove from DOM
      videoElement = null;
    }
    console.log('Screen capture stopped and cleaned up.');
  }

  async function grabFrameAndFetch() {
    if (isLoading || !mediaStream || !videoElement || videoElement.readyState < videoElement.HAVE_METADATA || videoElement.videoWidth === 0) {
      return;
    }

    isLoading = true;
    errorMessage = '';

    try {
      const captureCanvas = document.createElement('canvas');
      const ctx = captureCanvas.getContext('2d');

      const videoWidth = videoElement.videoWidth;
      const videoHeight = videoElement.videoHeight;

      let sx = 0; // Source X
      let sy = 0; // Source Y
      let sWidth = videoWidth; // Source Width
      let sHeight = videoHeight; // Source Height
      let canvasOutputWidth = videoWidth;
      let canvasOutputHeight = videoHeight;

      if (CROP_TO_CENTER) {
        const smallerDim = Math.min(videoWidth, videoHeight);
        const cropSize = Math.floor(smallerDim * CROP_PERCENTAGE_OF_SMALLER_DIM); // Use floor for whole pixels

        // For a square crop from the center
        sWidth = cropSize;
        sHeight = cropSize;
        canvasOutputWidth = cropSize;
        canvasOutputHeight = cropSize;

        sx = Math.floor((videoWidth - sWidth) / 2);
        sy = Math.floor((videoHeight - sHeight) / 2) + 150;
      }

      captureCanvas.width = canvasOutputWidth;
      captureCanvas.height = canvasOutputHeight;

      // Draw the cropped portion of the video onto the canvas
      ctx.drawImage(videoElement, sx, sy, sWidth, sHeight, 0, 0, canvasOutputWidth, canvasOutputHeight);

      debugScreenshotUrl = captureCanvas.toDataURL('image/png');

      const blob = await new Promise(resolve => captureCanvas.toBlob(resolve, 'image/png'));

      if (!blob) {
        throw new Error('Failed to convert captured frame to Blob.');
      }

      const formData = new FormData();
      formData.append('image', blob, 'screen_capture_frame.png');

      const response = await fetch('http://127.0.0.1:8081/api/v1/classifier/predict', {
        method: 'POST',
        headers: { 'accept': 'application/json' },
        body: formData,
      });

      if (!response.ok) {
        let errorDetails = '';
        try { errorDetails = await response.text(); } catch (e) { /* Ignore */ }
        throw new Error(`API Error: ${response.status} ${response.statusText}. ${errorDetails}`);
      }

      const data = await response.json();
      carPartsData = data;

    } catch (error) {
      console.error('Frame Grab and Fetch Error:', error);
      errorMessage = `Error during frame processing: ${error.message}`;
    } finally {
      isLoading = false;
    }
  }

  function startPeriodicFrameGrab() {
    if (captureIntervalId) clearInterval(captureIntervalId);
    if (mediaStream && videoElement) {
        grabFrameAndFetch();
        captureIntervalId = setInterval(grabFrameAndFetch, CAPTURE_INTERVAL_DURATION_MS);
        console.log('Periodic frame grabbing started.');
    } else {
        console.warn('Cannot start periodic frame grab: screen capture not active.');
        errorMessage = 'Screen capture is not active. Click "Start Capture".';
    }
  }

  onMount(() => {
    document.title = "Car State Components Classifier App"
  });

  onDestroy(() => {
    stopScreenCapture();
  });

</script>

<main>
  <h1>🚘 Car State Components Classifier using model architecture from EfficientNet-B3 </h1>
  <p style="text-align: center; margin-bottom: 2rem;">
    The app predicts and identifies the immediate change in a car component's state (e.g., Front Left Door Open/Close, Hood Open/Close)
    triggered by a button interaction or component click from <a href="https://euphonious-concha-ab5c5d.netlify.app/" target="_blank"> https://euphonious-concha-ab5c5d.netlify.app/ </a>
  </p>

  <div style="text-align: center; margin-bottom: 1.5rem;" >
    {#if !mediaStream}
      <button on:click={startScreenCapture} style="padding: 10px 20px; font-size: 16px; cursor: pointer;" class="action-button">
        Start Screen Capture
      </button>
    {:else}
      <button on:click={stopScreenCapture} style="padding: 10px 20px; font-size: 16px; cursor: pointer; background-color: #dc3545; color: white;">
        Stop Screen Capture
      </button>
    {/if}
  </div>

  {#if debugScreenshotUrl}
    <div class="debug-screenshot-container">
      <h4>Debug View (Cropped Captured Frame):</h4>
      <img src="{debugScreenshotUrl}" alt="Debug Screenshot" class="debug-image" />
    </div>
  {/if}

  {#if Object.keys(carPartsData).length > 0}
    <div class="status-container">
      <h2>Car Status Results</h2>
      <ul>
        {#each displayOrder as part}
          {@const statusDetail = carPartsData[part.key]}
          {#if statusDetail}
            <li>
              <span>{part.label}</span>
              <span
                class="status-badge"
                class:open={statusDetail.state && statusDetail.state.toLowerCase() === 'open'}
                class:closed={statusDetail.state && statusDetail.state.toLowerCase() === 'closed'}
              >
                {statusDetail.state || 'N/A'}
              </span>
            </li>
          {:else}
             <li>
              <span>{part.label}</span>
              <span class="status-badge unknown">Not Found</span>
            </li>
          {/if}
        {/each}
      </ul>
    </div>
  {/if}

  {#if mediaStream && captureIntervalId && !isLoading }
    <p class="info-message">
      ℹ️ Capturing frames every {CAPTURE_INTERVAL_DURATION_MS / 1000} second(s). Ensure this tab is selected for capture.
    </p>
  {:else if isLoading}
     <p class="info-message">
      <span class="spinner" style="border-color: #004085; border-top-color: transparent; display: inline-block; vertical-align: middle; margin-right: 5px;"></span>
      Processing frame...
    </p>
  {/if}

  {#if errorMessage}
    <p class="error-message">⚠️ {errorMessage}</p>
  {/if}

</main>