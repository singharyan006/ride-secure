# RideSecure API — Frontend Integration Guide

This document shows minimal frontend examples for integrating a web frontend with the `src/api.py` FastAPI backend you added.

Base URL
--------

When running locally with Uvicorn:

http://127.0.0.1:8000

Endpoints used in examples
--------------------------
- `GET /health` — health check
- `GET /models?category=detection` — list available detection models
- `POST /predict/frame` — multipart file upload (image) to get detections

Notes
-----
- The example backend enables CORS for all origins by default. In production, restrict `allow_origins` to your frontend origin.
- The `/predict/frame` endpoint expects a multipart/form-data body with key `file` and optional fields `model` and `conf`.

JavaScript (Fetch) examples
---------------------------

1) Health check

```js
fetch('http://127.0.0.1:8000/health')
  .then(r => r.json())
  .then(j => console.log('health:', j))
  .catch(err => console.error('health-check failed', err));
```

2) List models

```js
async function listModels() {
  const res = await fetch('http://127.0.0.1:8000/models?category=detection');
  if (!res.ok) throw new Error('failed to get models');
  const json = await res.json();
  console.log('models:', json);
}

listModels();
```

3) Predict on a single image (file input)

```html
<input id="file" type="file" accept="image/*" />
<button id="send">Send</button>
<pre id="out"></pre>

<script>
document.getElementById('send').addEventListener('click', async () => {
  const finput = document.getElementById('file');
  if (!finput.files.length) return alert('pick a file');
  const file = finput.files[0];

  const fd = new FormData();
  fd.append('file', file);
  fd.append('model', 'custom_helmet'); // optional

  const resp = await fetch('http://127.0.0.1:8000/predict/frame', {
    method: 'POST',
    body: fd
  });

  if (!resp.ok) {
    const txt = await resp.text();
    document.getElementById('out').innerText = `Error: ${resp.status}\n${txt}`;
    return;
  }

  const json = await resp.json();
  document.getElementById('out').innerText = JSON.stringify(json, null, 2);
});
</script>
```

Handling detections on the frontend
-----------------------------------

The `/predict/frame` response includes a `detections` array with objects `{x1,y1,x2,y2,confidence,class_id,class_name}`. Use these to overlay bounding boxes on a `<canvas>` or `<img>` element (scale coordinates to your displayed image size).

Performance & UX tips
---------------------
- Debounce or throttle uploads when processing live camera frames (e.g., send one frame every 250-500ms).
- If doing real-time processing consider adding a small `POST /predict/frame-stream` or WebSocket endpoint to push frames and receive detections (can be added later).
- Show a spinner while waiting for response. Consider showing a lower-fidelity preview while the server processes.

Security
--------
- Restrict CORS to your frontend origin in production.
- Add authentication or API keys if the API will be publicly accessible.

Next integration steps you may want me to implement
--------------------------------------------------
1. Add a `POST /predict/video` endpoint that accepts a video upload and runs the full pipeline (longer-running job + status polling or WebSocket updates).
2. Add a WebSocket `/ws/progress` endpoint to stream processing progress/partial results to the frontend.
3. Add example React/Vue component that calls the API and overlays boxes on video.
4. Add a lightweight client-side worker to capture camera frames and POST at a capped rate.

Tell me which next step you want me to implement and I'll add it (I can implement the video upload endpoint + polling or a WebSocket progress endpoint next).
