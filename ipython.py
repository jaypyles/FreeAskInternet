import json

import requests


def main():
    body = {
        "model": "gpt3.5",
        "messages": [
            {
                "role": "user",
                "content": "How would you build a log cabin if you were really cold?",
            }
        ],
    }
    response = requests.post("http://localhost:8000/v1/chat/completions", json=body)
    response_text = response.text
    data_chunks = response_text.split("\n")

    total_content = ""
    for chunk in data_chunks:
        if chunk:
            print(f"Chunk: {chunk}")
            clean_json = chunk.replace("data: ", "")
            try:
                if clean_json:
                    dict_data = json.loads(clean_json)
                    token = dict_data["choices"][0]["delta"].get("content", "")
                    if token:
                        total_content += token
            except json.JSONDecodeError as e:
                print(f"Failed to decode JSON: {e} - Chunk: {clean_json}")

    print(f"Total content: {total_content}")


if __name__ == "__main__":
    main()
