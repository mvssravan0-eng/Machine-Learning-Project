# Rice Variety Classification Using Lightweight Machine Learning

## 1. Problem statement

This project classifies individual rice grains as **Cammeo** or **Osmancik** from physical and morphological measurements. The main goal is to identify a small group of highly useful measurements and build a model that remains accurate while needing fewer inputs.

## 2. Dataset

The supplied Rice Cammeo and Osmancik dataset was used directly from `Rice_Cammeo_Osmancik.arff`.

| Item | Result |
|---|---:|
| Total records | 3,810 |
| Input features | 7 |
| Target classes | Cammeo, Osmancik |
| Cammeo records | 1,630 |
| Osmancik records | 2,180 |
| Missing values | 0 |
| Duplicate rows | 0 |

The input measurements are Area, Perimeter, Major Axis Length, Minor Axis Length, Eccentricity, Convex Area, and Extent. An 80:20 stratified train-test split was used, giving 3,048 training samples and 762 unseen test samples.

## 3. Exploratory data analysis

The class distribution is moderately uneven, with more Osmancik observations, so stratified splitting was used. No values were missing and no duplicate records were found. The correlation plot shows that area-related measurements have strong relationships with each other, which supports the aim of removing redundant input features.

Generated visuals:

- `outputs/figures/01_class_distribution.png`
- `outputs/figures/02_key_feature_boxplots.png`
- `outputs/figures/03_feature_correlation.png`

## 4. Baseline model comparison

All seven features were standardized where needed. Five classifiers were trained and evaluated on the same unseen test set.

| Model | Accuracy | Precision (Cammeo) | Recall (Cammeo) | F1 score | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| XGBoost | 91.99% | 92.60% | 88.34% | 90.42% | 97.39% |
| Random Forest | 91.86% | 92.58% | 88.04% | 90.25% | 97.18% |
| Logistic Regression | 91.60% | 91.72% | 88.34% | 90.00% | 97.50% |
| Support Vector Machine | 91.08% | 91.35% | 87.42% | 89.34% | 95.62% |
| K-Nearest Neighbors | 90.94% | 90.54% | 88.04% | 89.27% | 94.90% |
| Decision Tree | 89.76% | 88.51% | 87.42% | 87.96% | 89.47% |

XGBoost produced the highest baseline test accuracy at 91.99%. Logistic Regression had the strongest ROC-AUC, indicating strong separation between the two varieties.

## 5. Feature selection

Three methods were used: Random Forest importance, mutual information, and Recursive Feature Elimination (RFE). Random Forest ranked the features in this order:

1. Major Axis Length
2. Perimeter
3. Area
4. Convex Area
5. Eccentricity
6. Minor Axis Length
7. Extent

The first three features were selected for the final lightweight model because they delivered the strongest reduced-feature baseline result while reducing the inputs from seven to three. This is a 57% reduction in the number of required measurements.

The complete feature-selection results are in `outputs/feature_selection_results.csv`, and the plot is `outputs/figures/04_feature_importance.png`.

## 6. Lightweight model comparison

Support Vector Machine models were tested with the top 3, top 5, and all 7 features.

| Number of features | Feature subset | Accuracy | F1 score (Cammeo) |
|---:|---|---:|---:|
| 3 | Major Axis Length, Perimeter, Area | 91.47% | 89.80% |
| 5 | Top 3 + Convex Area, Eccentricity | 91.21% | 89.51% |
| 7 | All features | 91.08% | 89.34% |

The three-feature version achieved the highest baseline accuracy among the SVM variants. Adding more inputs did not improve this result on the test set. The comparison chart is saved as `outputs/figures/05_lightweight_tradeoff.png`.

## 7. Final model

The final model is a Support Vector Machine using only Major Axis Length, Perimeter, and Area. A grid search with five-fold cross-validation tuned its parameters.

| Metric | Final result |
|---|---:|
| Selected features | 3 |
| Best hyperparameters | C = 50, gamma = 0.1 |
| Five-fold CV weighted F1 | 93.31% |
| Test accuracy | 91.21% |
| Test precision, Cammeo | 92.54% |
| Test recall, Cammeo | 85.89% |
| Test F1, Cammeo | 89.09% |
| Test ROC-AUC | 95.96% |
| Incorrect test predictions | 67 of 762 |

The full Random Forest has a marginally higher accuracy of 91.86%, but it requires every input feature and is more complex. The final SVM uses only three measurements and gives 91.21% accuracy, a difference of 0.66 percentage points. It is therefore the preferred lightweight solution.

The saved final model is `outputs/models/lightweight_rice_svm.joblib`. Its confusion matrix, ROC curve, metrics, and incorrect test rows are available in the output folder.

## 8. Error analysis and limitations

The final model misclassified 67 of 762 unseen grains. The lower Cammeo recall means some Cammeo grains have shape and size values that overlap with Osmancik grains. The dataset contains image-derived measurements, so model performance may differ if measurement quality changes in a new imaging setup. The model distinguishes only the two varieties represented in this dataset and should not be used to identify other rice varieties.

## 9. Conclusion

The project successfully developed a rice-variety classifier and reduced the required features from seven to three. Major Axis Length, Perimeter, and Area carry enough information to achieve 91.21% test accuracy after tuning. The final lightweight SVM provides a practical balance between accuracy, simplicity, and deployment cost.
