# Stage 1: build the React app
FROM node:22-alpine AS frontend
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Python API that also serves the built website
FROM python:3.13-slim
WORKDIR /app/backend
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/app ./app
COPY --from=frontend /frontend/dist /app/frontend/dist
ENV PORT=8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
