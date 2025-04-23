FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

ENV SCICAT_BASE_URL="https://public-data-dev.desy.de/api/v3"
ENV HIFIS_BASE_URL="https://hifis-storage.desy.de:2880"

CMD ["python", "app.py"]
