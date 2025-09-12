
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def create_logreg_pipeline(max_iter=1000, model_solver="lbfgs", class_weight="balanced"):
    """Creates a logistic regression pipeline with standard scaling."""
    log_reg_pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("logreg", LogisticRegression(max_iter=max_iter, solver=model_solver, class_weight=class_weight))
    ])

    return log_reg_pipeline


# log_reg_pipeline = Pipeline([
#     ("scaler", StandardScaler()),
#     ("logreg", LogisticRegression(max_iter=1000, class_weight="balanced"))
# ])

# log_reg_pipeline = Pipeline([
#     ("scaler", StandardScaler()),
#     ("logreg", LogisticRegression(max_iter=1000, solver="lbfgs", class_weight="balanced"))
# ])

# log_reg_pipeline = Pipeline([
#     ("scaler", StandardScaler()),
#     ("logreg", LogisticRegression(max_iter=1000, solver="liblinear", class_weight="balanced"))
# ])

# log_reg_pipeline = Pipeline([
#     ("scaler", StandardScaler()),
#     ("logreg", LogisticRegression(max_iter=1000, solver="newton-cg", class_weight="balanced"))
# ])
# log_reg_pipeline = Pipeline([
#     ("scaler", StandardScaler()),
#     ("logreg", LogisticRegression(max_iter=1000, solver="saga", class_weight="balanced"))
# ])  
# log_reg_pipeline = Pipeline([
#     ("scaler", StandardScaler()),
#     ("logreg", LogisticRegression(max_iter=1000, solver="sag", class_weight="balanced"))
# ])
# log_reg_pipeline = Pipeline([
#     ("scaler", StandardScaler()),
#     ("logreg", LogisticRegression(max_iter=1000, solver="sag", penalty="l1", class_weight="balanced"))
# ])