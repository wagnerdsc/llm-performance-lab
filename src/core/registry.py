"""Generic registry for benchmarks, datasets, and evaluators."""

from __future__ import annotations

from typing import Callable, Generic, Iterator, TypeVar

T = TypeVar("T")


class Registry(Generic[T]):
    """Thread-safe name-to-object registry with decorator support."""

    def __init__(self, name: str = "registry") -> None:
        self._name = name
        self._items: dict[str, T] = {}

    def register(self, name: str, obj: T | None = None) -> Callable[[T], T] | T:
        """Register an object by name. Usable as decorator or direct call."""
        if obj is not None:
            self._items[name] = obj
            return obj

        def decorator(cls: T) -> T:
            self._items[name] = cls
            return cls

        return decorator

    def get(self, name: str) -> T:
        if name not in self._items:
            available = ", ".join(sorted(self._items)) or "(none)"
            raise KeyError(f"{self._name}: '{name}' not found. Available: {available}")
        return self._items[name]

    def list(self) -> list[str]:
        return sorted(self._items)

    def __contains__(self, name: str) -> bool:
        return name in self._items

    def __iter__(self) -> Iterator[tuple[str, T]]:
        yield from sorted(self._items.items())
