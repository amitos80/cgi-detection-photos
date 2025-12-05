FROM python:3.10-slim-bullseye

WORKDIR /app

# Install necessary libraries for OpenCV
RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
    libgl1-mesa-glx \
    libsm6 \
    libxext6 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]