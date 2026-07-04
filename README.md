# Password Checker

Simple microservice for checking password strength. It utilizes the `zxcvbn` library for strength checking with additional manual checks. The password check follows HIPAA and FedRAMP requirements. These constraints revolve around password length and relations to previous passwords and other credentials. The app does not store any user data.

---

## Example

```bash
curl -X POST https://password-checker-qeiu.onrender.com/check_password/ \
  -H "Content-Type: application/json" \
  -d '{"username": "okenobi", "email": "o.kenobi@jedi-council.com", "password": "Hello there!"}'
```

Response:
```json
{
  "score": 2,
  "label": "Medium",
  "color": "#FFC107",
  "description": "Contains weak patterns or personal info.",
  "is_compliant": false,
  "suggestions": ["Add another word or two. Uncommon words are better."]
}
```
---

## Password check algorithm

As mentioned, the app uses the `zxcvbn` library to estimate password strength from 0 to 4. A few changes have been made to make this algorithm more suitable for the requirements. The app automatically marks a password as `VERY_WEAK` when the length is below 12 characters. HIPAA requirements state that 12 is the absolute minimum, while the recommended length is 15. To address that, passwords with lengths between 12 and 15 have their score lowered by one. Password lenghts is contrained and set to max length of 72 characters. These are default limits for `zxcvbn` library.

When a user provides an email address and username, the app detects if the password contains similar parts. When similar parts are detected, they are marked as a single token, and the effective password strength drops significantly. The password is also compared against the most popular English words to add an extra layer of security. Project contains file with common passwords and checks if users password hasn't been leaked.

Users can provide a previous password to check if the new one is too similar. Similarity is calculated using [Levenshtein distance](https://en.wikipedia.org/wiki/Levenshtein_distance).

The project contains unit tests that cover various edge cases and popular password schemes. To run them use
```bash
# With uv
uv run python -m unittest tests/password_unittest.py
uv run python -m unittest tests/test_api.py

# OR using python
python -m unittest tests/password_unittest.py
python -m unittest tests/test_api.py
```

Error logs from FastAPI has been redacted to secure user information.
---

## Deployment
- **Live Service:** [https://password-checker-qeiu.onrender.com](https://password-checker-qeiu.onrender.com)
- **API Docs:** [https://password-checker-qeiu.onrender.com/docs](https://password-checker-qeiu.onrender.com/docs)
*Note: Hosted on Render's free tier; the service may take ~30s to wake up after inactivity.*

---

## Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (recommended) or `pip`

### Local build

Create a virtual environment:
```bash
# Using uv
uv venv

# OR using standard python
python -m venv .venv
```
Install requirements:
```bash
# Using uv
uv sync

# OR using pip
pip install -r requirements.txt
```

Run the app via uvicorn:
```bash
# Using uv
uv run uvicorn main:app

# OR using venv
uvicorn main:app
```
---
### Docker deployment
The project contains a ready-to-deploy Dockerfile. To build the project, use:
```bash
docker build -t password-checker-api .
```
To run it:
```bash
docker run -d -p 8000:8000 --name my-password-checker password-checker-api
```
---