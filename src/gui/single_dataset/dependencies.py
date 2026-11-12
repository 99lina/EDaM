import itertools
from typing import Any, Self

from src.edam.profile.profiles import TransformationProfile

class DependencyMap:
    def __init__(self, *args: str, **kwargs: str):
        all_str = all(
            [isinstance(value, str) for value in itertools.chain(args, kwargs.values())]
        )
        if not all_str:
            raise ValueError("Dict values must be of type 'str'")
        self._mapping = dict(
            itertools.chain(zip(args, args), kwargs.items())
        )
        self._target: dict[str, Any] = {}

    def set_target(self, target: TransformationProfile) -> Self:
        if not isinstance(target, TransformationProfile):
            raise ValueError(f"'target' must be a TransformationProfile ({target} is not)")
        self._target = target.to_dict()
        return self

    def set_alias(self, old_key: str, new_key: str) -> Self:
        if old_key not in self._mapping:
            raise KeyError(f"Mapping key '{old_key}' doesn't exist.")
        elif new_key in self._mapping:
            raise ValueError(f"New key '{new_key}' already exists in mapping.")
        self._mapping[new_key] = self._mapping[old_key]
        return self


    def is_complete(self) -> bool:
        return set(self._target.keys()).issuperset(self._mapping.values())

    def dependency_keys(self) -> set[str]:
        return set(self._mapping.values())

    def __getitem__(self, name: str):
        return self._target[self._mapping[name]]

    def __contains__(self, item: str):
        return self._mapping[item] in self._target