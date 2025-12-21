# Stage 1: Build the frontend
FROM node:18-alpine AS build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Create the final image
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY --from=build /app/frontend/dist ./frontend/dist
COPY backend/ ./backend
COPY agents/ ./agents
COPY main.py .
EXPOSE 8080,3000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
