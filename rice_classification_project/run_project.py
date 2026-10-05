"""End-to-end lightweight rice variety classification project.

Run from the project directory:
    python rice_classification_project/run_project.py

The script reads the supplied ARFF file, creates figures and CSV result files,
compares baseline models, selects useful features, tunes the final classifier,
and saves a deployment-ready model.
"""

from pathlib import Path
import json
import sys
import types
import warnings

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.io import arff

# The local Anaconda pyarrow installation cannot load its native DLL. Scikit-learn
# only checks pyarrow's version at import time and this project does not use it.
try:
    import pyarrow  # noqa: F401
except ImportError:
    pyarrow = types.ModuleType("pyarrow")
    pyarrow.__version__ = "17.0.0"
    sys.modules["pyarrow"] = pyarrow

from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import RFE, mutual_info_classif
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier

warnings.filterwarnings("ignore", category=FutureWarning)

ROOT = Path(__file__).resolve().parent
DATASET = ROOT.parent / "rice+cammeo+and+osmancik" / "Rice_Cammeo_Osmancik.arff"
OUTPUT = ROOT / "outputs"
FIGURES = OUTPUT / "figures"
MODELS = OUTPUT / "models"
RANDOM_STATE = 42


def save_figure(name: str) -> None:
    """Save the active plot consistently and release its memory."""
    plt.tight_layout()
    plt.savefig(FIGURES / name, dpi=200, bbox_inches="tight")
    plt.close()


def load_data() -> pd.DataFrame:
    """Load the supplied ARFF dataset and make the class values readable."""
    data, _ = arff.loadarff(DATASET)
    frame = pd.DataFrame(data)
    frame["Class"] = frame["Class"].str.decode("utf-8")
    return frame


def make_eda(df: pd.DataFrame, features: list[str]) -> dict:
    """Create dataset inspection outputs and exploratory plots."""
    class_counts = df["Class"].value_counts().rename_axis("Class").reset_index(name="Count")
    class_counts.to_csv(OUTPUT / "class_distribution.csv", index=False)
    df.describe().T.to_csv(OUTPUT / "feature_summary.csv")

    sns.set_theme(style="whitegrid", palette="deep")
    ax = sns.countplot(data=df, x="Class", hue="Class", legend=False)
    ax.set(title="Rice Variety Distribution", xlabel="Rice variety", ylabel="Number of grains")
    save_figure("01_class_distribution.png")

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    for ax, feature in zip(axes.ravel(), ["Area", "Perimeter", "Major_Axis_Length", "Minor_Axis_Length"]):
        sns.boxplot(data=df, x="Class", y=feature, hue="Class", legend=False, ax=ax)
        ax.set_title(f"{feature} by rice variety")
    save_figure("02_key_feature_boxplots.png")

    plt.figure(figsize=(9, 7))
    sns.heatmap(df[features].corr(), annot=True, fmt=".2f", cmap="coolwarm", center=0)
    plt.title("Feature Correlation Heatmap")
    save_figure("03_feature_correlation.png")

    return {
        "records": int(len(df)),
        "input_features": int(len(features)),
        "missing_values": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "class_counts": {str(k): int(v) for k, v in df["Class"].value_counts().items()},
    }


