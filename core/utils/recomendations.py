import numpy as np
import pandas as pd
from scipy.sparse import lil_matrix

from core.models import Company, CompanyStudentEmotion


def callobarative(company: Company) -> None:
    student_emotions = CompanyStudentEmotion.objects.values_list("company_id", "student_id", "emotion")

    companies_ids = Company.objects.values_list("id", flat=True)
    student_ids = []

    user_to_col = {u: i for i, u in enumerate(companies_ids)}
    obj_to_row = []

    company_count = len(np.unique([c for c, *_ in student_emotions]))
    student_count = len(np.unique([c for _, c, _ in student_emotions]))

    matrix = lil_matrix()
