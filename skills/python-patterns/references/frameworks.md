# Python Frameworks & Selection Guide (2025)

## 1. Decision Tree

| Build Objective | Recommended Framework | Why |
|-----------------|-----------------------|-----|
| **API-first / Microservices** | **FastAPI** | Async-native, type-safe, Pydantic v2. |
| **Full-stack / Admin / CMS** | **Django** | Batteries-included, mature ORM/Admin. |
| **Simple Scripts / Learning** | **Flask** | Unopinionated, minimal overhead. |
| **AI/ML API Serving** | **FastAPI** | High performance, easy data validation. |

---

## 2. Comparison Matrix

| Feature | FastAPI | Django | Flask |
|---------|---------|--------|-------|
| **Async** | Native | Django 5.0+ | Extensions needed |
| **Admin** | Manual | Built-in | Extensions needed |
| **Validation** | Pydantic (Integrated) | Django Forms | Manual / Pydantic |
| **Learning** | Low | Medium | Low |

---

## 3. Background Task Selection

| Solution | Best For | Architecture |
|----------|----------|--------------|
| **BackgroundTasks** | Quick, in-process tasks. | FastAPI built-in. |
| **Celery** | Distributed workflows. | RabbitMQ/Redis needed. |
| **ARQ** | Async-native queue. | Redis. |
| **RQ** | Simple Redis queue. | Redis. |
| **Dramatiq** | Actor-based. | Simpler than Celery. |
