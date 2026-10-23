# Student Results API

A small FastAPI service for managing subjects, assessments, and student scores. It uses SQLite for storage, Pydantic to validate JSON, and HTTP Basic authentication to protect API routes.

## Run it locally

Use Python 3.10 or newer.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.create_user
```

Enter a username and a password of at least 12 characters when prompted. Then start the API:

```bash
uvicorn app.main:app --reload
```

The API is available at <http://127.0.0.1:8000>. The SQLite database is created at `data/scores.db`; to use another location, set `DATABASE_PATH` before creating the user and starting the API. Passwords are stored as salted PBKDF2 hashes. All registered users can access all API routes. Use HTTPS outside local development.

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

## Send requests

You can send requests from Swagger UI at <http://127.0.0.1:8000/docs>: select **Authorize**, enter the username and password you created, then open an endpoint and select **Try it out**.

You can also use `curl` from a terminal. Replace `YOUR_USERNAME` and `YOUR_PASSWORD` with the credentials created above. Requests with a JSON body need the `Content-Type: application/json` header.

Create a subject:

```bash
curl -u 'YOUR_USERNAME:YOUR_PASSWORD' \
  -H 'Content-Type: application/json' \
  -d '{"name":"Mathematics"}' \
  http://127.0.0.1:8000/subjects
```

Use the returned subject `id` to create an assessment:

```bash
curl -u 'YOUR_USERNAME:YOUR_PASSWORD' \
  -H 'Content-Type: application/json' \
  -d '{"subject_id":1,"name":"Fractions Quiz","max_score":20}' \
  http://127.0.0.1:8000/assessments
```

Use the returned assessment `id` to add a score:

```bash
curl -u 'YOUR_USERNAME:YOUR_PASSWORD' \
  -H 'Content-Type: application/json' \
  -d '{"assessment_id":1,"student_id":"STU-001","score":16}' \
  http://127.0.0.1:8000/scores
```

Other example requests:

```bash
curl -u 'YOUR_USERNAME:YOUR_PASSWORD' http://127.0.0.1:8000/subjects
curl -u 'YOUR_USERNAME:YOUR_PASSWORD' 'http://127.0.0.1:8000/assessments?subject_id=1'
curl -u 'YOUR_USERNAME:YOUR_PASSWORD' http://127.0.0.1:8000/students/STU-001/results
curl -u 'YOUR_USERNAME:YOUR_PASSWORD' http://127.0.0.1:8000/students/STU-001/average
```

Correct an existing score with a JSON `PUT` request:

```bash
curl -u 'YOUR_USERNAME:YOUR_PASSWORD' \
  -X PUT \
  -H 'Content-Type: application/json' \
  -d '{"score":18}' \
  http://127.0.0.1:8000/scores/1
```

The full sample requests are also available in [`examples/sample_requests_and_responses.json`](examples/sample_requests_and_responses.json), and the Postman collection is in [`postman/Student-Results-API.postman_collection.json`](postman/Student-Results-API.postman_collection.json). Set its `baseUrl`, `username`, and `password` variables before sending requests.

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
