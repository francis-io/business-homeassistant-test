# Dockerfile for UI tests with Playwright browsers
FROM python:3.11-slim

# Install system dependencies for Playwright browsers
RUN apt-get update && apt-get install -y \
    # Basic utilities
    curl \
    wget \
    gnupg \
    # Required for Chromium and other browsers
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libatspi2.0-0 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    libgbm1 \
    libxkbcommon0 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libcairo-gobject2 \
    libasound2 \
    libgtk-3-0 \
    libgdk-pixbuf2.0-0 \
    libglib2.0-0 \
    # Additional X11 dependencies
    libxshmfence1 \
    # Clean up
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for running tests
RUN useradd -m -s /bin/bash testuser

# Switch to non-root user
USER testuser
WORKDIR /home/testuser

# Copy and install Python dependencies
COPY --chown=testuser:testuser tests/requirements.txt /tmp/requirements.txt
COPY --chown=testuser:testuser tests/ui/requirements.txt /tmp/ui-requirements.txt
RUN sed -i 's|-r ../requirements.txt|-r /tmp/requirements.txt|' /tmp/ui-requirements.txt && \
    pip install --user --no-cache-dir -r /tmp/ui-requirements.txt

# Install Playwright browsers
RUN python -m playwright install chromium firefox webkit

# Set up environment
ENV PATH="/home/testuser/.local/bin:${PATH}"
ENV PYTHONPATH="/workspace"

# Default command
CMD ["python", "-m", "pytest", "tests/ui", "-v"]
