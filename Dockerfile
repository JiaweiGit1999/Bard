# Use a lightweight base image
FROM python:3.11-slim

# Install system packages (ffmpeg, etc.)
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean

# Set working directory
WORKDIR /app

# Copy everything
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables (optional)
ENV PYTHONUNBUFFERED=1

# Run your bot
CMD ["python", "bot.py"]

ENV FFMPEG_PATH=/usr/bin/ffmpeg
