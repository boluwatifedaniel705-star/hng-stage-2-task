# hng-stage-2-task
smart library catalogue
# Intelligence Query Engine — Insighta Labs

A production-ready queryable demographic intelligence API built with **FastAPI** and **PostgreSQL**.

---

## Features

- Advanced filtering by gender, age group, country, age range, and confidence scores
- Combined multi-condition filters
- Sorting by age, created_at, or gender_probability
- Pagination with configurable page size
- **Natural language query parsing** — convert plain English into structured filters
- UUID v7 primary keys
- Full CORS support

---

## Tech Stack

- **Python 3.11+**
- **FastAPI** — web framework
- **SQLAlchemy** — ORM
- **PostgreSQL** — database
- **uuid6** — UUID v7 generation

---

## Setup

### 1. Clone and install dependencies

```bash

**Response:**
```json
{
  "status": "success",
  "page": 1,
  "limit": 10,
  "total": 342,
  "data": [...]
}
```

---

### `GET /api/profiles/search`

| Parameter | Type | Description |
|---|---|---|
| `q` | string | Natural language query |
| `page` | integer | Default `1` |
| `limit` | integer | Default `10`, max `50` |

**Example queries:**

| Query | Interpreted as |
|---|---|
| `young males` | gender=male, age 16–24 |
| `females above 30` | gender=female, min_age=30 |
| `people from angola` | country_id=AO |
| `adult males from kenya` | gender=male, age_group=adult, country_id=KE |

---

## Error Responses

```json
{ "status": "error", "message": "<description>" }
```

| Code | Meaning |
|---|---|
| `400` | Invalid or missing parameter |
| `422` | Invalid parameter type |
| `404` | Profile not found |
| `500` | Server error |

---

## Natural Language Parser

Rule-based only — no AI or LLMs used.

- **Gender:** male, males, man, men, female, females, woman, women
- **Age groups:** child, teenager, adult, senior and synonyms
- **"young":** maps to ages 16–24
- **Age:** `above X`, `over X`, `below X`, `under X`
- **Country:** `from [country name]` → ISO code

---

## Project Structure

