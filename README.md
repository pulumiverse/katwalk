# KatWalk
A model deployment runway project.

```bash
kat@herethegpu:~/katwalk$ curl -s -X 'POST'   'http://localhost:8000/v1/chat'   -H 'accept: application/json'   -H 'Content-Type: application/json'   -d '{
  "prompt": "Tell me a story about a little robot."
}' | jq .
{
  "text": [
    "\nOnce upon a time, there was a little robot named R2. R2 was a friendly and curious robot who lived in a big city. One day, R2 decided to go on an adventure. He set out to explore the city and learn about all the different things he could see and do.\nAs R2 explored the city, he met all kinds of people. Some were kind and welcoming, while others were scared or suspicious of him. Despite this, R2 continued to be friendly and curious, always asking questions and trying to learn more about the world around him.\nOne day, while R2 was exploring a busy market, he saw a group of people gathered around a little girl who was"
  ]
}
```

```
To perform an initial deployment, run the following commands:

   1. python3 -m venv venv
   2. source venv/bin/activate
   3. python -m pip install --upgrade pip setuptools wheel
   4. python -m pip install -r requirements.txt
   5. pulumi login file://~/.pulumi/state
   6. pulumi stack init

Then, run `pulumi up`
```

```bash
.
├── Dockerfile
├── LICENSE
├── main.py
├── README.md
└── src
    ├── app
    │   └── main.py
    └── etc
        └── apt
            └── apt.conf.d
                └── apt.conf
```
