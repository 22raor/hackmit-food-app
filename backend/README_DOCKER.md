# Docker Setup for Food Recommender API

## Prerequisites
- Docker and Docker Compose installed
- User added to docker group: `sudo usermod -aG docker $USER` (then logout/login)

## Quick Start

1. **Build and start services:**
   ```bash
   cd /home/rishi/Documents/hackmit/hackmit-food-app/backend
   docker-compose up --build -d
   ```

2. **Check service status:**
   ```bash
   docker-compose ps
   ```

3. **View logs:**
   ```bash
   # All services
   docker-compose logs -f
   
   # API only
   docker-compose logs -f api
   
   # Database only
   docker-compose logs -f db
   ```

4. **Test the API:**
   ```bash
   curl http://localhost:8000/health
   ```

## Services

- **PostgreSQL Database**: `localhost:5432`
  - Database: `food_recommender`
  - User: `postgres`
  - Password: `postgres`

- **FastAPI Backend**: `localhost:8000`
  - Swagger docs: http://localhost:8000/docs
  - ReDoc: http://localhost:8000/redoc

## Testing Authentication

1. **Get JWT token:**
   ```bash
   curl -X POST "http://localhost:8000/auth/google" \
     -H "Content-Type: application/json" \
     -d '{"id_token": "test-token-123"}'
   ```

2. **Use JWT token:**
   ```bash
   curl -X GET "http://localhost:8000/auth/me" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
   ```

## Database Access

Connect to PostgreSQL directly:
```bash
docker-compose exec db psql -U postgres -d food_recommender
```

## Stopping Services

```bash
docker-compose down
```

## Rebuilding

```bash
docker-compose down
docker-compose up --build -d
```
