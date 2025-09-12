## NOT COMPLETED MODULE YET
## This file is a registry for test suites for testing suite scalability, 
## intended to use decorators to register different test suites.
## As of now, will use a two basic suites in basic.py and advanced.py

# from typing import Awaitable, Callable, Protocol, Dict
# from generic_client import MCPTesterClient

# class Suite(Protocol):
#     async def __call__(self, client: MCPTesterClient, **kwargs) -> None: ...

# _REGISTRY: Dict[str, Suite] = {}

# def register(name: str):
#     def deco(fn: Suite) -> Suite:
#         _REGISTRY[name] = fn
#         return fn
#     return deco

# def get(name: str) -> Suite:
#     try:
#         return _REGISTRY[name]
#     except KeyError:
#         raise SystemExit(f"Unknown test suite '{name}'. Use --list-suites.")
        
# def all_names():
#     return sorted(_REGISTRY.keys())