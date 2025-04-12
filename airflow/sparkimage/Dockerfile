FROM bitnami/spark:latest

USER root

# Install necessary dependencies including unzip
RUN apt-get update --fix-missing && apt-get install -y --no-install-recommends \
    wget curl gnupg ca-certificates unzip && \
    # Add Google Chrome repository and install Chrome
    curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | tee /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update --fix-missing && apt-get install -y google-chrome-stable && \
    # Install ChromeDriver (matching Chrome version 133.0.6943.126)
    wget -q "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/135.0.7049.84/linux64/chromedriver-linux64.zip" && \
    unzip chromedriver-linux64.zip && \
    mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver && \
    # Clean up unnecessary files to keep the image smaller
    rm -rf chromedriver-linux64.zip chromedriver-linux64 /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Switch back to non-root user
USER 1001
