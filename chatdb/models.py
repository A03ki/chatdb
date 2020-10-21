import copy

from py2neo.ogm import Label, Model, Property, Related, RelatedTo, RelatedFrom

from chatdb.util import flatten_dictionary


def MetaKeepingModelAttrs(name, bases, attributes):
    model_attributes = {"property": {}, "label": {}, "related": {}}
    for attr_name, attr in attributes.items():
        if isinstance(attr, Property):
            model_attributes["property"][attr_name] = attr
        elif isinstance(attr, Label):
            model_attributes["label"][attr_name] = attr
        elif isinstance(attr, Related):
            model_attributes["related"][attr_name] = attr

    cls = type(name, bases, attributes)

    if "__model_attributes__" in dir(cls):
        new_model_attributes = copy.deepcopy(cls.__model_attributes__)
        for key, value in model_attributes.items():
            new_model_attributes[key].update(**value)
        cls.__model_attributes__ = new_model_attributes
    else:
        cls.__model_attributes__ = model_attributes

    return cls


class Status(Model, metaclass=MetaKeepingModelAttrs):
    __primarylabel__ = "Status"

    text = Property()

    in_reply_to_statuses = RelatedTo(__primarylabel__, "REPLY")
    in_reply_from_statuses = RelatedFrom(__primarylabel__, "REPLY")

    def __init__(self, **properties) -> None:
        all_properties = self.__model_attributes__["property"]
        for key, value in properties.items():
            if key in all_properties:
                setattr(self, key, value)

    def reply_to(self, model: "Status") -> None:
        self.in_reply_to_statuses.add(model)
        model.in_reply_from_statuses.add(self)

    def reply_from(self, model: "Status") -> None:
        self.in_reply_from_statuses.add(model)
        model.in_reply_to_statuses.add(self)


class OrdinaryStatus(Status, metaclass=MetaKeepingModelAttrs):
    __primarykey__ = "status_id"

    status_id = Property()
    user_name = Property()
    date = Property()

    def __init__(self, **properties) -> None:
        super().__init__(**properties)


class SimpleTweetStatus(Status, metaclass=MetaKeepingModelAttrs):
    __primarylabel__ = "TweetStatus"
    __primarykey__ = "id_str"

    id_str = Property()
    in_reply_to_status_id_str = Property()
    created_at = Property()

    def __init__(self, **properties) -> None:
        flat_dict = flatten_dictionary(properties)
        super().__init__(**flat_dict)
