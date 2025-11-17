# Development Plan: Analysis Report Feature

**Analysis:**

The goal is to enhance the user experience by providing a detailed, visually intuitive report after an image analysis is complete. The current implementation only provides a final prediction and a single confidence score, which lacks the depth required for a comprehensive report.

To build this feature, the backend Python service must be updated to provide a more granular breakdown of its analysis. The current forensic engine already calculates individual scores for ELA, CFA, and HOS, so the foundation is already in place. We will expose this data and add context, such as a "normal range" for each metric.

On the frontend, we will implement both of the user's requests: a clear, easy-to-read table that explains the insights, and a simple, lightweight graphical representation (infographic) for each metric. This will be achieved using styled HTML elements to avoid introducing heavy charting libraries, ensuring the application remains fast and lean.

**Plan:**

1.  **Update the Python AI Microservice (`cgi-detector-service/forensics/engine.py`):**
    *   The `run_analysis` function already calculates individual scores. This step will focus on enriching the `analysis_breakdown` it returns.
    *   For each metric (ELA, CFA, HOS), a `normal_range` key will be defined. This will be a two-element array (e.g., `[0.0, 0.3]`) representing the typical score range for a "real" photograph.
    *   An `insight` key will also be added, providing a brief, user-friendly explanation of what that specific forensic test measures.
    *   The final JSON response structure passed through `main.py` will now contain all the necessary data for the frontend to build the report.

2.  **Enhance the Frontend (`webservice/static/index.html`):**
    *   Add a new container element to the HTML, `<div id="report"></div>`, which will hold the detailed analysis report.
    *   Update the CSS to style the new report elements, including the table and the infographic bars.
    *   In the JavaScript `submit` event listener, after receiving a successful response, the code will parse the `analysis_breakdown` array from the JSON.
    *   **Table Display:** The script will dynamically generate an HTML `<table>`. It will iterate through the `analysis_breakdown` data and create a row for each forensic test, with columns for "Feature," "Calculated Score," and "Insight."
    *   **Infographic Display:** For each feature, the script will also generate a simple graphical bar using styled `<div>` elements:
        *   A main container `div` will act as the background bar, representing the full range (0.0 to 1.0).
        *   An inner `div` will be positioned and sized to represent the `normal_range`, styled as a shaded background area.
        *   A separate marker `div` (e.g., a vertical line or a dot) will be positioned using the `score` to visually indicate the calculated value in relation to the normal range.

3.  **Update Documentation:**
    *   Update the main `README.md` to include a description of the new detailed analysis report feature.
    *   Update the "API Response Structure" section in the `README.md` to reflect the new, richer `analysis_breakdown` object in the JSON response.