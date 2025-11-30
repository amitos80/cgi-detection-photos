# Use an official Node.js runtime as a parent image
FROM node:18-alpine

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json to the working directory
COPY package*.json ./

# Install app dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the TypeScript code
RUN npm run build

# Verify build output directory
RUN ls -l /app/dist

# Install Nginx and clean up apt cache
RUN apk update && apk add --no-cache nginx && nginx -t

# Create Nginx log directory and set permissions
RUN mkdir -p /var/log/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    mkdir -p /etc/nginx/conf.d && \
    chown -R nginx:nginx /etc/nginx/conf.d

# Copy the Nginx configuration file
COPY ../original_backend_files/nginx.conf .

# Expose port 8000
EXPOSE 8000

# Start Nginx in the foreground
CMD ["nginx", "-c", "/app/nginx.conf", "-g", "daemon off;"]