document.getElementById("apkForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const fileInput = document.getElementById("apkFile");
  const resultDiv = document.getElementById("apkResult"); 

  if (!fileInput.files[0]) {
    resultDiv.style.display = "block";
    resultDiv.innerHTML = `<div class="alert alert-danger">Please select an APK file.</div>`;
    return;
  }

  const file = fileInput.files[0];
  const fileName = file.name;
  // Extension check
  if (!fileName.toLowerCase().endsWith('.apk')) {
    alert('Please upload a valid .apk file.');
    return;
  }

  // Hex signature check (ZIP: 50 4B 03 04)
  const arrayBuffer = await file.slice(0, 4).arrayBuffer();
  const uint8 = new Uint8Array(arrayBuffer);
  if (!(uint8[0] === 0x50 && uint8[1] === 0x4B && uint8[2] === 0x03 && uint8[3] === 0x04)) {
    alert('The file does not appear to be a valid APK (ZIP signature missing).');
    return;
  }

  // Show loading state
  resultDiv.style.display = "block";
  resultDiv.innerHTML = `
    <div class="alert alert-info">
      <div class="spinner-border spinner-border-sm me-2" role="status"></div>
      Analyzing APK... This may take a few minutes.
    </div>`;

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch("http://localhost:5000/analyze", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();

    // Show results with better formatting
    // Check if this is a direct Docker response (has 'status' field) or wrapped response (has 'success' field)
    if (data.status || data.safe !== undefined) {
      // Direct Docker service response - format based on safety
      const isSafe = data.safe || data.status === 'safe';
      const alertClass = isSafe ? 'alert-success' : 'alert-danger';
      const icon = isSafe ? '✅' : '⚠️';
      const title = isSafe ? 'APK Analysis Complete - Safe' : 'APK Analysis Complete - Threat Detected';
      
      resultDiv.innerHTML = `
        <div class="alert ${alertClass}">
          <h5>${icon} ${title}</h5>
          <p><strong>Status:</strong> ${data.status || (data.safe ? 'safe' : 'unsafe')}</p>
          <p><strong>Threat Level:</strong> ${data.threat_level || 'unknown'}</p>
          <p><strong>Confidence:</strong> ${data.confidence || 'N/A'}%</p>
          <p><strong>Message:</strong> ${data.message || 'No message'}</p>
          ${data.analysis && data.analysis.suspicious_permissions ? 
            `<p><strong>Suspicious Permissions:</strong> ${data.analysis.suspicious_permissions.join(', ')}</p>` : ''}
          <details>
            <summary>View Full Analysis</summary>
            <pre class="mt-2">${JSON.stringify(data, null, 2)}</pre>
          </details>
        </div>`;
    } else if (data.success) {
      // Wrapped response format
      resultDiv.innerHTML = `
        <div class="alert alert-success">
          <h5>✅ Analysis Complete</h5>
          <p><strong>File:</strong> ${data.filename || 'Unknown'}</p>
          <details> 
            <summary>View Full Response</summary>
            <pre class="mt-2">${JSON.stringify(data, null, 2)}</pre>
          </details>
        </div>`;
    } else {
      // Error response format
      resultDiv.innerHTML = `
        <div class="alert alert-danger">
          <h5>❌ Analysis Failed</h5>
          <p><strong>Error:</strong> ${data.error || 'Unknown error'}</p>
          <details>
            <summary>View Details</summary>
            <pre class="mt-2">${JSON.stringify(data, null, 2)}</pre>
          </details>
        </div>`;
    }
  } catch (err) {
    resultDiv.innerHTML = `
      <div class="alert alert-danger">
        <h5>❌ Connection Error</h5>
        <p>Could not connect to the backend server.</p>
        <p><small>Error: ${err.message}</small></p>
        <p><small>Make sure the backend is running on http://localhost:5000</small></p>
      </div>`;
  }
});

// Test backend connection
document.getElementById("testBackend").addEventListener("click", async () => {
  const resultDiv = document.getElementById("apkResult");
  
  resultDiv.style.display = "block";
  resultDiv.innerHTML = `
    <div class="alert alert-info">
      <div class="spinner-border spinner-border-sm me-2" role="status"></div>
      Testing backend connection...
    </div>`;

  try {
    // First check if we have a health endpoint
    let res;
    try {
      res = await fetch("http://localhost:5000/health");
    } catch (healthErr) {
      // If no health endpoint, try a simple GET to root
      res = await fetch("http://localhost:5000/");
    }
    
    if (res.ok) {
      const text = await res.text();
      let data;
      try {
        data = JSON.parse(text);
      } catch {
        data = text;
      }
      
      resultDiv.innerHTML = `
        <div class="alert alert-success">
          <h5>✅ Backend is Running</h5>
          <p>Successfully connected to http://localhost:5000</p>
          <details>
            <summary>Response</summary>
            <pre class="mt-2">${typeof data === 'string' ? data : JSON.stringify(data, null, 2)}</pre>
          </details>
        </div>`;
    } else {
      resultDiv.innerHTML = `
        <div class="alert alert-warning">
          <h5>⚠️ Backend Responded with Error</h5>
          <p>Status: ${res.status} ${res.statusText}</p>
        </div>`;
    }
  } catch (err) {
    resultDiv.innerHTML = `
      <div class="alert alert-danger">
        <h5>❌ Backend Not Reachable</h5>
        <p>Could not connect to http://localhost:5000</p>
        <p><small>Error: ${err.message}</small></p>
        <p><small><strong>Make sure:</strong></small></p>
        <ul class="small">
          <li>Backend server is running (python restapi.py)</li>
          <li>Backend is listening on port 5000</li>
          <li>No firewall blocking the connection</li>
        </ul>
      </div>`;
  }
});
