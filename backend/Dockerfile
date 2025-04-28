# FROM mcr.microsoft.com/playwright/python:v1.51.0-noble-arm64
FROM mcr.microsoft.com/playwright/python:v1.51.0-noble-amd64

WORKDIR /app

# Install Java 11
# RUN apt-get update && \
#     apt-get install -y openjdk-11-jdk && \
#     ln -s /usr/lib/jvm/java-11-openjdk-* /usr/lib/jvm/java-11-openjdk-amd64

# # Set JAVA_HOME for all shells + Python
# ENV JAVA_HOME="/usr/lib/jvm/java-11-openjdk-amd64"
# ENV PATH="$JAVA_HOME/bin:$PATH"

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN playwright install

EXPOSE 5050

# CMD ["flask", "run", "--host=0.0.0.0"]
CMD ["gunicorn", "-b", "0.0.0.0:5050", "app:app"]