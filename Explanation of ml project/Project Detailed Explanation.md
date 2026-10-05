# Project Detailed Explanation

## Lightweight Rice Variety Classification Using Machine Learning

**Project team:** Team 15  
**Dataset:** Rice (Cammeo and Osmancik)  
**Project type:** Binary classification with feature selection and lightweight deployment

---

## 1. Project overview

This project creates a machine-learning system that identifies the variety of a rice grain from measurements of its shape and size. The system predicts one of two classes:

- **Cammeo**
- **Osmancik**

The main requirement is not only to build an accurate classifier. The project also needs a **lightweight model**: a model that uses fewer input measurements while preserving high prediction accuracy. Such a model is simpler, needs less data collection, and is easier to deploy.

The final project compares several algorithms, identifies the most useful grain measurements, tests models with fewer features, tunes the chosen model, analyses its errors, and saves it for future predictions.

---

## 2. Problem statement

Rice varieties can have similar visual appearances, making manual distinction difficult. Each grain has measurable physical properties such as area, perimeter, length, and width. This project uses those measurements to classify a grain automatically.

### Objective

> Predict whether a rice grain belongs to the Cammeo or Osmancik variety using its morphological measurements, then reduce the number of required features without causing a major loss in accuracy.

### Research questions

1. Which machine-learning algorithm gives the best classification performance?
2. Which physical measurements are most useful for distinguishing Cammeo and Osmancik rice?
3. Can a model using only a few selected measurements perform almost as well as a model using all measurements?

---

## 3. Dataset explanation

### 3.1 Dataset source and format

The project uses the supplied file:

`rice+cammeo+and+osmancik/Rice_Cammeo_Osmancik.arff`

An **ARFF** file (Attribute-Relation File Format) is a text-based dataset format commonly used in machine learning. It contains two parts:

1. A header that defines the dataset name and each feature.
2. A `@DATA` section that contains the actual rows.

For example, the header declares a feature like this:

```text
@ATTRIBUTE Area Integer
```

Each row in the data section describes one rice grain. The final value in each row is its known class label, Cammeo or Osmancik.

### 3.2 Dataset size and quality

| Dataset property | Value |
|---|---:|
| Total rice-grain records | 3,810 |
| Input features | 7 |
| Target classes | 2 |
| Cammeo records | 1,630 |
| Osmancik records | 2,180 |
| Missing values | 0 |
| Duplicate rows | 0 |

The classes are moderately unbalanced because Osmancik has more observations. This is handled by using a **stratified train-test split**, which preserves the same class proportion in the training and test datasets.

### 3.3 Feature definitions

| Feature | Type | Explanation |
|---|---|---|
| `Area` | Integer | Number of image pixels occupied by the rice grain. It represents grain size. |
| `Perimeter` | Real number | Length around the outer boundary of the grain. |
| `Major_Axis_Length` | Real number | Length of the longest axis of the grain. It is closely related to grain length. |
| `Minor_Axis_Length` | Real number | Length of the shortest axis of the grain. It is closely related to grain width. |
| `Eccentricity` | Real number | Shows how elongated the grain is. Values closer to 1 indicate a more elongated shape. |
| `Convex_Area` | Integer | Area of the smallest convex shape enclosing the grain. |
| `Extent` | Real number | Ratio of the grain area to the area of its bounding rectangle. |
| `Class` | Category | The output to predict: `Cammeo` or `Osmancik`. |

The first seven columns are input variables, usually called **X**. The `Class` column is the output or target, usually called **y**.

---

## 4. How the dataset is read in Python

The dataset is loaded using the `arff` reader provided by SciPy, then converted into a Pandas DataFrame.

```python
import pandas as pd
from scipy.io import arff

data, metadata = arff.loadarff(
    "rice+cammeo+and+osmancik/Rice_Cammeo_Osmancik.arff"
)

df = pd.DataFrame(data)
df["Class"] = df["Class"].str.decode("utf-8")
```

### Explanation of this code

