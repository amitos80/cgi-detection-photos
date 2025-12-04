import express, { type Request, type Response } from 'express';
import path from 'path';
import multer from 'multer';
import fs from 'fs/promises';
import fetch from 'node-fetch';
import FormData from 'form-data';
import { fileURLToPath } from 'url';

const app = express();
const port = process.env.PORT || 8000;

// ES Module equivalent of __dirname
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configure multer for file uploads
const upload = multer({ dest: path.join(__dirname, 'temp'), limits: { fieldSize: 10 * 1024 * 1024 } }); // Temp directory within webservice container

// Ensure temp directory exists
const tempDir = path.join(__dirname, 'temp');
fs.mkdir(tempDir, { recursive: true }).catch(console.error);

// Serve static files from the React build output directory
app.use(express.static(path.join(__dirname, '..')));

// Serve the React app's index.html for all routes
app.get('*', (_req: Request, res: Response) => {
  res.sendFile(path.join(__dirname, '..', 'index.html'));
});

app.post('/analyze', upload.array('files'), async (req: Request, res: Response) => {
  if (!req.files || (req.files as Express.Multer.File[]).length === 0) {
    return res.status(400).json({ error: 'No files uploaded.' });
  }

  const uploadedFiles = req.files as Express.Multer.File[];

  try {
    const form = new FormData();
    for (const file of uploadedFiles) {
      const imageBuffer = await fs.readFile(file.path);
      form.append('files', imageBuffer, {
        filename: file.originalname,
        contentType: file.mimetype,
      });
    }

    // Forward the images to the Python AI microservice
    const pythonServiceUrl = process.env.PYTHON_SERVICE_URL || 'http://cgi-detector-service:8000/analyze';
    const response = await fetch(pythonServiceUrl, {
      method: 'POST',
      body: form,
      headers: form.getHeaders(),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Python service error: ${response.status} - ${errorText}`);
    }

    const predictionResult = await response.json();
    res.json(predictionResult);

  } catch (e: unknown) {
    let errorMessage = 'Processing failed';
    if (e instanceof Error) {
      errorMessage = e.message;
    }
    console.error('Processing failed:', e);
    res.status(500).json({ error: errorMessage, details: errorMessage });
  } finally {
    // Clean up all temporary files
    for (const file of uploadedFiles) {
      await fs.unlink(file.path).catch(console.error);
    }
  }
});

app.post('/report', upload.single('file'), async (req: Request, res: Response) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No file uploaded for report.' });
  }

  const filePath = req.file.path;
  const userCorrection = req.body.userCorrection;
  const originalPrediction = req.body.originalPrediction;

  try {
    const imageBuffer = await fs.readFile(filePath);

    const form = new FormData();
    form.append('file', imageBuffer, {
      filename: req.file.originalname,
      contentType: req.file.mimetype,
    });
    form.append('userCorrection', userCorrection);
    form.append('originalPrediction', originalPrediction);

    const pythonServiceUrl = process.env.PYTHON_SERVICE_URL_FEEDBACK || 'http://cgi-detector-service:8000/report';
    const response = await fetch(pythonServiceUrl, {
      method: 'POST',
      body: form,
      headers: form.getHeaders(),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Python service feedback error: ${response.status} - ${errorText}`);
    }

    const feedbackResult = await response.json();
    res.json({ message: 'Report submitted successfully', feedback: feedbackResult });

  } catch (e: unknown) {
    let errorMessage = 'Failed to submit report';
    if (e instanceof Error) {
      errorMessage = e.message;
    }
    console.error('Reporting failed:', e);
    res.status(500).json({ error: errorMessage, details: errorMessage });
  } finally {
    await fs.unlink(filePath).catch(console.error);
  }
});


app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});