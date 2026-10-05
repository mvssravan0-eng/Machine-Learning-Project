# Lightweight Rice Variety Classification

This project classifies a rice grain as **Cammeo** or **Osmancik** from its measured shape features. It compares six baseline machine-learning models, including XGBoost, ranks feature importance, compares reduced feature sets, tunes a final lightweight SVM model, and saves it for predictions.

## Run the project

From `D:\Machine Learning Project`:

```powershell
python rice_classification_project/run_project.py
```

All charts, result tables, metrics, error-analysis data, and the saved final model are created in `rice_classification_project/outputs`.

## Run a prediction

After running the project pipeline:

```powershell
python rice_classification_project/predict_rice.py
```

The predictor asks only for the five features selected for the lightweight final model.

## Project method

1. Load and inspect the provided `Rice_Cammeo_Osmancik.arff` dataset.
2. Create class-distribution, boxplot, and correlation visualizations.
3. Split data into stratified 80% training and 20% test sets.
4. Compare Logistic Regression, KNN, SVM, Decision Tree, Random Forest, and XGBoost.
5. Rank inputs through Random Forest importance, mutual information, and RFE.
6. Compare SVM accuracy with 3, 5, and all features.
7. Tune a five-feature SVM through five-fold cross-validation.
8. Save the model and analyse its test-set errors.
