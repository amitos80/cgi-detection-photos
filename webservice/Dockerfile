
# Stage 1: Build the React frontend
FROM node:20-alpine as builder

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build && npx tsc -p tsconfig.server.json

# Stage 2: Serve the React application with Node.js Express server
FROM node:20-alpine

WORKDIR /app

# Copy built React app from builder stage
COPY --from=builder /app/dist ./dist

# Copy backend server files (package.json, etc.) and compiled index.js
COPY package*.json ./
COPY tsconfig*.json ./
COPY --from=builder /app/dist/server/index.js ./dist/server/index.js

RUN npm install --omit=dev

EXPOSE 8000

CMD ["node", "./dist/server/index.js"]
