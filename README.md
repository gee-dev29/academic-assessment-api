# Student Results API

A small FastAPI service for managing subjects, assessments, and student scores. It uses SQLite for storage, Pydantic to validate JSON, and HTTP Basic authentication to protect API routes.

## Run it locally

Use Python 3.10 or newer.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The database is created at `data/scores.db` the first time the service starts. To use another location, set `DATABASE_PATH`.

For this learning project, the default Basic Auth login is `teacher` / `classroom123`. It is only for local practice. Set your own values before starting the service:

```bash
export API_USERNAME=teacher
export API_PASSWORD=your-local-password
uvicorn app.main:app --reload
```

Basic Auth sends credentials with requests. Use HTTPS and strong, private credentials outside local practice; do not use this demo login for real student data.

## API documentation

Start the service, then open:

- Swagger UI: <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>

All API routes require Basic Auth. The OpenAPI documentation pages are provided by FastAPI.

| Method | Path | What it does |
| --- | --- | --- |
| `POST` | `/subjects` | Add a subject |
| `GET` | `/subjects` | List subjects |
| `POST` | `/assessments` | Add an assessment to a subject |
| `GET` | `/assessments` | List assessments; optionally filter with `?subject_id=1` |
| `POST` | `/scores` | Add a student's score |
| `PUT` | `/scores/{score_id}` | Correct an existing score |
| `GET` | `/students/{student_id}/results` | Retrieve the student's assessment results |
| `GET` | `/students/{student_id}/average` | Calculate the average percentage |

The average is the arithmetic mean of the student's assessment percentages, so assessments with different maximum scores can be compared consistently.

## Try a complete example

Send `Content-Type: application/json` on requests with a body. Authenticate with the local practice credentials above.

Create a subject:

```http
POST /subjects
```

```json
{"name": "Mathematics"}
```

Response (`201 Created`):

```json
{"id": 1, "name": "Mathematics"}
```

Create an assessment:

```http
POST /assessments
```

```json
{"subject_id": 1, "name": "Fractions Quiz", "max_score": 20}
```

Add a score:

```http
POST /scores
```

```json
{"assessment_id": 1, "student_id": "STU-001", "score": 16}
```

Response (`201 Created`):

```json
{"id": 1, "message": "Score added"}
```

To correct that result, send `PUT /scores/1` with `{"score": 18}`. Then request `GET /students/STU-001/results`:

```json
[
  {
    "assessment_id": 1,
    "assessment_name": "Fractions Quiz",
    "subject_name": "Mathematics",
    "score": 18.0,
    "max_score": 20.0,
    "percentage": 90.0
  }
]
```

`GET /students/STU-001/average` returns:

```json
{
  "student_id": "STU-001",
  "average_percentage": 90.0,
  "assessment_count": 1
}
```

Full sample requests and responses are in [`examples/sample_requests_and_responses.json`](examples/sample_requests_and_responses.json). An importable Postman collection is in [`postman/Student-Results-API.postman_collection.json`](postman/Student-Results-API.postman_collection.json). Set its `baseUrl`, `username`, and `password` variables for your local server.

## Validation and errors

Pydantic checks that required fields have the right types, names and student IDs are not blank, and scores and maximum scores are valid numbers. The API also checks that a score does not exceed its assessment's maximum.

Errors use clear HTTP status codes and JSON details:

| Status | Meaning | Example |
| --- | --- | --- |
| `401` | Missing or incorrect login | `{"detail": "Incorrect username or password"}` |
| `404` | Assessment, score, or average result does not exist | `{"detail": "Assessment not found"}` |
| `409` | Duplicate subject, assessment, or score | `{"detail": "A score for this student and assessment already exists"}` |
| `422` | Invalid request data or a score above the maximum | `{"detail": "Score cannot be greater than the maximum of 20.0"}` |

FastAPI's `422` validation response includes a `detail` list that identifies the invalid field and reason.

## Why authentication, validation, and clear errors matter

- **Authentication** limits who can read or change student results. Keep credentials private and use HTTPS so they are not sent over an unencrypted connection.
- **Validation** catches missing, incorrectly formatted, negative, or out-of-range values before they can become stored results.
- **Clear errors** let a client fix a rejected request without guessing whether data was saved. They also avoid returning internal database details.

## Run tests

```bash
pytest
```
