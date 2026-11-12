from dataclasses import dataclass


@dataclass(frozen=True)
class Visuals:
    label: str
    switch_group: str
    graph_group: str = "__default__"
    is_default: bool = True

    @property
    def label_long(self):
        return f"{self.label} ({self.switch_group})"