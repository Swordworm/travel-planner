# Travel Planner API

A REST API for managing travel projects and places using the [Art Institute of Chicago](https://api.artic.edu/docs/) as a source for place data.

## Tech Stack

- **FastAPI** — web framework
- **SQLAlchemy 2** (async) + **aiosqlite** — ORM + SQLite driver
- **Alembic** — database migrations
- **uv** — package manager
- **Pydantic** — request/response validation

## Setup

### Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

### Installation

```bash
git clone <repo-url>
cd travel-planner

# Install dependencies
uv sync

# Copy env file
cp .env.example .env

# Run migrations
uv run alembic upgrade head

# Start server
uv run uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

Interactive docs: `http://localhost:8000/docs`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite+aiosqlite:///travel-planner.db` | SQLite connection string |

## API Endpoints

Base path: `/api/v1`

### Projects

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/projects` | Create a project (optionally with places) |
| `GET` | `/projects` | List all projects |
| `GET` | `/projects/{id}` | Get a single project |
| `PUT` | `/projects/{id}` | Update a project |
| `DELETE` | `/projects/{id}` | Delete a project |

### Places

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/projects/{id}/places` | Add a place to a project |
| `GET` | `/projects/{id}/places` | List all places in a project |
| `GET` | `/projects/{id}/places/{place_id}` | Get a single place |
| `PUT` | `/projects/{id}/places/{place_id}` | Update notes or mark as visited |

## Business Rules

- Project can have 1–10 places
- Same artwork cannot be added to the same project twice
- Project cannot be deleted or updated if any place is marked as visited
- When all places in a project are visited, the project is automatically marked as completed

## Example Requests

### Create a project with places

```bash
curl -X POST http://localhost:8000/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Chicago Art Trip",
    "description": "Artworks to see in Chicago",
    "places": [{"external_id": "27992"}]
  }'
```

### Add a place to an existing project

```bash
curl -X POST http://localhost:8000/api/v1/projects/1/places \
  -H "Content-Type: application/json" \
  -d '{"external_id": "28560"}'
```

### Mark a place as visited

```bash
curl -X PUT http://localhost:8000/api/v1/projects/1/places/1 \
  -H "Content-Type: application/json" \
  -d '{"is_visited": true}'
```

### Update notes

```bash
curl -X PUT http://localhost:8000/api/v1/projects/1/places/1 \
  -H "Content-Type: application/json" \
  -d '{"notes": "Must see the Sunday on La Grande Jatte!"}'
```

## Finding Artwork IDs

Search the Art Institute of Chicago API:

```
GET https://api.artic.edu/api/v1/artworks/search?q=monet&fields=id,title
```

Use the `id` field as `external_id` when adding places.
