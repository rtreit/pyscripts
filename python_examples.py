# This is a place for me to collect some examples of useful ways to do things in Python. 

def find_keys_with_value_containing(data, target, path=''):
    """
    Generator that returns all keys in a nested dictionary whose value contains a given string.
    """
    if isinstance(data, dict):
        for k, v in data.items():
            if target in str(k): 
                yield path + '.' + str(k)
            yield from find_keys_with_value_containing(v, target, path + '.' + str(k))
    elif isinstance(data, list):
        for i, v in enumerate(data):
            yield from find_keys_with_value_containing(v, target, path + '.' + str(i))
    elif isinstance(data, str) and target in data:
        yield path

