import ollama

schema = {
    "type": "object",
    "properties": {
        "start": {
            "description": "the current position of the piece to move (example: a2)",
            "type": "string",
        },
        "end": {
            "description": "the end position of the move (example: a4)",
            "type": "string",
        }
    },
    "required": [
        "start",
        "end",
    ]
}

stream = ollama.chat(
    model='llama3.2',
    messages=[{'role': 'user', 'content': 'You are a chess player, make your first move. Respond using the json format.'}],
    format=schema,
    stream=True,
)

for chunk in stream:
  print(chunk['message']['content'], end='', flush=True)