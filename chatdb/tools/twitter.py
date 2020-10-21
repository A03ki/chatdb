from typing import Any

from py2neo.database import Graph
from py2neo.ogm import ModelType


class TweetArchiver:
    def __init__(self, graph: Graph, model_class: ModelType) -> None:
        self.graph = graph
        self._model_class = model_class

    def add_status(self, **properties) -> None:
        cls = self._model_class
        status = cls(**properties)
        in_reply_to_status_id_str = status.in_reply_to_status_id_str

        if in_reply_to_status_id_str:
            in_reply_to_status = self.find_status(in_reply_to_status_id_str)

            if in_reply_to_status is None:
                in_reply_to_status = cls(id_str=in_reply_to_status_id_str)

            status.reply_to(in_reply_to_status)

        self.graph.merge(status)

    def find_status(self, primary_value: Any):
        return self._model_class.match(self.graph, primary_value).first()
