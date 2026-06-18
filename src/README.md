# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities
- Unregister students from activities
- Persist activities and participants in SQLite

## Getting Started

1. Install the dependencies:

   ```
   pip install -r ../requirements.txt
   ```

2. Run the application:

   ```
   uvicorn app:app --reload
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity                                             |
| DELETE | `/activities/{activity_name}/unregister?email=student@mergington.edu` | Unregister a student from an activity                               |

## Persistent Data Model

The application uses a relational SQLite schema:

1. **activities**:

   - `id` (primary key)
   - `name` (unique)
   - `description`
   - `schedule`
   - `max_participants`

2. **participants**:
   - `id` (primary key)
   - `activity_id` (foreign key to `activities.id`)
   - `email`
   - `created_at`

The schema is defined in `migrations/001_initial_schema.sql`.

## Migration and Seed Data

- Migration script: `migrations/001_initial_schema.sql`
- Seed dataset: `data/activities_seed.json`
- Database file: `data/school.db`

On application startup, migrations are applied automatically and the database is seeded if it is empty.

To reset and reseed the database manually:

```bash
rm -f data/school.db
uvicorn app:app --reload
```
