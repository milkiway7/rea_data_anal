# Używamy lekkiego obrazu Pythona 3.12 bazującego na Debianie slim
FROM python:3.12-slim

# Ustawiamy katalog roboczy w kontenerze na /app
WORKDIR /app

# Kopiujemy plik requirements.txt do kontenera (zawiera listę pakietów Python)
COPY requirements.txt .

# Aktualizujemy listę pakietów i instalujemy potrzebne narzędzia i biblioteki systemowe,
# które są wymagane do kompilacji oraz do obsługi MSSQL (sterownik ODBC)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    gnupg \
    unixodbc-dev \
    libpq-dev \
    libssl-dev \
    libffi-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*  # Czyszczenie cache apt, by zmniejszyć rozmiar obrazu

# Dodajemy klucz Microsoft i repozytorium pakietów do instalacji sterownika ODBC do MSSQL
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Aktualizujemy pip do najnowszej wersji
RUN pip install --upgrade pip

# Instalujemy wszystkie wymagane paczki Pythona z requirements.txt
RUN pip install -r requirements.txt

# Kopiujemy plik .env do katalogu /app w kontenerze, aby aplikacja miała dostęp do zmiennych środowiskowych
COPY .env .

# Kopiujemy cały kod źródłowy do katalogu roboczego w kontenerze
COPY . .

# Ustawiamy zmienną środowiskową, aby Python nie buforował outputu (logi od razu pojawiają się w konsoli)
ENV PYTHONUNBUFFERED=1

# Komenda uruchamiająca FastAPI za pomocą uvicorn, nasłuchująca na wszystkich interfejsach i porcie 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
