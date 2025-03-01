FROM apache/airflow:2.10.2

USER root

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget unzip build-essential libsndfile1 libopenmpi-dev \
    libnss3 libgconf-2-4 libxi6 libgbm1 libxrandr2 \
    libasound2 libatk1.0-0 libpangocairo-1.0-0 \
    libx11-xcb1 libxcomposite1 libxcursor1 libxdamage1 \
    libxfixes3 libpangoft2-1.0-0 \
    ca-certificates fonts-liberation \
    libappindicator3-1 xdg-utils curl gnupg \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Add Google Chrome’s official repository (fixed method)
RUN curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | tee /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver (matching Chrome version 133.0.6943.126)
ENV CHROMEDRIVER_VERSION=133.0.6943.126
RUN wget -q "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip" \
    && unzip chromedriver-linux64.zip \
    && mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver \
    && chmod +x /usr/local/bin/chromedriver \
    && rm -rf chromedriver-linux64.zip chromedriver-linux64

# Switch back to airflow user
USER airflow

# Copy and install Python dependencies
COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt







# FROM apache/airflow:2.10.2
# USER root
# RUN apt-get update && apt-get install -y --no-install-recommends wget unzip build-essential libsndfile1 libopenmpi-dev && apt-get autoremove -yqq --purge && apt-get clean && rm -rf /var/lib/apt/lists/*
# RUN apt-get autoremove -yqq --purge \
#     && apt-get clean \
#     && rm -rf /var/lib/apt/lists/*
# RUN apt-get install wget

# COPY requirements.txt /

# USER airflow
# RUN pip install --no-cache-dir -r /requirements.txt