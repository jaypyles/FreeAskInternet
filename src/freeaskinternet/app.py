import time
from typing import List, Literal, Optional, Union

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from freeaskinternet.utils import ask_internet, search_web_ref

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ModelCard(BaseModel):
    id: str
    object: str = "model"
    created: int = Field(default_factory=lambda: int(time.time()))
    owned_by: str = "owner"
    root: Optional[str] = None
    parent: Optional[str] = None
    permission: Optional[list] = None


class ModelList(BaseModel):
    object: str = "list"
    data: List[ModelCard] = []


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class DeltaMessage(BaseModel):
    role: Optional[Literal["user", "assistant", "system"]] = None
    content: Optional[str] = None


class QueryRequest(BaseModel):
    query: str
    model: str
    ask_type: Literal["search", "llm"]
    llm_auth_token: Optional[str] = "CUSTOM"
    llm_base_url: Optional[str] = ""
    using_custom_llm: Optional[bool] = False
    lang: Optional[str] = "zh-CN"


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    max_length: Optional[int] = None
    stream: Optional[bool] = False


class ChatCompletionResponseChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: Literal["stop", "length"]


class ChatCompletionResponseStreamChoice(BaseModel):
    index: int
    delta: DeltaMessage
    finish_reason: Optional[Literal["stop", "length"]]


class ChatCompletionResponse(BaseModel):
    model: str
    object: Literal["chat.completion", "chat.completion.chunk"]
    choices: List[
        Union[ChatCompletionResponseChoice, ChatCompletionResponseStreamChoice]
    ]
    created: Optional[int] = Field(default_factory=lambda: int(time.time()))


class SearchItem(BaseModel):
    url: str
    icon_url: str
    site_name: str
    snippet: str
    title: str


class SearchItemList(BaseModel):
    search_items: List[SearchItem] = []


class SearchResp(BaseModel):
    code: int
    msg: str
    data: List[SearchItem] = []


@app.get("/v1/models", response_model=ModelList)
async def list_models():
    global model_args
    model_card = ModelCard(id="gpt-3.5-turbo")
    return ModelList(data=[model_card])


@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def create_chat_completion(request: ChatCompletionRequest):
    global model, tokenizer
    if request.messages[-1].role != "user":
        raise HTTPException(status_code=400, detail="Invalid request")
    query = request.messages[-1].content

    generate = predict(query, request.model)
    return EventSourceResponse(generate, media_type="text/event-stream")


def predict(query: str, model_id: str):
    choice_data = ChatCompletionResponseStreamChoice(
        index=0, delta=DeltaMessage(role="assistant"), finish_reason=None
    )
    chunk = ChatCompletionResponse(
        model=model_id, choices=[choice_data], object="chat.completion.chunk"
    )
    yield "{}".format(chunk.json(exclude_unset=True))
    new_response = ""
    current_length = 0

    for token in ask_internet(query=query):
        new_response += token
        if len(new_response) == current_length:
            continue

        new_text = new_response[current_length:]
        current_length = len(new_response)

        choice_data = ChatCompletionResponseStreamChoice(
            index=0,
            delta=DeltaMessage(content=new_text, role="assistant"),
            finish_reason=None,
        )
        chunk = ChatCompletionResponse(
            model=model_id, choices=[choice_data], object="chat.completion.chunk"
        )
        yield "{}".format(chunk.json(exclude_unset=True))

    choice_data = ChatCompletionResponseStreamChoice(
        index=0, delta=DeltaMessage(), finish_reason="stop"
    )
    chunk = ChatCompletionResponse(
        model=model_id, choices=[choice_data], object="chat.completion.chunk"
    )
    yield "{}".format(chunk.json(exclude_unset=True))
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
            url = search_item.get("url")
            icon_url = search_item.get("icon_url")
            site_name = search_item.get("site_name")
            title = search_item.get("title")

            si = SearchItem(
                snippet=snippet,
                url=url,
                icon_url=icon_url,
                site_name=site_name,
                title=title,
            )

            search_item_list.append(si)

    resp = SearchResp(code=0, msg="success", data=search_item_list)
    return resp
