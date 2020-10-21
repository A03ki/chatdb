"""
The code below is:
Copyright 2011-2020, Nigel Small
Licensed under the Apache License, Version 2.0
(https://github.com/technige/py2neo/blob/master/LICENSE)
"""


import csv
from typing import Any, Optional, List, Tuple

from py2neo.cypher import cypher_escape
from py2neo.database import Graph
from py2neo.matching import NodeMatch
from py2neo.ogm import ModelType

pandas = Any


class Predicate:
    @classmethod
    def cast(cls, value: Any):
        if value is None:
            return IsNull()
        elif isinstance(value, Predicate):
            return value
        elif isinstance(value, (tuple, set, frozenset)):
            return In(value)
        else:
            return EqualTo(value)

    def compile(self, key: str, label_n: int, _):
        return "", {}


class IsNull(Predicate):
    def compile(self, key: str, label_n: int = 0):
        return f"s{label_n}.{cypher_escape(key)} IS NULL", {}


class Predicate1(Predicate):
    def __init__(self, value: Any):
        self.value = value


class EqualTo(Predicate1):
    def compile(self, key: str, tmp_n: int, label_n: int = 0):
        return (f"s{label_n}.{cypher_escape(key)} = ${tmp_n}",
                {f"{tmp_n}": self.value})


class In(Predicate1):
    def compile(self, key: str, tmp_n: int, label_n: int = 0):
        return (f"s{label_n}.{cypher_escape(key)} IN ${tmp_n}",
                {f"{tmp_n}": list(self.value)})


def _property_predicates(properties: dict, label_n: int = 0, offset: int = 1):
    for i, (key, value) in enumerate(properties.items(), start=offset):
        yield Predicate.cast(value).compile(key, i, label_n)


class ReplyPathMatch(NodeMatch):
    def __init__(self, graph: Graph, model_classes: List[ModelType],
                 predicates: tuple = tuple(), order_by: tuple = tuple(),
                 skip: Optional[int] = None,
                 limit: Optional[int] = None) -> None:
        self._model_classes = model_classes
        labels = {model_class.__primarylabel__ for model_class in model_classes}
        super().__init__(graph=graph, labels=labels, predicates=predicates,
                         order_by=order_by, skip=skip, limit=limit)

    def _query_and_parameters(self, count: bool = False) -> Tuple[str, dict]:
        _nodes = [f"(s{i}:{model_class.__primarylabel__})"
                  for i, model_class in enumerate(self._model_classes)]
        clauses = ["MATCH path = (%s)" % "<-[:REPLY]-".join(_nodes)]
        parameters = {}

        if self._predicates:
            predicates = []
            for predicate in self._predicates:
                if isinstance(predicate, tuple):
                    predicate, param = predicate
                    parameters.update(param)
                predicates.append(predicate)
            clauses.append("WHERE %s" % " AND ".join(predicates))
        if count:
            clauses.append("RETURN count(path)")
        else:
            clauses.append("RETURN path")
            if self._order_by:
                clauses.append("ORDER BY %s" % (", ".join(self._order_by)))
            if self._skip:
                clauses.append("SKIP %d" % self._skip)
            if self._limit is not None:
                clauses.append("LIMIT %d" % self._limit)
        return " ".join(clauses), parameters

    def where(self, *predicates, **properties):
        return self.__class__(self.graph, self._model_classes,
                              (self._predicates + predicates
                               + tuple(_property_predicates(properties))),
                              self._order_by, self._skip, self._limit)

    def order_by(self, *fields):
        return self.__class__(self.graph, self._model_classes,
                              self._predicates, fields, self._skip,
                              self._limit)

    def skip(self, amount: Optional[int]):
        return self.__class__(self.graph, self._model_classes,
                              self._predicates, self._order_by,
                              amount, self._limit)

    def limit(self, amount: Optional[int]):
        return self.__class__(self.graph, self._model_classes,
                              self._predicates, self._order_by,
                              self._skip, amount)


class ReplyPathMatcher:
    _match_class = ReplyPathMatch

    def __init__(self, graph: Graph) -> None:
        self.graph = graph

    def match(self, model_classes: List[ModelType],
              primary_value: Any = None) -> ReplyPathMatch:
        return self._match(model_classes, primary_value=primary_value)

    def _match(self, model_classes: List[ModelType],
               primary_value: Any = None) -> ReplyPathMatch:
        if primary_value is not None:
            cls = model_classes[0]
            if cls.__primarylabel__ == "__id__":
                predicate = {"id(s0)": f"{primary_value}"}
            else:
                predicate = {f"{cls.__primarykey__}": f"{primary_value}"}
            return self._match_class(self.graph, model_classes=model_classes).where(**predicate)
        else:
            return self._match_class(self.graph, model_classes=model_classes)


class TextOutput(ReplyPathMatch):
    def __init__(self, graph: Graph, model_classes: List[ModelType],
                 predicates: tuple = tuple(), order_by: tuple = tuple(),
                 skip: Optional[int] = None,
                 limit: Optional[int] = None) -> None:
        super().__init__(graph=graph, model_classes=model_classes,
                         predicates=predicates, order_by=order_by,
                         skip=skip, limit=limit)

    def extract_text(self) -> List[List[str]]:
        records = self.all()
        return [[node["text"] for node in record.nodes] for record in records]

    def to_csv(self, file, newline="", delimiter=",", **kwargs) -> None:
        rows = self.extract_text()
        with open(file, "w", newline=newline) as csvfile:
            writer = csv.writer(csvfile, delimiter=delimiter, **kwargs)
            writer.writerows(rows)

    def to_multiple_csv(self, files, newline="", **kwargs) -> None:
        rows = self.extract_text()
        columns = [[[column] for column in columns]
                   for columns in zip(*rows)]
        for column, file in zip(columns, files):
            with open(file, "w", newline=newline) as csvfile:
                writer = csv.writer(csvfile, **kwargs)
                writer.writerows(column)

    def to_data_frame(self, columns: Optional[List[str]] = None) -> "pandas.DataFrame":
        try:
            from pandas import DataFrame
        except ImportError:
            raise ImportError("Please install Pandas.")
        else:
            return DataFrame(self.extract_text(), columns=columns)


class TextOutputer(ReplyPathMatcher):
    _match_class = TextOutput

    def __init__(self, graph: Graph) -> None:
        self.graph = graph

    def match(self, model_classes: List[ModelType],
              primary_value: Any = None) -> TextOutput:
        return self._match(model_classes, primary_value=primary_value)
