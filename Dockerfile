FROM node:22-alpine AS frontend-build
WORKDIR /frontend
COPY frontend/package.json ./
RUN npm install
COPY frontend/ ./
ENV VITE_API_URL=/api
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/app ./app
COPY --from=frontend-build /frontend/dist ./frontend_dist

ENV PORT=10000
ENV DATABASE_URL=sqlite:///./store.db
ENV DEFAULT_TRY_RUB=2.28
ENV DEFAULT_MARKUP=0.10

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
