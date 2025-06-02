<script>
  import {onDestroy, onMount} from 'svelte';

  let selectedFile = null;
  let imagePreviewUrl = null;
  let caption = '';
  let isLoading = false;
  let error = null;
  let fileInput; // To bind to the input element

  // Function to trigger file input click
  function triggerFileInput() {
    if (isLoading) return; // Don't trigger if already processing
    fileInput.click();
  }

  async function handleFileSelect(event) {
    const files = event.target.files;

    // Revoke previous object URL if it exists
    if (imagePreviewUrl) {
      URL.revokeObjectURL(imagePreviewUrl);
      imagePreviewUrl = null;
    }

    if (files && files[0]) {
      selectedFile = files[0];
      imagePreviewUrl = URL.createObjectURL(selectedFile);
      caption = ''; // Reset caption for new image
      error = null;   // Reset error for new image
      await generateCaption(); // Automatically generate caption after selection
    } else {
      selectedFile = null;
      // imagePreviewUrl is already null or revoked
    }
  }

  async function generateCaption() {
    if (!selectedFile) {
      // This should ideally not be hit if generateCaption is only called after valid file selection
      error = 'No file selected to generate caption for.';
      return;
    }

    isLoading = true;
    error = null; // Clear previous errors
    // caption is reset in handleFileSelect

    const formData = new FormData();
    // The API expects the field name to be 'image'
    formData.append('image', selectedFile, selectedFile.name);

    try {
      const response = await fetch('http://127.0.0.1:8081/api/v1/explainer/predict', {
        method: 'POST',
        headers: {
          'accept': 'application/json',
          // 'Content-Type': 'multipart/form-data' is automatically set by the browser with the correct boundary when using FormData.
        },
        body: formData,
      });

      if (!response.ok) {
        let errorDetail = response.statusText;
        try {
            const errorData = await response.json(); // Try to parse API's JSON error response
            errorDetail = errorData.detail || (typeof errorData === 'string' ? errorData : JSON.stringify(errorData));
        } catch (e) {
            // If parsing errorData as JSON fails (e.g., HTML error page), errorDetail remains response.statusText
        }
        throw new Error(`API Error: ${response.status} - ${errorDetail}`);
      }

      // The API is expected to return a JSON string like "heres the caption"
      const resultText = await response.json();
      caption = resultText;

    } catch (e) {
      console.error('Error generating caption:', e);
      error = e.message || 'Failed to generate caption. Please try again.';
      caption = ''; // Ensure caption is cleared on error
    } finally {
      isLoading = false;
    }
  }

  onMount(() => {
    document.title = "Car State Components Explainer App"
  });

  // Revoke the object URL when the component is destroyed to prevent memory leaks
  onDestroy(() => {
    if (imagePreviewUrl) {
      URL.revokeObjectURL(imagePreviewUrl);
    }
  });
</script>

<main>
  <div class="app-container">
      <h1>🚘 Car State Components Explainer </h1>
      <p style="text-align: center; margin-bottom: 2rem;">
        The app explains uploaded image using BLIP (Bootstrapping Language-Image Pre-training) fine tuned mnodel.
      </p>

    <input
      type="file"
      accept="image/*"
      on:change={handleFileSelect}
      bind:this={fileInput}
      style="display: none;"
      aria-hidden="true"
    />

    <button on:click={triggerFileInput} disabled={isLoading} class="action-button">
      {#if isLoading}
        Processing...
      {:else}
        Capture and Describe
      {/if}
    </button>

    {#if error}
      <p class="error-message">⚠️ {error}</p>
    {/if}

    {#if imagePreviewUrl}
      <div class="result-card">
        <img src={imagePreviewUrl} alt="Uploaded car preview" class="image-preview">
        {#if isLoading}
          <p class="caption-text loading-caption">Generating caption...</p>
        {:else if caption}
          <p class="caption-text">{caption}</p>
        {/if}
        </div>
    {/if}
  </div>
</main>