- `arff.loadarff(...)` reads the ARFF file.
- The returned `data` contains the rows, and `metadata` contains information about the fields.
- `pd.DataFrame(data)` turns the data into a table that can be analysed easily.
- ARFF text values are read as bytes, such as `b'Cammeo'`. The `decode("utf-8")` line turns them into normal text such as `Cammeo`.

The following checks were then used:

```python
print(df.shape)
print(df.head())
print(df.isnull().sum())
print(df.duplicated().sum())
print(df["Class"].value_counts())
print(df.describe())
```

These commands answer important questions before model training: how large the dataset is, whether data is missing, whether duplicate records exist, whether both classes are represented, and the range of each measurement.

---

## 5. Exploratory data analysis

Exploratory Data Analysis (EDA) is done before model building to understand patterns in the data.

### 5.1 Class distribution

A count plot shows how many Cammeo and Osmancik samples exist. This confirms that both classes have enough data for training, although Osmancik is more frequent.

```python
sns.countplot(data=df, x="Class", hue="Class", legend=False)
plt.title("Rice Variety Distribution")
```

### 5.2 Boxplots

Boxplots compare the distribution of each feature across the two rice classes. They show whether the two varieties tend to have different areas, perimeters, lengths, or widths.

```python
sns.boxplot(data=df, x="Class", y="Major_Axis_Length",
            hue="Class", legend=False)
```

If the boxplots of the two classes are well separated, that feature is likely useful for classification. If they overlap heavily, it is less useful on its own.

### 5.3 Correlation heatmap

The correlation heatmap measures how strongly numerical features move together.

```python
sns.heatmap(df.drop(columns="Class").corr(), annot=True,
            cmap="coolwarm", center=0)
```

Area, Convex Area, Perimeter, and Major Axis Length are related size measurements. Strongly related features can contain overlapping information. This is one reason feature selection is useful for this project.

The generated EDA figures are saved in `outputs/figures`.

---

## 6. Data preparation

### 6.1 Separate inputs and target

```python
X = df.drop(columns="Class")
y = df["Class"]
```

`X` contains all numerical grain measurements. `y` contains the correct rice class for each row.

### 6.2 Training and test split

```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.20,
    random_state=42,
    stratify=y
)
```

| Set | Percentage | Number of rows | Purpose |
|---|---:|---:|---|
| Training set | 80% | 3,048 | Used to learn patterns and tune the model. |
| Test set | 20% | 762 | Kept unseen until final evaluation. |

`random_state=42` makes the split reproducible. `stratify=y` makes sure the class ratio is similar in both groups.

### 6.3 Feature scaling

Measurements have very different numerical ranges. For example, area is in thousands, while eccentricity is less than one. Models such as KNN, SVM, and Logistic Regression can be affected by this difference. Therefore, StandardScaler was used inside a machine-learning pipeline.

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

