# STL
import time
from typing import List, Union, Literal, Optional

# PDM
from pydantic import Field, BaseModel


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
    discord_friendly: Optional[bool] = False
    ollama_model: Optional[str] = ""


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
