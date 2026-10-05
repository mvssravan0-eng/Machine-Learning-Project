# Rice Variety Classification Using Lightweight Machine Learning

An end-to-end machine learning project to classify **Cammeo** and **Osmancik** rice varieties based on their morphological measurements. Developed as part of the Machine Learning curriculum at Anil Neerukonda Institute of Technology and Sciences (ANITS), Department of CSE (AI & ML).

## 👥 Team Members (Team 15)
* **MALLADI VENKATA SUBRAHMANYA SRAVAN** (A24126552268)
* **DWARAPUDI SUSWETHA** (A24126552079)
* **ROHITH GURUGUBELLI** (A24126552112)
* **KOYYA APPALA REDDY** (A24126552089)

**Project Guide:** Dr. Appala Srinuvasu Muttipati (Associate Professor, ANITS)

## 📌 Overview
Visual identification of rice varieties can be time-consuming and inconsistent. This project leverages a dataset of image-derived physical measurements to build a lightweight machine learning classifier. The goal is to accurately distinguish between the two varieties while actively reducing the number of input features required, making the final model more practical for potential real-world downstream sensing applications.

## 📊 Key Results & Models
We evaluated multiple models (Random Forest, Logistic Regression, SVM, KNN, Decision Tree, and XGBoost). 
* **Top Performer:** **XGBoost** achieved the highest baseline accuracy at **91.99%**.
* **Lightweight Model:** We successfully created a highly efficient **Support Vector Machine (SVM)** that uses only **3 features** (Major Axis Length, Perimeter, and Area) instead of the full 7. It achieved a highly competitive test accuracy of **91.21%** and an ROC-AUC of **97.39%**, effectively reducing input complexity by 57%.

## 📂 Repository Structure
* `/rice_classification_project/` - The core ML environment.
  * `run_project.py` - The main pipeline script that loads the data, trains baseline models, selects features, tunes the final SVM, and generates the metrics/graphs.
  * `predict_rice.py` - An interactive command-line tool to make predictions using the trained `.joblib` model.
  * `outputs/` - Generated models, CSV metrics, error analysis, and visualization figures.
  * `Final_Project_Report_v4.docx` - The fully formatted, automated final project report containing all experiments and outputs.
* `/document folder/` - Contains the custom Python automation scripts used to programmatically generate and format the `.docx` project report.
* `/rice+cammeo+and+osmancik/` - The original source dataset in `.arff` format.

## 🚀 How to Run
1. Ensure you have Python installed along with `scikit-learn`, `xgboost`, `pandas`, `matplotlib`, and `seaborn`.
2. Navigate to the `rice_classification_project` folder.
3. Run the main pipeline to train the models and generate outputs:
   ```bash
   python run_project.py
   ```
4. Test the model with custom inputs:
   ```bash
   python predict_rice.py
   ```
