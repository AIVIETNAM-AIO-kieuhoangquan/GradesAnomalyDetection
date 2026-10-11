FROM python:3.11-slim

# Ngăn Python tạo tệp .pyc và bật stdout buffer flushing tức thì
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000

WORKDIR /app

# Cài đặt curl phục vụ healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy và cài đặt thư viện phụ thuộc trước để tận dụng Docker layer caching
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy mã nguồn dự án
COPY . /app/

# Tạo thư mục uploads và người dùng non-root để tăng cường bảo mật
RUN mkdir -p /app/uploads && \
    useradd --create-home appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

CMD ["python", "app.py"]
