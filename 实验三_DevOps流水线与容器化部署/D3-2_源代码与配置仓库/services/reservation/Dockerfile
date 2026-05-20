FROM python:3.12-alpine AS test
WORKDIR /app
COPY src ./src
COPY tests ./tests
ENV PYTHONPATH=/app
RUN python -m unittest discover -s tests -v

FROM python:3.12-alpine AS runtime
RUN addgroup -S app && adduser -S app -G app
WORKDIR /app
COPY --from=test /app/src ./src
ENV PORT=8080 SERVICE_NAME=reservation PYTHONUNBUFFERED=1
USER app
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/healthz', timeout=2)"
CMD ["python", "-m", "src.main"]
