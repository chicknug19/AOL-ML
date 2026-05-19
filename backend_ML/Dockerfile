# Kita naikkan versinya dari 3.10 menjadi 3.11
FROM python:3.11-slim

# Menentukan folder kerja di dalam server
WORKDIR /app

# Mengopi file requirements dan menginstalnya
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Mengopi seluruh file backend kita ke server
COPY . .

# Hugging Face secara default mendengarkan di port 7860
EXPOSE 7860

# Menyalakan Flask menggunakan Gunicorn di port 7860
CMD ["gunicorn", "-b", "0.0.0.0:7860", "app:app"]