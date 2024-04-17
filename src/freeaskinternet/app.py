# STL
import logging
from typing import Optional

# PDM
from fastapi import FastAPI, HTTPException
from sse_starlette.sse import EventSourceResponse
from fastapi.middleware.cors import CORSMiddleware

# LOCAL
from freeaskinternet.utils import ask_internet, search_web_ref
from freeaskinternet.models.Models import *

LOG = logging.getLogger(__name__)

app = FastAPI(title="api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/v1/models", response_model=ModelList)
async def list_models():
    model_card = ModelCard(id="gpt-3.5-turbo")
    return ModelList(data=[model_card])


@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def create_chat_completion(request: ChatCompletionRequest):
    if request.messages[-1].role != "user":
        raise HTTPException(status_code=400, detail="Invalid request")

    query = request.messages[-1].content

    generate = predict(
        query, request.model, request.discord_friendly, request.ollama_model
    )
    return EventSourceResponse(generate, media_type="text/event-stream")


def create_response_chunk(
    model: str,
    content: str = "",
    finish_reason: Optional[Literal["stop", "length"]] = None,
):
    """Helper function to create a formatted response chunk."""
    delta = DeltaMessage(content=content, role="assistant")
    choice_data = ChatCompletionResponseStreamChoice(
        index=0, delta=delta, finish_reason=finish_reason
    )
    chunk = ChatCompletionResponse(
        model=model, choices=[choice_data], object="chat.completion.chunk"
    )
    return chunk.model_dump_json(exclude_unset=True)


def predict(
    query: str,
    model: str,
    discord_friendly: Optional[bool] = False,
    ollama_model: Optional[str] = "",
):
    yield create_response_chunk(model)

    new_response = ""
    current_length = 0

    for token in ask_internet(
        query=query,
        model=model,
        discord_friendly=discord_friendly,
        ollama_model=ollama_model,
    ):
        new_response += token
        if len(new_response) > current_length:
            new_text = new_response[current_length:]
            current_length = len(new_response)
            yield create_response_chunk(model, new_text)

    yield create_response_chunk(model, finish_reason="stop")
    yield "[DONE]"


@app.post("/api/search/get_search_refs", response_model=SearchResp)
async def get_search_refs(request: QueryRequest):
    global search_results
    search_results = []
    search_item_list = []
    if request.ask_type == "search":
        search_links, search_results = search_web_ref(request.query)
        for search_item in search_links:
            snippet = search_item.get("snippet")
            search_item_list.append(SearchItem(**snippet))

    resp = SearchResp(code=0, msg="success", data=search_item_list)
    return resp
