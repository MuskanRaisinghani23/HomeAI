FROM apache/airflow:2.10.2

USER root

# Install only necessary dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget unzip curl gnupg openjdk-17-jdk \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME for Java 17
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

USER airflow

# Copy and install Python dependencies
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

