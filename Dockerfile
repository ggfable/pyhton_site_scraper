FROM python:3.10-slim-buster

WORKDIR /var/www/scraper/app

RUN apt-get update && \
    apt-get install -y wget gnupg2 unzip curl procps && \
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list && \
    apt update && \
    apt install -y google-chrome-stable

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

RUN CHROME_DRIVER_VERSION=127.0.6533.72 && \
    # CHROME_DRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
    # curl -sS -o /tmp/chromedriver_linux64.zip http://chromedriver.storage.googleapis.com/${CHROME_DRIVER_VERSION}/chromedriver_linux64.zip && \
    # https://googlechromelabs.github.io/chrome-for-testing/#stable
    # curl -sS -o /tmp/chromedriver-linux64.zip https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/123.0.6312.58/linux64/chromedriver-linux64.zip && \
    curl -sS -o /tmp/chromedriver-linux64.zip https://storage.googleapis.com/chrome-for-testing-public/127.0.6533.72/linux64/chromedriver-linux64.zip && \
    unzip /tmp/chromedriver-linux64.zip -d /tmp && cd /tmp/chromedriver-linux64 && cp chromedriver /usr/local/bin && \
    ls /usr/local/bin && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -Rf /tmp/chromedriver-linux64

COPY ./app .

EXPOSE 8123