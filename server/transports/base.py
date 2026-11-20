from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class TransportOptions:
    host: str
    port: int


# Transport实体 
# 抽象方法： 只要继承了这个类的任何子类都需要实现这个方法
class Transport(ABC):
    def __init__(self, options: TransportOptions) -> None:
        self.options = options

    @abstractmethod
    def serve(self) -> None: ...


# 工厂模式
# streamable http stdio