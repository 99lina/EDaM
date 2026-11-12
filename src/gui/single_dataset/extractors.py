from .row import *
from .dependencies import DependencyMap


def quantiles_extractor(data: DependencyMap, visuals: Visuals, id: ForeignID) -> list[VLineRow]:
    return [
        VLineRow(visuals.graph_group, str(label), id, quantile)
        for label, quantile in data["value"].items()
    ]

def n_outliers_extractor(data: DependencyMap, visuals: Visuals, id: ForeignID) -> list[TableRow]:
    return [
        TableRow(visuals.graph_group, visuals.label_long, id, data["value"]["n_outliers"])
    ]