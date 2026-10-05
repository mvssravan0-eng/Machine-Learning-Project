"""Interactive predictor for the final lightweight rice-variety model."""

from pathlib import Path
import sys
import types
import joblib
import pandas as pd

# See run_project.py: this avoids a broken optional pyarrow DLL during the
# scikit-learn import triggered while loading the saved model.
try:
    import pyarrow  # noqa: F401
except ImportError:
    pyarrow = types.ModuleType("pyarrow")
    pyarrow.__version__ = "17.0.0"
    sys.modules["pyarrow"] = pyarrow

MODEL_PATH = Path(__file__).resolve().parent / "outputs" / "models" / "lightweight_rice_svm.joblib"


def main() -> None:
    artifact = joblib.load(MODEL_PATH)
    model, features = artifact["model"], artifact["features"]
    print("Rice Variety Predictor")
    print("Enter physical measurements for one grain.\n")
    values = {}
    for feature in features:
        values[feature] = float(input(f"{feature}: "))
    sample = pd.DataFrame([values])
    predicted_class = model.predict(sample)[0]
    probabilities = model.predict_proba(sample)[0]
    confidence = probabilities[list(model.classes_).index(predicted_class)]
    print(f"\nPredicted rice variety: {predicted_class}")
    print(f"Confidence: {confidence:.2%}")


if __name__ == "__main__":
    main()