def evaluate_models(X_train, X_test, y_train, y_test) -> tuple[pd.DataFrame, dict]:
    """Fit baseline classifiers and return comparable test metrics."""
    classifiers = {
        "Logistic Regression": LogisticRegression(max_iter=2000, random_state=RANDOM_STATE),
        "K-Nearest Neighbors": KNeighborsClassifier(n_neighbors=5),
        "Support Vector Machine": SVC(kernel="rbf", C=1.0, probability=True, random_state=RANDOM_STATE),
        "Decision Tree": DecisionTreeClassifier(random_state=RANDOM_STATE),
        "Random Forest": RandomForestClassifier(n_estimators=300, random_state=RANDOM_STATE, n_jobs=-1),
        "XGBoost": XGBClassifier(
            n_estimators=300,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            objective="binary:logistic",
            eval_metric="logloss",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
    }
    results, fitted = [], {}
    for name, classifier in classifiers.items():
        model = Pipeline([("scaler", StandardScaler()), ("classifier", classifier)])
        if name == "XGBoost":
            # XGBoost expects numeric class labels; encode Cammeo as the positive class.
            encoded_train = (y_train == "Cammeo").astype(int)
            model.fit(X_train, encoded_train)
            prediction = np.where(model.predict(X_test) == 1, "Cammeo", "Osmancik")
            probability = model.predict_proba(X_test)[:, 1]
        else:
            model.fit(X_train, y_train)
            prediction = model.predict(X_test)
            probability = model.predict_proba(X_test)[:, list(model.classes_).index("Cammeo")]
        results.append({
            "Model": name,
            "Accuracy": accuracy_score(y_test, prediction),
            "Precision": precision_score(y_test, prediction, pos_label="Cammeo"),
            "Recall": recall_score(y_test, prediction, pos_label="Cammeo"),
            "F1 Score": f1_score(y_test, prediction, pos_label="Cammeo"),
            "ROC-AUC": roc_auc_score((y_test == "Cammeo").astype(int), probability),
        })
        fitted[name] = model
    table = pd.DataFrame(results).sort_values("Accuracy", ascending=False).reset_index(drop=True)
    table.to_csv(OUTPUT / "baseline_model_comparison.csv", index=False)
    return table, fitted


def select_features(X_train, y_train) -> pd.DataFrame:
    """Rank features using three complementary feature-selection methods."""
    forest = RandomForestClassifier(n_estimators=500, random_state=RANDOM_STATE, n_jobs=-1)
    forest.fit(X_train, y_train)
    rfe = RFE(LogisticRegression(max_iter=2000, random_state=RANDOM_STATE), n_features_to_select=1)
    rfe.fit(StandardScaler().fit_transform(X_train), y_train)
    mutual_information = mutual_info_classif(X_train, y_train, random_state=RANDOM_STATE)
    feature_table = pd.DataFrame({
        "Feature": X_train.columns,
        "Random Forest Importance": forest.feature_importances_,
        "Mutual Information": mutual_information,
        "RFE Rank (1 is best)": rfe.ranking_,
    }).sort_values("Random Forest Importance", ascending=False).reset_index(drop=True)
    feature_table.to_csv(OUTPUT / "feature_selection_results.csv", index=False)

    plt.figure(figsize=(9, 5))
    sns.barplot(data=feature_table, x="Random Forest Importance", y="Feature", hue="Feature", legend=False)
    plt.title("Random Forest Feature Importance")
    save_figure("04_feature_importance.png")
    return feature_table


def compare_lightweight_models(X_train, X_test, y_train, y_test, ranking: list[str]) -> tuple[pd.DataFrame, dict]:
    """Compare 3, 5 and 7 feature SVM versions to quantify simplification."""
    results, fitted = [], {}
    for number in [3, 5, len(ranking)]:
        selected = ranking[:number]
        model = Pipeline([
            ("scaler", StandardScaler()),
            ("classifier", SVC(kernel="rbf", C=1.0, probability=True, random_state=RANDOM_STATE)),
        ])
        model.fit(X_train[selected], y_train)
        prediction = model.predict(X_test[selected])
        results.append({
            "Number of Features": number,
            "Features": ", ".join(selected),
            "Accuracy": accuracy_score(y_test, prediction),
            "F1 Score": f1_score(y_test, prediction, pos_label="Cammeo"),
        })
        fitted[number] = model
    table = pd.DataFrame(results)
    table.to_csv(OUTPUT / "lightweight_feature_comparison.csv", index=False)

    plt.figure(figsize=(7, 5))
    sns.lineplot(data=table, x="Number of Features", y="Accuracy", marker="o", linewidth=2.5)
    plt.ylim(max(0.8, table["Accuracy"].min() - 0.02), 1.005)
    plt.title("Accuracy Versus Number of Features")
    plt.xticks(table["Number of Features"])
    save_figure("05_lightweight_tradeoff.png")
    return table, fitted


def tune_and_save_final_model(X_train, X_test, y_train, y_test, selected: list[str]) -> dict:
    """Tune the final lightweight SVM, report errors, and persist the pipeline."""
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", SVC(probability=True, random_state=RANDOM_STATE)),
    ])
    search = GridSearchCV(
        pipeline,
        {"classifier__C": [0.1, 1, 10, 50], "classifier__gamma": ["scale", 0.01, 0.1, 1]},
        scoring="f1_weighted",
        cv=5,
        # Keep tuning in this interpreter: the installed pyarrow DLL prevents
        # spawned worker processes from importing scikit-learn.
        n_jobs=1,
    )
    search.fit(X_train[selected], y_train)
    final_model = search.best_estimator_
    prediction = final_model.predict(X_test[selected])
    probability = final_model.predict_proba(X_test[selected])[:, list(final_model.classes_).index("Cammeo")]

    ConfusionMatrixDisplay.from_predictions(y_test, prediction, cmap="Blues")
    plt.title("Final Lightweight SVM: Confusion Matrix")
    save_figure("06_final_confusion_matrix.png")

    actual_binary = (y_test == "Cammeo").astype(int)
    fpr, tpr, _ = roc_curve(actual_binary, probability)
    plt.figure(figsize=(6, 5))
    plt.plot(fpr, tpr, label=f"AUC = {roc_auc_score(actual_binary, probability):.4f}")
    plt.plot([0, 1], [0, 1], "--", color="gray")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("Final Lightweight SVM: ROC Curve")
    plt.legend(loc="lower right")
    save_figure("07_final_roc_curve.png")

    errors = X_test[selected].copy()
    errors["Actual"] = y_test
    errors["Predicted"] = prediction
    errors["Correct"] = errors["Actual"] == errors["Predicted"]
    errors.loc[~errors["Correct"]].to_csv(OUTPUT / "misclassified_test_samples.csv", index=False)

    report = classification_report(y_test, prediction, output_dict=True)
    metrics = {
        "selected_features": selected,
        "best_parameters": search.best_params_,
        "cross_validation_f1_weighted": float(search.best_score_),
        "test_accuracy": float(accuracy_score(y_test, prediction)),
        "test_precision_cammeo": float(precision_score(y_test, prediction, pos_label="Cammeo")),
        "test_recall_cammeo": float(recall_score(y_test, prediction, pos_label="Cammeo")),
        "test_f1_cammeo": float(f1_score(y_test, prediction, pos_label="Cammeo")),
        "test_roc_auc": float(roc_auc_score(actual_binary, probability)),
        "test_errors": int((prediction != y_test).sum()),
        "test_samples": int(len(y_test)),
        "classification_report": report,
    }
    with open(OUTPUT / "final_model_metrics.json", "w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=2)
    joblib.dump({"model": final_model, "features": selected}, MODELS / "lightweight_rice_svm.joblib")
    return metrics


def main() -> None:
    OUTPUT.mkdir(exist_ok=True)
    FIGURES.mkdir(exist_ok=True)
    MODELS.mkdir(exist_ok=True)
    df = load_data()
    features = df.drop(columns="Class").columns.tolist()
    overview = make_eda(df, features)
    X, y = df[features], df["Class"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y
    )
    baseline, _ = evaluate_models(X_train, X_test, y_train, y_test)
    feature_table = select_features(X_train, y_train)
    ranking = feature_table["Feature"].tolist()
    lightweight, _ = compare_lightweight_models(X_train, X_test, y_train, y_test, ranking)

    # The top three inputs match the strongest reduced-set baseline while using
    # less than half of the original measurements.
    final_features = ranking[:3]
    final_metrics = tune_and_save_final_model(X_train, X_test, y_train, y_test, final_features)
    overview["baseline_best_model"] = baseline.iloc[0]["Model"]
    overview["baseline_best_accuracy"] = float(baseline.iloc[0]["Accuracy"])
    overview["lightweight_results"] = lightweight.to_dict(orient="records")
    overview["final_model"] = final_metrics
    with open(OUTPUT / "project_summary.json", "w", encoding="utf-8") as file:
        json.dump(overview, file, indent=2)

    print("Project completed successfully.")
    print(f"Final selected features: {', '.join(final_features)}")
    print(f"Final test accuracy: {final_metrics['test_accuracy']:.4f}")
    print(f"Outputs saved to: {OUTPUT}")


if __name__ == "__main__":
    main()
