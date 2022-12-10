def coverage(elements1: list, elements2: list):
    elements1 = set(elements1)
    elements2 = set(elements2)

    return len(elements1 & elements2) / (len(elements2) + 1)