model = Pipeline([
    ("scaler", StandardScaler()),
    ("classifier", SVC(probability=True))
])
```

StandardScaler transforms each input so that its training-set mean is approximately 0 and standard deviation is approximately 1. The pipeline prevents test-data information from leaking into model training.

---

## 7. Baseline model building

Five algorithms were trained using all seven features. This is necessary because one model alone cannot prove that it is the best choice.

| Algorithm | Why it was included |
|---|---|
| Logistic Regression | A simple linear classification baseline. |
| K-Nearest Neighbors (KNN) | Predicts based on the most similar nearby grains. |
| Support Vector Machine (SVM) | Effective at finding a decision boundary between two classes. |
| Decision Tree | Easy to interpret and able to learn non-linear rules. |
| Random Forest | An ensemble of decision trees; usually robust and accurate for tabular data. |

### Evaluation metrics

| Metric | Meaning |
|---|---|
| Accuracy | Percentage of all test predictions that are correct. |
| Precision | Of grains predicted as Cammeo, the percentage truly Cammeo. |
| Recall | Of all actual Cammeo grains, the percentage correctly found. |
| F1 score | Balance between precision and recall. |
| ROC-AUC | Ability to separate the two classes across different decision thresholds. |

### Baseline results

| Model | Accuracy | Precision (Cammeo) | Recall (Cammeo) | F1 score | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| Random Forest | 91.86% | 92.58% | 88.04% | 90.25% | 97.18% |
| Logistic Regression | 91.60% | 91.72% | 88.34% | 90.00% | 97.50% |
| Support Vector Machine | 91.08% | 91.35% | 87.42% | 89.34% | 95.62% |
| K-Nearest Neighbors | 90.94% | 90.54% | 88.04% | 89.27% | 94.90% |
| Decision Tree | 89.76% | 88.51% | 87.42% | 87.96% | 89.47% |

The Random Forest gave the highest baseline accuracy. Logistic Regression produced the highest ROC-AUC. Both results show that the physical measurements can distinguish the two rice types well.

---

## 8. Feature selection: making the model lightweight

The project title requires a lightweight model. A lightweight model needs fewer features and less computation while keeping useful accuracy.

Three feature-selection methods were used:

### 8.1 Random Forest feature importance

Random Forest calculates how much each feature helps reduce uncertainty during its decision-tree splits. A higher score means the feature contributes more to correct predictions.

### 8.2 Mutual information

Mutual information measures the relationship between each feature and the target class. A larger value means knowing that feature gives more information about whether the grain is Cammeo or Osmancik.

### 8.3 Recursive Feature Elimination (RFE)

RFE repeatedly trains a model, removes the least useful feature, and ranks features by importance. A rank of 1 means the feature was selected earliest as important.

### Feature-selection results

| Rank by Random Forest | Feature | Random Forest importance | Mutual information | RFE rank |
|---:|---|---:|---:|---:|
| 1 | Major Axis Length | 0.2903 | 0.4993 | 3 |
| 2 | Perimeter | 0.2401 | 0.4798 | 4 |
| 3 | Area | 0.1571 | 0.4035 | 6 |
| 4 | Convex Area | 0.1558 | 0.4019 | 1 |
| 5 | Eccentricity | 0.0847 | 0.2339 | 2 |
| 6 | Minor Axis Length | 0.0401 | 0.0778 | 5 |
| 7 | Extent | 0.0319 | 0.0407 | 7 |

Major Axis Length, Perimeter, and Area were selected as the final lightweight input set. They represent important length, boundary, and size information.

---

## 9. Testing reduced feature sets

An SVM was trained with different numbers of top-ranked features to measure the trade-off between simplicity and performance.

| Features used | Input variables | Accuracy | F1 score (Cammeo) |
|---:|---|---:|---:|
| 3 | Major Axis Length, Perimeter, Area | 91.47% | 89.80% |
| 5 | Top 3 plus Convex Area and Eccentricity | 91.21% | 89.51% |
| 7 | All original features | 91.08% | 89.34% |

The three-feature version produced the best baseline SVM accuracy. Therefore, adding the remaining measurements did not improve the SVM on this test split.

The final model reduces inputs from seven to three. This is a **57% feature reduction**:

```text
Reduction = (7 - 3) / 7 × 100 = 57.14%
```

---

## 10. Hyperparameter tuning and final model

The final model is a Support Vector Machine using only these features:

```text
Major_Axis_Length, Perimeter, Area
```

The model was optimized using GridSearchCV, which tries several combinations of SVM settings and selects the combination with the best five-fold cross-validation weighted F1 score.

```python
GridSearchCV(
    pipeline,
    {
        "classifier__C": [0.1, 1, 10, 50],
        "classifier__gamma": ["scale", 0.01, 0.1, 1]
    },
    scoring="f1_weighted",
    cv=5
)
```

`C` controls how strongly the SVM tries to classify all training records correctly. `gamma` controls how closely the decision boundary follows individual data points.

### Final tuned-model results

| Metric | Result |
|---|---:|
| Best `C` | 50 |
| Best `gamma` | 0.1 |
| Five-fold cross-validation weighted F1 | 93.31% |
| Test accuracy | 91.21% |
| Precision for Cammeo | 92.54% |
| Recall for Cammeo | 85.89% |
| F1 score for Cammeo | 89.09% |
| ROC-AUC | 95.96% |
| Incorrect predictions | 67 out of 762 test rows |

The complete seven-feature Random Forest is slightly more accurate at 91.86%. However, the final SVM needs only three features and loses only 0.66 percentage points of accuracy. It is selected because it provides the intended balance between high performance and low complexity.

---

## 11. Error analysis

The final model made 67 incorrect predictions out of 762 unseen test samples. The prediction errors are saved in:

`outputs/misclassified_test_samples.csv`

The model has lower recall for Cammeo than for Osmancik. This means some Cammeo grains have values similar to Osmancik grains and are predicted as Osmancik. This overlap is expected when two physical objects have related shapes and sizes.

The confusion matrix shows the exact number of correct and incorrect predictions for each class. The ROC curve shows that the model still separates the classes very well overall, with an ROC-AUC of 95.96%.

---

## 12. Final prediction system

The trained final model is saved at:

`outputs/models/lightweight_rice_svm.joblib`

The program `predict_rice.py` loads the saved model and asks a user for only the three selected measurements. It then prints the predicted variety and confidence.

Run it from the main project folder:

```powershell
python rice_classification_project/predict_rice.py
```

Example input and output:

```text
Major_Axis_Length: 229.75
Perimeter: 525.58
Area: 15231

