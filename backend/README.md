# Evalio Backend

FastAPI-based backend for Evalio course grading rules and simulation.

## Setup

1. Create virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

## API Endpoints

- `GET /health` - Health check
- `GET /courses` - List all courses
- `POST /courses` - Create a new course
- `PUT /courses/{course_id}/weights` - Update assessment weights
- `PUT /courses/{course_id}/grades` - Update grades and standing
- `POST /courses/{course_id}/target` - Evaluate target feasibility
- `POST /courses/{course_id}/minimum-required` - Minimum needed on one assessment
- `POST /courses/{course_id}/whatif` - Read-only what-if analysis

`course_id` is a UUID returned by course creation/list endpoints.

## Database (Coming Soon)

SQLAlchemy models and PostgreSQL integration.
