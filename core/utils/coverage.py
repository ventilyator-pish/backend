def coverage(elements1: list, elements2: list):
    elements1 = set(elements1)
    elements2 = set(elements2)

    if not elements2:
        return 1

    return len(elements1 & elements2) / (len(elements2) + 1)


def get_student_coverage(students, tags):
    pass