Predicted rice variety: Cammeo
Confidence: 99.99%
```

The predictor was tested successfully using a dataset sample labelled Cammeo.

---

## 13. Project files and what they contain

| File or folder | Purpose |
|---|---|
| `run_project.py` | Full reproducible ML pipeline. It loads data, makes plots, trains models, selects features, tunes the final model, and saves outputs. |
| `predict_rice.py` | Simple console prediction interface for the final saved model. |
| `PROJECT_REPORT.md` | Short report containing methodology, results, and conclusion. |
| `Project Detailed Explanation.docx` | This detailed document for submission and presentation preparation. |
| `outputs/baseline_model_comparison.csv` | Metrics from the five baseline models. |
| `outputs/feature_selection_results.csv` | Feature importance and selection results. |
| `outputs/lightweight_feature_comparison.csv` | Comparison of models using 3, 5, and 7 features. |
| `outputs/final_model_metrics.json` | Final tuned model metrics and hyperparameters. |
| `outputs/figures` | EDA, feature importance, trade-off, confusion matrix, and ROC charts. |

---

## 14. Conclusion

The project successfully classifies Cammeo and Osmancik rice grains from physical shape measurements. Five algorithms were evaluated, and Random Forest gave the highest full-feature accuracy of 91.86%.

For the lightweight requirement, feature selection identified Major Axis Length, Perimeter, and Area as the most useful inputs. A tuned SVM using only these three features achieved 91.21% accuracy and a 95.96% ROC-AUC on unseen data. This removes 57% of the original input features while retaining performance close to the strongest full model.

The project therefore demonstrates that rice variety can be classified accurately with a small, practical set of morphological measurements.

---

## 15. Short viva explanation

If asked to explain the project orally, use this summary:

> Our project classifies rice grains into Cammeo and Osmancik varieties using seven image-derived shape features. We first cleaned and explored 3,810 records, then trained and compared Logistic Regression, KNN, SVM, Decision Tree, and Random Forest. Random Forest gave the best full-feature accuracy of 91.86%. Since our project requires a lightweight model, we used Random Forest importance, mutual information, and RFE to identify the most useful features. Major Axis Length, Perimeter, and Area were selected. A tuned SVM using only these three features achieved 91.21% accuracy and 95.96% ROC-AUC. This reduced the required features by 57% while keeping performance very close to the full model. We also saved the final model and created a predictor that returns the rice class and confidence for new grain measurements.
