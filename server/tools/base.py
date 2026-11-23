import inspect
import logging
from collections.abc import Callable
from typing import Any, get_type_hints

from pydantic import BaseModel, create_model

logger = logging.getLogger("tools")

# tools就是我们要通过 tools/list返回给 ai agent 比如 cursor claude 的所有 tool

# Tool(get_artifact)

class Tool:

    def __init__(self, fn: Callable[..., list]) -> None:
        self.fn = fn
        self.model = model_of(fn) # self.model ？ pydantic的实例对象

    @property
    def name(self) -> str:
        return self.fn.__name__

    def definition(self) -> dict[str, Any]:
        # 这个结构体就是给到ai agent的对象 inputschema是函数的类型表述 get_character { name: string, required: true }
        return {
            "name": self.name,
            "description": inspect.getdoc(self.fn) or "",
            "inputSchema": self.model.model_json_schema(),
        }

    # py的一个语法糖: tool = Tool(), tool() === tool.__call__() ### tool()
    def __call__(self, arguments: Any) -> list:
        logger.info("call %s %s", self.name, arguments)
        data = self.model.model_validate(arguments) # 验证传进来的参数
        result = self.fn(**data.model_dump()) # 如果是Tool(get_artifact) 那么 self.fn()就是get_artifact()
        logger.info("call %s -> %s", self.name, result)
        return result


def tool(fn: Callable[..., list]) -> Tool:
    return Tool(fn)


def model_of(fn: Callable[..., list]) -> type[BaseModel]:
    hints = get_type_hints(fn, include_extras=True) # 获取这个函数的类型注解
    logger.info("get_type_hints(%s) = %s", fn.__name__, hints)
    signature = inspect.signature(fn) # 拿到函数的一些参数签名信息
    logger.info("inspect.signature(%s) = %s", fn.__name__, signature)
    fields = {}
    for name, param in signature.parameters.items():
        default = ... if param.default is inspect.Parameter.empty else param.default
        logger.info("parameter %s annotation=%s default=%s", name, param.annotation, default)
        fields[name] = (hints.get(name, Any), default)
    return create_model(fn.__name__, **fields)
