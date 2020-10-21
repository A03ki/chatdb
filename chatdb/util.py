def flatten_dictionary(dictionary: dict, sep: str = "_") -> dict:
    flat_dictionary = {}

    def _flatten_dictionary(dictionary, parent_name=""):
        for key, value in dictionary.items():
            if isinstance(value, dict):
                _flatten_dictionary(value, f"{parent_name + key}{sep}")
            else:
                flat_dictionary[parent_name+key] = value

    _flatten_dictionary(dictionary)
    return flat_dictionary
