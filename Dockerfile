FROM python:3.11-slim

# Sistem paketlerini ve geliştirme araçlarını yükleyin
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    libpq-dev \
    gcc \
    g++ \
    make \
    libxml2-dev

# Google Chrome için anahtar ekleme
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list
RUN apt-get update && apt-get install -y google-chrome-stable

# set display port to avoid crash
ENV DISPLAY=:99

RUN pip install --upgrade pip
# Python bağımlılıkları
COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt

# Çalışma dizini ve uygulama
WORKDIR /src
COPY . .

# Başlat
CMD ["python3", "main.py"]
