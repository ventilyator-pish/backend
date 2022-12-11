import pandas as pd
from scipy.sparse import lil_matrix

from core.models import Company, CompanyStudentEmotion


def callobarative(company: Company) -> None:
    student_emotions = CompanyStudentEmotion.objects.values_list("company_id", "student_id", "emotion")

    matrix = lil_matrix()
