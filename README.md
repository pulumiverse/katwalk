# KatWalk
A model deployment infrastructure repository

```bash
curl -X 'POST'   'http://localhost:8000/generate'   -H 'accept: application/json'   -H 'Content-Type: application/json'   -d '{
  "prompt": "Write a short story about a robot.",
  "temperature": 0.7,
  "top_p": 0.9,
  "max_tokens": 150
}'
```
