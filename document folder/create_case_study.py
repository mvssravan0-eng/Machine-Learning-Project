from pathlib import Path
import csv
import json

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor


BASE = Path(__file__).resolve().parent
OUT = BASE / "Rice_Variety_Classification_Case_Study.docx"
METRICS = json.loads((BASE / "outputs/final_model_metrics.json").read_text(encoding="utf-8"))
SUMMARY = json.loads((BASE / "outputs/project_summary.json").read_text(encoding="utf-8"))
TEAM = [
    ("A24126552268", "MALLADI VENKATA SUBRAHMANYA SRAVAN"),
    ("A24126552079", "DWARAPUDI SUSWETHA"),
    ("A24126552112", "ROHITH GURUGUBELLI"),
    ("A24126552089", "KOYYA APPALA REDDY"),
]

doc = Document()
sec = doc.sections[0]
sec.top_margin = Inches(.72)
sec.bottom_margin = Inches(.72)
sec.left_margin = Inches(.85)
sec.right_margin = Inches(.85)
styles = doc.styles
styles['Normal'].font.name = 'Times New Roman'
styles['Normal'].font.size = Pt(11)
styles['Normal'].paragraph_format.space_after = Pt(6)
for nm, size, color in [('Title', 24, '17365D'), ('Heading 1', 17, '17365D'), ('Heading 2', 13, '1F4E79'), ('Heading 3', 11, '1F4E79')]:
    st = styles[nm]
    st.font.name = 'Times New Roman'; st.font.size = Pt(size); st.font.bold = True
    st.font.color.rgb = RGBColor.from_string(color)

def p(text='', bold=False, italic=False, align=None, size=None):
    q = doc.add_paragraph()
    if align is not None: q.alignment = align
    r = q.add_run(text); r.bold = bold; r.italic = italic
    if size: r.font.size = Pt(size)
    return q

def heading(text, level=1): doc.add_heading(text, level=level)

def bullets(items):
    for item in items: doc.add_paragraph(item, style='List Bullet')

def numbered(items):
    for item in items: doc.add_paragraph(item, style='List Number')

def table(headers, rows, widths=None):
    t = doc.add_table(rows=1, cols=len(headers)); t.style = 'Table Grid'; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(headers):
        cell=t.rows[0].cells[i]; cell.text=str(h); cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
        for r in cell.paragraphs[0].runs: r.bold=True; r.font.color.rgb=RGBColor(255,255,255)
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        sh=OxmlElement('w:shd'); sh.set(qn('w:fill'),'1F4E79'); cell._tc.get_or_add_tcPr().append(sh)
    for row in rows:
        cells=t.add_row().cells
        for i, val in enumerate(row):
            cells[i].text=str(val); cells[i].vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
    doc.add_paragraph()
    return t

def image(name, caption, width=6.0):
    f=BASE/'outputs'/'figures'/name
    if f.exists():
        q=doc.add_paragraph(); q.alignment=WD_ALIGN_PARAGRAPH.CENTER
        q.add_run().add_picture(str(f), width=Inches(width))
        p(caption, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, size=9)

def page(): doc.add_page_break()

