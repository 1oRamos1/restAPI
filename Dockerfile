# ── Stage 1: Build React ─────────────────────────────────────
FROM node:16-alpine AS frontend-build

ARG REACT_APP_API_URL
ENV REACT_APP_API_URL=$REACT_APP_API_URL

WORKDIR /frontend

COPY mysite/frontend/package*.json ./
RUN npm install

COPY mysite/frontend/ ./
RUN npm run build

# ── Stage 2: Build Django ────────────────────────────────────
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY mysite/ .

COPY --from=frontend-build /frontend/build ./frontend/build

RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD ["gunicorn", "mysite.wsgi:application", "--bind", "0.0.0.0:8000"]