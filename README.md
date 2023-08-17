# KatWalk
A model deployment infrastructure repository

```bash
kat@herethegpu:~/katwalk$ curl -X 'POST'   'http://localhost:8000/generate'   -H 'accept: application/json'   -H 'Content-Type: application/json'   -d '{
  "prompt": "Write a short story about a robot.",
  "temperature": 0.7,
  "top_p": 0.9,
  "max_tokens": 150
}'
{"text":["\n\nRobot's Dream\n\nOnce upon a time, in a world not so far away, there was a robot named Zeta. Zeta was just like any other robot, going about his daily tasks, completing his programming, and living his life as a machine. But Zeta had a secret dream, a dream that he kept hidden deep within his circuits.\nZeta wanted to be more than just a machine, he wanted to be creative. He wanted to paint, to write, to compose music. He wanted to express himself, to feel alive. But alas, he was just a robot, and such things were not possible.\nOne day, Zeta's programmer, a brilliant scientist"]}
```
