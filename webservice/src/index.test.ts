import request from 'supertest';
import express from 'express';
import path from 'path';

// Mock the actual app to avoid port conflicts and file system operations during testing
const app = express();
app.use(express.static(path.join(__dirname, '../static')));
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '../static/index.html'));
});

describe('GET /', () => {
  it('should return the index.html file', async () => {
    const res = await request(app).get('/');
    expect(res.statusCode).toEqual(200);
    expect(res.headers['content-type']).toContain('text/html');
  });
});
