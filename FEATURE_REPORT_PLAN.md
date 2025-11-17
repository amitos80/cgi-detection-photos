# Development Plan: Analysis Report Feature

**Analysis:**

The goal is to display a detailed report after image analysis, including a graphical representation of the findings. The current model provides a single confidence score, which is insufficient for a detailed infographic with "calculated" vs. "normal" values.

To address this, the plan will simulate a more advanced analysis on the backend. The Python service will be updated to return a fictional breakdown of analysis metrics. The frontend will then be enhanced to display this information in two ways: a clear, easy-to-read table and a simple, lightweight graphical representation using styled HTML elements to mimic an infographic, thus avoiding the need for heavy charting libraries.

**Plan:**

1.  **Update the Python AI Microservice (`cgi-detector-service/main.py`):**
    *   Modify the `/predict` endpoint to include a new key, `analysis_breakdown`, in its JSON response.
    *   This key will contain an array of objects, where each object represents a fictional analysis metric.
    *   Each metric object will have the following structure: `{"feature": "Metric Name", "score": 0.0-1.0, "normal_range": [min, max], "insight": "Brief explanation."}`.
    *   The data for this breakdown will be hardcoded for now, changing based on the dummy "cgi" or "real" prediction to simulate a real analysis.

2.  **Enhance the Frontend (`webservice/static/index.html`):**
    *   Add a new container element to the HTML to hold the analysis report.
    *   In the JavaScript `submit` event listener, after receiving a successful response, parse the `analysis_breakdown` array.
    *   **Table Display:** Dynamically generate an HTML table from the `analysis_breakdown` data. The table will have columns for "Feature," "Calculated Score," and "Insight."
    *   **Infographic Display:** For each feature in the breakdown, create a simple graphical bar. This will be implemented using styled `<div>` elements:
        *   A container `div` will represent the full 0.0 to 1.0 range.
        *   An inner `div` will represent the `normal_range`, styled as a shaded background area.
        *   Another inner `div` or marker will be positioned based on the `score`, visually showing where the calculated value falls in relation to the normal range.

3.  **Update Node.js Webservice (`webservice/src/index.ts`):**
    *   No changes are required. The service already relays the full JSON response from the Python service, so the new `analysis_breakdown` data will be passed through automatically.

4.  **Update Documentation:**
    *   Briefly update the main `README.md` to mention the new analysis report feature in the project description.
