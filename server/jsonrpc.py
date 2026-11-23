from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

RequestId = Annotated[int, Field(strict=True)] | str

METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602


class ProtocolError(Exception):
    def __init__(self, code: int, message: str, id: str | int | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.id = id


class JSONRPCRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    jsonrpc: Literal["2.0"]
    id: RequestId
    method: str
    params: dict[str, Any] | None = None


class JSONRPCNotification(BaseModel):
    model_config = ConfigDict(extra="forbid")

    jsonrpc: Literal["2.0"]
    method: str
    params: dict[str, Any] | None = None


class JSONRPCResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    jsonrpc: Literal["2.0"]
    id: RequestId
    result: dict[str, Any]


class ErrorData(BaseModel):
    code: int
    message: str


class JSONRPCError(BaseModel):
    model_config = ConfigDict(extra="forbid")

    jsonrpc: Literal["2.0"]
    id: RequestId | None
    error: ErrorData


JSONRPCMessage = JSONRPCRequest | JSONRPCNotification | JSONRPCResponse | JSONRPCError
jsonrpc_message_adapter: TypeAdapter[JSONRPCMessage] = TypeAdapter(JSONRPCMessage)


def failure(id: str | int | None, code: int, message: str) -> JSONRPCError:
    return JSONRPCError(jsonrpc="2.0", id=id, error=ErrorData(code=code, message=message))