# Cover
p('ANIL NEERUKONDA INSTITUTE OF TECHNOLOGY AND SCIENCES', True, align=WD_ALIGN_PARAGRAPH.CENTER, size=16)
p('(UGC AUTONOMOUS)', True, align=WD_ALIGN_PARAGRAPH.CENTER)
p('Permanently Affiliated to Andhra University | Approved by AICTE | Accredited by NBA and NAAC', align=WD_ALIGN_PARAGRAPH.CENTER, size=9)
p('Sangivalasa, Bheemunipatnam Mandal, Visakhapatnam District, Andhra Pradesh – 531162', align=WD_ALIGN_PARAGRAPH.CENTER, size=9)
for _ in range(3): p('')
p('LIGHTWEIGHT RICE VARIETY CLASSIFICATION', True, align=WD_ALIGN_PARAGRAPH.CENTER, size=23)
p('A CASE STUDY REPORT', True, align=WD_ALIGN_PARAGRAPH.CENTER, size=17)
p('Machine Learning: Cammeo and Osmancik Classification', italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, size=13)
for _ in range(2): p('')
p('Submitted in partial fulfillment of the requirements for the project case study', align=WD_ALIGN_PARAGRAPH.CENTER)
p('BACHELOR OF TECHNOLOGY', True, align=WD_ALIGN_PARAGRAPH.CENTER, size=14)
p('Department of Computer Science and Engineering (AI & ML)', True, align=WD_ALIGN_PARAGRAPH.CENTER)
p('Submitted by', bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
for reg, name in TEAM: p(f'{name}  ({reg})', align=WD_ALIGN_PARAGRAPH.CENTER)
for _ in range(2): p('')
p('Academic Year 2026–2027', True, align=WD_ALIGN_PARAGRAPH.CENTER)
page()

# Certificate
p('ANIL NEERUKONDA INSTITUTE OF TECHNOLOGY AND SCIENCES', True, align=WD_ALIGN_PARAGRAPH.CENTER, size=14)
p('(UGC AUTONOMOUS)', True, align=WD_ALIGN_PARAGRAPH.CENTER)
p('DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING (AI & ML)', True, align=WD_ALIGN_PARAGRAPH.CENTER)
heading('CERTIFICATE', 1)
p('This is to certify that the case study report entitled “LIGHTWEIGHT RICE VARIETY CLASSIFICATION” is a bonafide record of work carried out by the following students of the Department of Computer Science and Engineering (AI & ML), Anil Neerukonda Institute of Technology and Sciences, during the academic year 2026–2027.')
table(['S. No.','Registration No.','Name'], [[str(i+1),reg,name] for i,(reg,name) in enumerate(TEAM)])
p('The work presents a machine-learning study using morphological measurements to classify Cammeo and Osmancik rice grains. The report is submitted in partial fulfillment of the applicable academic requirements.')
p('')
table(['PROJECT GUIDE','HEAD OF THE DEPARTMENT'], [['Signature: ____________________\nName: ________________________\nDesignation: __________________','Signature: ____________________\nDr. K. Selvani Deepthi\nHead, Department of CSE (AI & ML)']])
p('Date: ____________________                                      Place: Visakhapatnam', italic=True)
page()

heading('DECLARATION',1)
p('We hereby declare that this case study report entitled “LIGHTWEIGHT RICE VARIETY CLASSIFICATION” is our original academic work. The project uses a supplied dataset of rice grain measurements and reports the methods, implementation outputs, and evaluation results generated for this study. Sources used for dataset provenance and technical concepts are acknowledged in the References section.')
p('We further declare that this report has not been submitted, in full or in part, for the award of any other degree, diploma, or similar qualification at this or any other institution.')
p('')
p('Place: Visakhapatnam\nDate: 03-10-2026')
table(['Registration No.','Student name','Signature'], [[reg,name,'__________________'] for reg,name in TEAM])
page()

heading('ACKNOWLEDGEMENT',1)
p('We express our sincere gratitude to the faculty and staff of the Department of Computer Science and Engineering (AI & ML), Anil Neerukonda Institute of Technology and Sciences, for providing the academic environment and facilities required to complete this case study.')
p('We thank our faculty guide for guidance and feedback on problem formulation, experimental design, and interpretation of the results. We also acknowledge the creators and maintainers of the Rice Cammeo and Osmancik dataset and the open-source Python libraries used in the implementation.')
p('Finally, we thank our classmates and families for their encouragement and support throughout this work.')
p('TEAM MEMBERS',True,align=WD_ALIGN_PARAGRAPH.CENTER)
for reg,name in TEAM: p(f'{name} ({reg})')
page()

heading('ABSTRACT',1)
p('This case study develops a lightweight machine-learning classifier for identifying two rice varieties, Cammeo and Osmancik, from seven image-derived morphological measurements. The dataset contains 3,810 records, with no missing values or duplicate rows. The work includes exploratory analysis, stratified train-test partitioning, comparison of five baseline classifiers, feature ranking, reduced-input model comparison, hyperparameter tuning, and error analysis. A radial-basis-function Support Vector Machine using Major Axis Length, Perimeter, and Area was selected as the compact model. On the held-out set of 762 grains it achieved 91.21% accuracy, 97.39% ROC-AUC, and weighted five-fold cross-validation F1 of 93.27%. It used three of seven measurements, a 57.1% reduction in required inputs. The best all-feature baseline, Random Forest, achieved 91.86% accuracy, a difference of 0.65 percentage points. Results show that a compact input set can retain competitive performance for these two classes, while errors and dataset scope limit generalization claims.')
p('Keywords: rice classification, machine learning, feature selection, support vector machine, lightweight model', italic=True)
page()

heading('TABLE OF CONTENTS',1)
toc = [
'Abstract','1. Introduction','2. Objectives and Research Questions','3. Problem Identification','4. Dataset and Data Preparation','5. Methodology and Algorithm Design','6. Step-by-Step Experimental Demonstration','7. Complexity and Resource Analysis','8. Comparative Analysis','9. System Architecture and Implementation','10. Results and Discussion','11. Conclusion and Future Work','12. Learning Outcomes','References']
for x in toc: p(x)
p('Note: Update page numbers and the automatic table of contents in Word after editing.', italic=True, size=9)
page()

heading('1. INTRODUCTION',1)
heading('1.1 Context and motivation',2)
p('Rice is a staple crop, and distinguishing varieties can support quality control, sorting, and agricultural analysis. Visual identification by people can be time-consuming and inconsistent. Image-derived measurements provide a numerical basis for automated classification.')
heading('1.2 Machine learning for grain classification',2)
p('A supervised classifier learns a relationship between measured grain properties and known variety labels. Once trained, it can predict the class of a new observation with the same input definitions. In this study the target is binary: Cammeo or Osmancik.')
heading('1.3 Lightweight classification',2)
p('A model that relies on fewer measurements may reduce sensing and data-entry effort. It can also simplify a downstream measurement pipeline. Lightweight design is treated here as feature reduction while retaining useful predictive performance; it does not mean the model is universally optimal for all rice varieties or imaging environments.')
heading('1.4 Scope',2)
p('The experiments use the supplied Rice Cammeo and Osmancik ARFF dataset, a fixed stratified 80:20 split, five baseline algorithms, three feature-selection approaches, and a tuned SVM. The study is an offline benchmark, not a deployed grading system.')

heading('2. OBJECTIVES AND RESEARCH QUESTIONS',1)
heading('2.1 Objectives',2)
numbered(['Inspect dataset size, feature types, class balance, missingness, and duplicate records.','Compare Logistic Regression, K-Nearest Neighbors, Support Vector Machine, Decision Tree, and Random Forest on a common held-out test set.','Rank measurements using Random Forest importance, mutual information, and Recursive Feature Elimination.','Compare SVM variants using the top 3, top 5, and all 7 measurements.','Tune and save a compact final classifier; report its performance and errors.'])
heading('2.2 Research questions',2)
numbered(['Which baseline classifier gives the strongest held-out performance?','Which measurements are most useful for distinguishing the two varieties?','How much performance is retained when the input set is reduced?','What limitations are visible in the final test results?'])

heading('3. PROBLEM IDENTIFICATION',1)
heading('3.1 Problem statement',2)
p('Given a vector of physical measurements for one rice grain, predict whether its label is Cammeo or Osmancik. The practical challenge is that the two classes have overlapping measurement distributions, while several size-related inputs carry correlated information.')
heading('3.2 Challenges',2)
bullets(['Moderate class imbalance: 2,180 Osmancik records and 1,630 Cammeo records.','Correlated size variables can add redundancy to the feature set.','Different features have different numerical scales, requiring scaling for distance- and margin-based models.','A model can perform well on this dataset yet degrade under changes in cameras, image processing, or population.'])
heading('3.3 Success criteria',2)
p('The project considers held-out accuracy, class-specific precision and recall, F1 score, ROC-AUC, cross-validation performance, number of required features, and error count. No single score is treated as sufficient by itself.')

heading('4. DATASET AND DATA PREPARATION',1)
heading('4.1 Dataset profile',2)
p('The input file is Rice_Cammeo_Osmancik.arff, provided in the workspace. Each row describes one grain and includes seven numerical measurements plus a categorical class label.')
table(['Property','Value'], [['Records','3,810'],['Input features','7'],['Cammeo','1,630'],['Osmancik','2,180'],['Missing values','0'],['Duplicate rows','0']])
heading('4.2 Feature definitions',2)
table(['Feature','Interpretation'], [['Area','Number of image pixels occupied by the grain; a size measure.'],['Perimeter','Length around the grain boundary.'],['Major Axis Length','Length of the longest axis.'],['Minor Axis Length','Length of the shortest axis.'],['Eccentricity','Elongation measure derived from the grain shape.'],['Convex Area','Area of the smallest convex enclosure.'],['Extent','Grain area relative to its bounding rectangle.'],['Class','Target label: Cammeo or Osmancik.']])
heading('4.3 Split and preprocessing',2)
p('The implementation uses an 80:20 stratified split with random_state=42: 3,048 observations for training and 762 for testing. Stratification preserves class proportions. StandardScaler is placed inside each model pipeline so that the scaler is fitted on training data and applied consistently to held-out data.')
heading('4.4 Exploratory analysis',2)
p('Exploratory plots show the class counts, distributions of selected shape features, and pairwise feature correlations. Size features are strongly related, motivating the feature-reduction experiment.')
image('01_class_distribution.png','Figure 4.1. Class distribution in the dataset.',5.5)
image('02_key_feature_boxplots.png','Figure 4.2. Selected measurement distributions by rice variety.',6.0)
image('03_feature_correlation.png','Figure 4.3. Correlation among numerical input measurements.',5.6)

heading('5. METHODOLOGY AND ALGORITHM DESIGN',1)
heading('5.1 Processing pipeline',2)
numbered(['Read the ARFF file and decode class labels.','Validate dimensions, missing values, duplicates, and class counts.','Separate the seven input columns from the target label.','Create a reproducible stratified train-test split.','Train and compare five baseline models with standardized inputs.','Rank features and compare SVM performance for 3, 5, and 7 inputs.','Tune the final three-feature SVM using five-fold cross-validation.','Evaluate once on the held-out test set, save plots and metrics, and serialize the model.'])
heading('5.2 Baseline algorithms',2)
table(['Algorithm','Role in comparison'], [['Logistic Regression','Linear probabilistic baseline.'],['K-Nearest Neighbors','Local similarity-based classifier.'],['Support Vector Machine','Margin-based classifier; final compact model uses an RBF kernel.'],['Decision Tree','Rule-based nonlinear classifier.'],['Random Forest','Ensemble of decision trees; strongest baseline accuracy.']])
heading('5.3 Feature selection',2)
p('Random Forest impurity importance provides a model-based ranking; mutual information measures feature-target dependence; and RFE recursively eliminates features using Logistic Regression. The final reduced set follows the leading Random Forest ranking: Major Axis Length, Perimeter, and Area.')
feature_rows=[]
with (BASE/'outputs/feature_selection_results.csv').open(encoding='utf-8-sig',newline='') as f:
    for rank, r in enumerate(csv.DictReader(f), 1):
        label=r['Feature'].replace('_',' ')
        feature_rows.append([rank,label,f"{float(r['Random Forest Importance']):.4f}",f"{float(r['Mutual Information']):.4f}",r['RFE Rank (1 is best)']])
table(['Rank','Feature','RF importance','Mutual information','RFE rank'],feature_rows)
image('04_feature_importance.png','Figure 5.1. Random Forest feature importance.',5.8)
heading('5.4 Final model tuning',2)
p('The final classifier is an SVM with an RBF kernel and StandardScaler in a pipeline. GridSearchCV explores C in {0.1, 1, 10, 50} and gamma in {scale, 0.01, 0.1, 1}, using weighted F1 and five-fold cross-validation. The saved result selected C=10 and gamma=0.01. The complete preprocessing and classifier pipeline is serialized for repeatable prediction.')

heading('6. STEP-BY-STEP EXPERIMENTAL DEMONSTRATION',1)
heading('6.1 Baseline comparison',2)
baseline=[]
import csv
with (BASE/'outputs/baseline_model_comparison.csv').open(encoding='utf-8-sig',newline='') as f:
    for r in csv.DictReader(f):
        baseline.append([r['Model'],f"{float(r['Accuracy'])*100:.2f}%",f"{float(r['Precision'])*100:.2f}%",f"{float(r['Recall'])*100:.2f}%",f"{float(r['F1 Score'])*100:.2f}%",f"{float(r['ROC-AUC'])*100:.2f}%"])
table(['Model','Accuracy','Precision*','Recall*','F1*','ROC-AUC'],baseline)
p('*Class-specific metrics use Cammeo as the positive class.',italic=True,size=9)
heading('6.2 Lightweight feature experiment',2)
light=[]
with (BASE/'outputs/lightweight_feature_comparison.csv').open(encoding='utf-8-sig',newline='') as f:
    for r in csv.DictReader(f): light.append([r['Number of Features'],r['Features'],f"{float(r['Accuracy'])*100:.2f}%",f"{float(r['F1 Score'])*100:.2f}%"])
table(['Inputs','Feature subset','Accuracy','Cammeo F1'],light)
image('05_lightweight_tradeoff.png','Figure 6.1. Test accuracy against number of input features.',5.3)
heading('6.3 Final tuned model',2)
p(f"Grid search selected C={METRICS['best_parameters']['classifier__C']} and gamma={METRICS['best_parameters']['classifier__gamma']}. Mean weighted F1 across five cross-validation folds was {METRICS['cross_validation_f1_weighted']*100:.2f}%. On the 762-item test set, accuracy was {METRICS['test_accuracy']*100:.2f}%, ROC-AUC was {METRICS['test_roc_auc']*100:.2f}%, and {METRICS['test_errors']} predictions were incorrect.")
heading('6.4 Confusion matrix and ROC curve',2)
image('06_final_confusion_matrix.png','Figure 6.2. Confusion matrix for the final three-feature SVM.',5.4)
image('07_final_roc_curve.png','Figure 6.3. ROC curve for the final model.',5.0)

heading('7. COMPLEXITY AND RESOURCE ANALYSIS',1)
heading('7.1 Input and storage reduction',2)
p('The final classifier consumes three of seven measurements. This reduces the number of required input values by (7−3)/7 = 57.14%. It also lowers feature preparation and scaling work relative to a seven-feature pipeline. The model file is saved as lightweight_rice_svm.joblib.')
heading('7.2 Computational considerations',2)
p('For n training observations, d features, and S support vectors, prediction with an RBF SVM generally requires work proportional to dS kernel evaluations per observation, with additional cost to compute each kernel. Reducing d from seven to three lowers the input dimension for those calculations, although actual latency depends on the support-vector count, implementation, and hardware. Training cost for kernel SVMs can grow substantially with sample count; this work is an offline training experiment.')
heading('7.3 Validation design',2)
p('Five-fold cross-validation is used only within the training partition for hyperparameter selection. The test partition remains held out for final evaluation. The reported scores estimate performance for a split drawn from this dataset and do not establish performance under dataset shift.')

heading('8. COMPARATIVE ANALYSIS',1)
heading('8.1 Best baseline versus compact model',2)
table(['Model','Inputs','Test accuracy','Notes'], [['Random Forest baseline','7','91.86%','Highest baseline accuracy.'],['Tuned RBF SVM','3','91.21%','57.1% fewer inputs; ROC-AUC 97.39%.']])
p('The accuracy difference is 0.65 percentage points. The compact model is selected for the project’s reduced-input objective, while the Random Forest remains the strongest result when maximizing baseline accuracy alone.')
heading('8.2 Three, five, and seven feature SVMs',2)
p('In the untuned comparison, the three-feature SVM achieved the highest accuracy among tested feature counts. Adding the selected fourth and fifth inputs, or all seven features, did not improve that test result. The final tuned three-feature result is evaluated separately and should not be conflated with the baseline feature-count comparison.')
heading('8.3 Interpretation',2)
p('The results suggest that size and length measurements carry much of the information needed to separate these two classes. Correlation among size-related variables offers a plausible reason that additional features do not necessarily improve the classifier. This interpretation is specific to the supplied data and split.')

heading('9. SYSTEM ARCHITECTURE AND IMPLEMENTATION',1)
heading('9.1 Software components',2)
table(['Component','Purpose'], [['Data loader','Reads the ARFF dataset and decodes class labels.'],['EDA module','Creates class, distribution, and correlation summaries and plots.'],['Training pipeline','Fits baseline classifiers and feature-selection methods.'],['Tuning and evaluation','Runs grid search, generates metrics, confusion matrix, and ROC curve.'],['Artifact output','Writes CSV/JSON summaries and a serialized model.']])
heading('9.2 Reproducibility',2)
p('The experiment uses a fixed random seed (42), a saved train-test split definition, explicit model parameters, and machine-readable outputs. The main implementation is run_project.py. The model artifact stores both the fitted pipeline and its expected feature names.')
heading('9.3 Prediction interface',2)
p('predict_rice.py is provided as a command-line example for entering grain measurements and obtaining a prediction. The final model requires Major_Axis_Length, Perimeter, and Area in the expected units and order. Predictions outside the two known classes should not be interpreted as a third class.')

heading('10. RESULTS AND DISCUSSION',1)
heading('10.1 Summary of measured results',2)
table(['Metric','Result'], [['Selected measurements','Major Axis Length, Perimeter, Area'],['Best parameters','C = 10; gamma = 0.01'],['Five-fold CV weighted F1','93.27%'],['Test accuracy','91.21%'],['Cammeo precision','91.37%'],['Cammeo recall','87.73%'],['Cammeo F1','89.51%'],['Test ROC-AUC','97.39%'],['Test errors','67 / 762']])
heading('10.2 Error analysis',2)
p('The final model made 67 incorrect predictions. Cammeo recall (87.73%) is lower than Osmancik recall (93.81%), indicating that a larger fraction of actual Cammeo test examples were missed. The overlap in grain measurements likely contributes to these mistakes, but individual error causes require further review of source images and measurement quality.')
heading('10.3 Limitations and validity',2)
bullets(['Only two rice varieties are represented; the classifier cannot identify other varieties.','Measurements are derived from images, and changes in imaging, segmentation, or measurement units may affect predictions.','A single held-out split provides limited evidence about variation across samples; repeated or external validation would strengthen the estimate.','The selected feature ranking and accuracy are dataset-dependent.','The compact SVM is not proven to be faster or cheaper on every deployment platform; runtime and memory should be benchmarked for the target device.'])

heading('11. CONCLUSION AND FUTURE WORK',1)
heading('11.1 Conclusion',2)
p('The project built and evaluated a binary classifier for Cammeo and Osmancik rice using seven morphological measurements. Among the baseline models, Random Forest gave the highest test accuracy at 91.86%. Feature ranking and reduced-input experiments led to a tuned three-feature RBF SVM using Major Axis Length, Perimeter, and Area. It achieved 91.21% test accuracy and 97.39% ROC-AUC, with 67 errors among 762 held-out examples. The result retains competitive accuracy while reducing the measured inputs by 57.1%.')
heading('11.2 Future work',2)
bullets(['Evaluate with repeated stratified cross-validation and an independent dataset.','Measure inference time, memory use, and end-to-end sensing cost on a target device.','Study calibration and class-specific decision thresholds where false negatives and false positives have different costs.','Test robustness to image resolution, lighting, segmentation, and measurement noise.','Extend the dataset and method to additional rice varieties only after collecting representative labeled examples.'])

heading('12. LEARNING OUTCOMES',1)
table(['Area','Demonstrated competency'], [['Data preparation','Read ARFF data, inspect quality, and create stratified partitions.'],['Machine learning','Train and compare linear, neighbor-based, tree, ensemble, and margin-based classifiers.'],['Feature engineering','Use feature ranking and quantify reduced-input performance.'],['Model evaluation','Interpret accuracy, class-specific precision/recall/F1, ROC-AUC, and confusion matrix.'],['Responsible interpretation','Describe error patterns, dataset boundaries, and generalization limits.'],['Implementation','Save plots, tabular metrics, and a reusable prediction pipeline.']])

heading('REFERENCES',1)
refs=[
'Rice Cammeo and Osmancik dataset, supplied project file: Rice_Cammeo_Osmancik.arff. Dataset originally associated with the UCI Machine Learning Repository; verify bibliographic citation and license against the instructor-provided source before formal publication.',
'Cortes, C. and Vapnik, V. (1995). Support-vector networks. Machine Learning, 20, 273–297.',
'Pedregosa, F. et al. (2011). Scikit-learn: Machine Learning in Python. Journal of Machine Learning Research, 12, 2825–2830.',
'Breiman, L. (2001). Random Forests. Machine Learning, 45, 5–32.',
'SciPy documentation, ARFF file format and scipy.io.arff module.',
'Project implementation and generated experiment artifacts: run_project.py, outputs/baseline_model_comparison.csv, outputs/feature_selection_results.csv, outputs/final_model_metrics.json, and outputs/project_summary.json.'
]
numbered(refs)

# Header/footer
for s in doc.sections:
    header=s.header.paragraphs[0]; header.text='LIGHTWEIGHT RICE VARIETY CLASSIFICATION | CASE STUDY'; header.alignment=WD_ALIGN_PARAGRAPH.CENTER
    for r in header.runs: r.font.name='Times New Roman'; r.font.size=Pt(8); r.font.color.rgb=RGBColor(100,100,100)
    footer=s.footer.paragraphs[0]; footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
    run=footer.add_run('ANITS • CSE (AI & ML) • Academic Year 2026–2027     |     Page '); run.font.size=Pt(8)
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    fld=OxmlElement('w:fldSimple'); fld.set(qn('w:instr'),'PAGE'); footer._p.append(fld)

doc.core_properties.title='Lightweight Rice Variety Classification Case Study'
doc.core_properties.subject='Cammeo and Osmancik classification using a lightweight SVM'
doc.core_properties.author=', '.join(n for _,n in TEAM)
doc.save(OUT)
print(OUT)
