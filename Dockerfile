FROM python:latest

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y \
    libgconf2-4 libnss3-1d libxss1 \
    fonts-liberation libappindicator3-1 xdg-utils \
    software-properties-common \
    curl unzip wget \
    libasound2 \
    xvfb


RUN CHROMEDRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE` && \
    wget https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip
RUN unzip chromedriver_linux64.zip -d /usr/bin
RUN chmod +x /usr/bin/chromedriver

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get update
RUN apt-get install -y google-chrome-stable


COPY test/test_requirements.txt ./test/
RUN pip install --no-cache-dir -r test/test_requirements.txt

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "app:app", "-b", "0.0.0.0:5000"]