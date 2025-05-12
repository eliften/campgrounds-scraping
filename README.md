# Web-Scrape Case Study

## Overview
Develop a scraper to extract all campground locations across the United States from The Dyrt https://thedyrt.com/search by leveraging their map interface which exposes latitude/longitude data through API requests when the mouse moves. You're free to use any library you want (requests, httpx, selenium, playwright)
For questions please connect us via email at info@smart-maple.com

**Hint:** Look for a search endpoint in the network tab!

## Core Requirements
- We provided a Docker compose file, you need to connect to PostgreSQL, create the necessary fields/tables (15p)
- Scrape all campground data from the US map interface and store it in the database (30p)
- Validate the data with pydantic, you can check the necessary fields from src/models/campground.py (these fields are the required fields to store in the db) (15p)
- Scheduling: Cron-like scheduling for regular updates (15p)
- Update: update existing records if they exist. (10p)
- Error handling: handle errors in your code, especially HTTP errors, aand add retries if necessary (15p)

## Bonus
- Database: Use an ORM for PostgreSQL operations
- Logging: Comprehensive logging system
- API Endpoint: Flask/FastAPI endpoint to trigger/control scraper 
  (Hint: you can implement this in an async fashion)
- Performance: Multithreading/async implementation
- Find address from lat/long field
- Feel free to use your creativity every additional field is appreciated



Proje Kurulumu ve Kullanımı
Bu proje, bir web scraping uygulamasıdır ve PostgreSQL veritabanı ile etkileşime geçer. Aşağıda, projeyi kurmak ve çalıştırmak için gerekli adımlar bulunmaktadır.

Gereksinimler
Docker

Docker Compose

Kurulum Adımları
1. Proje dosyalarını alın
Proje dosyalarını bilgisayarınıza indirin veya mevcut bir dizinde çalıştırın.

2. Docker ve Docker Compose ile Çalıştırma
Adım 1: Docker ve Docker Compose'ı kullanarak servisleri başlatın
Projenin kök dizininde, aşağıdaki komutu çalıştırarak gerekli servisleri başlatın:

docker-compose up --build
Bu komut, Dockerfile kullanarak scraper servisini oluşturacak ve ardından PostgreSQL veritabanını içeren postgres servisini başlatacaktır. scraper servisi, PostgreSQL veritabanına bağlanarak verileri işleyecektir.

Adım 2: Servislerin durumu
Docker Compose komutunu çalıştırdıktan sonra, aşağıdaki komutla tüm servislerin durumunu kontrol edebilirsiniz:

docker-compose ps

4. Proje Çalıştırma
Uygulama, scraper servisi olarak çalışacak ve belirtilen port olan 5000 üzerinden erişilebilir olacaktır.

PostgreSQL veritabanı, 5432 portu üzerinden erişilebilir.

5. Çevresel Değişkenler
DB_URL: Veritabanına bağlantı URL'si. Bu, docker-compose.yml dosyasında tanımlanan bağlantıyı kullanır.

DB_URL=postgresql://postgres:112233@postgres:5432/campgrounds

6. Çalışma Dizini
Proje çalışma dizini /src olarak ayarlanmıştır. Uygulama dosyalarınız bu dizine kopyalanacak ve burada çalıştırılacaktır.

7. Uygulama Başlatma
Uygulamanın çalışmasını başlatmak için, Docker Compose hizmetleri başlatıldıktan sonra şu komutla uygulama başlatılır:

docker-compose up
Eğer her şey doğru yapılandırılmışsa, uygulama çalışmaya başlayacak ve istenilen veritabanı bağlantısı sağlanacaktır.