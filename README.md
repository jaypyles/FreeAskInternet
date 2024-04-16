# FreeAskInternet++ API

This is a fork of the original FreeAskInternet, but only the backend, re-engineered to be more useful to build different apps (and in English).

Now with Ollama support!

## What is FreeAskInternet

FreeAskInternet is a completely free, private and locally running search aggregator & answer generate using LLM, Without GPU needed. The user can ask a question and the system will use searxng to make a multi engine search and combine the search result to the ChatGPT3.5 LLM and generate the answer based on search results. All process running locally and No GPU or OpenAI or Google API keys are needed.

## Deployment Guide

```bash
git clone https://github.com/jaypyles/FreeAskInternet-API.git
cd FreeAskInternet-API
make build up
```

This deployment relies on a docker network called search. Which can be made through `docker network create search`.

## Example Usage

```python
body = {
  "model": "gpt3.5",
  "messages": [{"role": "user", "content": "Why does the moon create the tides"}],
}

url = "http://searchbackend:8000/v1/chat/completions"
response = requests.post(url, json=body)
```

This is a STREAMED response, so the data is being sent in the response as it is generated, and will need to be parsed for use.

Response:

```
The Moon creates tides through its gravitational pull on Earth's oceans, causing bulges on the side facing the Moon and the side opposite it, resulting in high tides.
The low points correspond to low tides [citation:1][citation:2]. These tides occur due to the gravitational forces between the Moon and Earth,
leading to the ocean's surface rising and falling regularly [citation:1]. While the Moon and Earth's gravitational interaction primarily drives tides, other factors,
such as the shape of Earth, its geography, and the depth of the ocean, also influence tidal patterns [citation:1]. Additionally, the timing of high and low tide events
varies by location due to factors like the continental shelf's slope, leading to lag times of hours or even close to a day [citation:1].
NOAA utilizes advanced equipment to monitor tides in over 3,000 locations in the U.S. [citation:1].

---
Citations:
1. https://oceanservice.noaa.gov/facts/moon-tide.html
2. https://science.nasa.gov/resource/tides/
3. https://scijinks.gov/tides/
4. https://www.timeanddate.com/astronomy/moon/tides.html
5. https://oceanservice.noaa.gov/education/tutorial_tides/tides06_variations.html
```

Example of how I parse the data being received:

```python
  response_text = response.text
  data_chunks = response_text.split("\n")
  total_content = ""
  for chunk in data_chunks:
      if chunk:
          clean_json = chunk.replace("data: ", "")
          try:
              if clean_json:
                  dict_data = json.loads(clean_json)
                  token = dict_data["choices"][0]["delta"].get("content", "")
                  if token:
                      total_content += token
          except json.JSONDecodeError as e:
              print(f"Failed to decode JSON: {e} - Chunk: {clean_json}")

  return total_content
```

## Ollama Guide

In the docker-compose file, provide the environmental variable `OLLAMA_HOST`

```yml
backend:
  image: jpyles0524/freeaskinternetapi:latest
  build:
    context: .
  container_name: searchbackend
  environment:
    - OLLAMA_HOST=http://ollama:11434
  depends_on:
    - llm-freegpt35
  restart: on-failure
  networks:
    - search
```

In the request you send to the API, change the model from `gpt3.5` to `ollama`, and provide the Ollama model name:

```python

body = {
  "model": "ollama",
  "messages": [{"role": "user", "content": "Why does the moon create the tides"}],
  "ollama_model": "llama2"
}

```

## Credits

- Nashu: [https://github.com/nashsu/FreeAskInternet](https://github.com/nashsu/FreeAskInternet)
- ChatGPT-Next-Web : [https://github.com/ChatGPTNextWeb/ChatGPT-Next-Web](https://github.com/ChatGPTNextWeb/ChatGPT-Next-Web)
- FreeGPT35: [https://github.com/missuo/FreeGPT35](https://github.com/missuo/FreeGPT35)
- Kimi\Qwen\ZhipuAI [https://github.com/LLM-Red-Team](https://github.com/LLM-Red-Team)
- searxng: [https://github.com/searxng/searxng](https://github.com/searxng/searxng)

## License

Apache-2.0 license
