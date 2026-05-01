def count(elements: list) -> int:
    return len(elements)

def count_if(elements: list, condition: callable) -> int:
    return len([element for element in elements if condition(element)])

def count_ifs(elements: list, conditions: list) -> int:
    return len([element for element in elements if all(condition(element) for condition in conditions)])
