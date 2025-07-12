FROM python:3.12-slim

# 安裝 uv
RUN pip install uv

WORKDIR /app

# 複製 pyproject.toml 和 uv.lock 以便安裝依賴
COPY pyproject.toml uv.lock /app/

# 安裝依賴
RUN uv sync

# 複製應用程式碼
COPY . /app/

# 設定環境變數 (如果需要，可以在這裡設定預設值，但通常透過 docker-compose 或 .env 傳遞)
# ENV MONGO_HOST=mongodb
# ENV MONGO_PORT=27017
# ENV MONGO_DB=links_db

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
