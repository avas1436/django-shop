# Dockerfile

# ==========================
# Base Image
# ==========================
FROM python:3.13-slim AS base

# نمایش لاگ های پایتون
ENV PYTHONUNBUFFERED=1
# عدم ایجاد کش پایتون برای ایمیج کوچک تر
ENV PYTHONDONTWRITEBYTECODE=1
# عدم ایجاد محیط مجازی توسط یو وی
ENV UV_SYSTEM_PYTHON=1

# install uv
RUN pip install --no-cache-dir uv


# ==========================
# Builder
# ==========================
FROM base AS builder

# این محل از محیط لوکال نیست صرفا یک فولدر داخل کانتینر ایجاد خواهد شد
# container working directory
WORKDIR /app

# این دو فایل از محیط کنار داکرفایل کپی میشه به پوشه بک اند داخل ایمیج
# Copy dependency files first (better Docker cache)
COPY pyproject.toml uv.lock ./

# Install only production dependencies
RUN uv sync --frozen --no-dev


# ==========================
# Final Image
# ==========================
FROM base AS final

WORKDIR /app

# کپی کردن تمام پکیج‌های نصب شده از مرحله قبل
COPY --from=builder /usr/local /usr/local

# کپی کردن کدهای پروژه
COPY . .

# Create a non-root user
RUN useradd --create-home app

USER app

# Expose port
EXPOSE 8000

# ==========================
# Development
# ==========================
CMD ["uv", "run", "--no-dev", "manage.py", "runserver", "0.0.0.0:8000"]

# ==========================
# Production
# ==========================
# CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]