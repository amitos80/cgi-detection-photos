import express from 'express';
import path from 'path';
import multer from 'multer';
import sharp from 'sharp';
import { v4 as uuidv4 } from 'uuid';
import fs from 'fs/promises';

const app = express();
const port = process.env.PORT || 8000;

// Configure multer for file uploads
const upload = multer({ dest: path.join(__dirname, '../temp') });

// Ensure temp directory exists
const tempDir = path.join(__dirname, '../temp');
fs.mkdir(tempDir, { recursive: true }).catch(console.error);

// Serve static files from the 'static' directory
app.use(express.static(path.join(__dirname, '../static')));

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '../static/index.html'));
});

/**
 * Decodes an image buffer and computes a simple feature vector.
 * - per-channel mean and standard deviation (R,G,B) -> 6 values
 * - per-channel histogram with 16 bins each -> 48 values
 * Total -> 54 floats
 * @param imageBuffer The buffer of the image to process.
 * @returns A promise that resolves to a list of 54 floats representing the feature vector.
 */
async function processImageBuffer(imageBuffer: Buffer): Promise<number[]> {
  const image = sharp(imageBuffer);
  const metadata = await image.metadata();

  if (!metadata.width || !metadata.height) {
    throw new Error('Could not get image dimensions.');
  }

  // Ensure image is 3-channel sRGB to standardize input
  const { data, info } = await image.removeAlpha().toColourspace('srgb').raw().toBuffer({ resolveWithObject: true });

  const features: number[] = [];

  // Calculate per-channel mean and standard deviation
  const channelData: number[][] = Array.from({ length: info.channels }, () => []);
  for (let i = 0; i < data.length; i += info.channels) {
    for (let c = 0; c < info.channels; c++) {
      channelData[c].push(data[i + c] / 255.0); // Normalize to 0-1
    }
  }

  for (let c = 0; c < info.channels; c++) {
    const sum = channelData[c].reduce((acc, val) => acc + val, 0);
    const mean = sum / channelData[c].length;
    const variance = channelData[c].reduce((acc, val) => acc + Math.pow(val - mean, 2), 0) / channelData[c].length;
    const std = Math.sqrt(variance);
    features.push(mean, std);
  }

  // Calculate per-channel histograms (16 bins)
  const histBins = 16;
  for (let c = 0; c < info.channels; c++) {
    const histogram = new Array(histBins).fill(0);
    for (let i = 0; i < data.length; i += info.channels) {
      const bin = Math.floor((data[i + c] / 256) * histBins);
      histogram[bin]++;
    }
    const total = histogram.reduce((acc, val) => acc + val, 0);
    features.push(...histogram.map(val => total > 0 ? val / total : 0));
  }

  return features;
}

app.post('/analyze', upload.single('file'), async (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No file uploaded.' });
  }

  const filePath = req.file.path;
  try {
    const imageBuffer = await fs.readFile(filePath);
    const featureVector = await processImageBuffer(imageBuffer);

    res.json({ filename: req.file.originalname, feature_vector: featureVector });
  } catch (e: any) {
    console.error('Processing failed:', e);
    res.status(500).json({ error: 'Processing failed', details: e.message });
  } finally {
    // Clean up the temporary file
    await fs.unlink(filePath).catch(console.error);
  }
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});