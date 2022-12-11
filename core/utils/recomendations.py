from scipy.sparse import vstack
import numpy as np

from sklearn.preprocessing import normalize
from scipy.sparse import spdiags

from scipy.sparse import lil_matrix

from core.models import Company, CompanyStudentEmotion, StudentProfile


def collabarative_filtration(company: Company, top_k: int = 50) -> list[dict]:
    student_emotions = CompanyStudentEmotion.objects.values_list("student_id", "company_id", "emotion")

    companies_ids = Company.objects.values_list("id", flat=True)
    student_ids = StudentProfile.objects.values_list("id", flat=True)

    user_to_col = {u: i for i, u in enumerate(companies_ids)}
    obj_to_row = {s: i for i, s in enumerate(student_ids)}

    matrix = lil_matrix((len(obj_to_row), len(user_to_col)))

    for obj_id, user_id, emotion in student_emotions:
        row_id = obj_to_row.get(obj_id)
        col_id = user_to_col.get(user_id)

        if row_id is not None and col_id is not None:
            matrix[row_id, col_id] = int(emotion == "like")

    normalized_matrix = normalize(matrix.tocsr()).tocsr()
    cosine_sim_matrix = normalized_matrix.dot(normalized_matrix.T)

    diag = spdiags(-cosine_sim_matrix.diagonal(), [0], *cosine_sim_matrix.shape, format='csr')
    cosine_sim_matrix = cosine_sim_matrix + diag

    rows = []
    for row_id in np.unique(cosine_sim_matrix.nonzero()[0]):
        row = cosine_sim_matrix[row_id]
        if row.nnz > top_k:
            work_row = row.tolil()
            work_row[0, row.nonzero()[1][np.argsort(row.data)[-m:]]] = 0
            row = row - work_row.tocsr()
        rows.append(row)

    topk_matrix = vstack(rows)
    topk_matrix = normalize(topk_matrix)

    user_vector = matrix[:, user_to_col[company.id]].T

    x = topk_matrix.dot(user_vector).tolil()

    for i, j in zip(*user_vector.nonzero()):
        x[i, j] = 0

    x = x.T.tocsr()
    quorum = 10
    data_ids = np.argsort(x.data)[-quorum:][::-1]

    result = []
    for arg_id in data_ids:
        row_id, p = x.indices[arg_id], x.data[arg_id]
        result.append({"student_id": row_id, "weight": p})

    return result
