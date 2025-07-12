FROM python:3.12-slim

# 安裝 uv
RUN pip install uv

WORKDIR /app

# 複製 pyproject.toml 和 uv.lock 以便安裝依賴
COPY pyproject.toml uv.lock /app/

# 安裝依賴
RUN uv venv
RUN uv lock
RUN uv sync

ENV PATH="/app/.venv/bin:$PATH"

# 複製應用程式碼
COPY . /app/

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
