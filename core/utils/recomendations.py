import numpy as np
import pandas as pd
from scipy.sparse import lil_matrix

from core.models import Company, CompanyStudentEmotion


def callobarative(company: Company) -> None:
    student_emotions = CompanyStudentEmotion.objects.values_list("company_id", "student_id", "emotion")

    obj_to_row = []

    company_count = len(np.unique([c for c, *_ in student_emotions]))
    student_count = len(np.unique([c for _, c, _ in student_emotions]))

    matrix = lil_matrix()
