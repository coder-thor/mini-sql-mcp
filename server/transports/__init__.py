from transports.base import Transport, TransportOptions
from transports.http import HttpTransport
from transports.stdio import StdioTransport

TRANSPORTS: dict[str, type[Transport]] = {
    "stdio": StdioTransport,
    "http": HttpTransport,
}


# stdio streamablehttp
def create_transport(name: str, options: TransportOptions) -> Transport:
    return TRANSPORTS[name](options)
