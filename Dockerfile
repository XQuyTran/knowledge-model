FROM python:3.14-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends clang clang-tidy g++ ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir -e .
RUN useradd --uid 1000 --create-home appuser
USER appuser
EXPOSE 8000
COPY diagnostic_pipeline ./diagnostic_pipeline
CMD ["uvicorn", "diagnostic_pipeline.api.main:app", "--host", "0.0.0.0", "--port", "8000"]