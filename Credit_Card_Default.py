#!/usr/bin/env python
# coding: utf-8

# In[1]:


get_ipython().run_line_magic('matplotlib', 'inline')
get_ipython().run_line_magic('config', "InlineBackend.figure_format = 'retina'")


# In[2]:


import matplotlib.pyplot as plt
import seaborn as sns
import warnings

plt.style.use('seaborn')
plt.rcParams['figure.figsize'] = [8, 4.5]
plt.rcParams['figure.dpi'] = 300
warnings.simplefilter(action='ignore', category=FutureWarning)


# In[13]:


import sklearn 
sklearn.__version__


# # Advanced Machine Learning Models in Finance

# All the recipes use `scikit-learn` version `0.21` (unless specified otherwise). From `0.22`, the default settings of selected estimators are changed. For example, in the case of the `RandomForestClassifier`, the default setting of `n_estimators` was changed from 10 to 100. This will cause discrepancies with the results presented in the book.

# ## Investigating advanced classifiers

# ### Getting Ready

# Prepare the Pipeline:

# In[3]:


import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.tree import DecisionTreeClassifier
from sklearn.pipeline import Pipeline
from chapter_9_utils import performance_evaluation_report

from sklearn.tree import DecisionTreeClassifier, export_graphviz
from sklearn import metrics


# In[4]:


df = pd.read_csv('credit_card_default.csv', index_col=0, na_values='')

X = df.copy()
y = X.pop('default_payment_next_month')

X_train, X_test, y_train, y_test = train_test_split(X, y, 
                                                    test_size=0.2, 
                                                    stratify=y, 
                                                    random_state=42)

num_features = X_train.select_dtypes(include='number').columns.to_list()
cat_features = X_train.select_dtypes(include='object').columns.to_list()

num_pipeline = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median'))
])

cat_list = [list(X_train[column].dropna().unique()) for column in cat_features]

cat_pipeline = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('onehot', OneHotEncoder(categories=cat_list, sparse=False, 
                             handle_unknown='error', drop='first'))
])

preprocessor = ColumnTransformer(transformers=[
    ('numerical', num_pipeline, num_features),
    ('categorical', cat_pipeline, cat_features)],
    remainder='drop')

tree_pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                                ('classifier', DecisionTreeClassifier(random_state=42))])

tree_pipeline.fit(X_train, y_train)

LABELS = ['No Default', 'Default']
tree_perf = performance_evaluation_report(tree_pipeline, X_test, 
                                          y_test, labels=LABELS, 
                                          show_plot=True, 
                                          show_pr_curve=True)


# In[5]:


tree_perf


# In[6]:


# investigate the depth of the tree
tree_classifier = tree_pipeline.named_steps['classifier']
tree_classifier.tree_.max_depth


# ### How to do it...

# 1. Import the libraries:

# In[7]:


from sklearn.ensemble import (RandomForestClassifier, 
                              GradientBoostingClassifier)
from xgboost.sklearn import XGBClassifier
from lightgbm import LGBMClassifier


# 2. Create a Random Forest Pipeline:

# In[8]:


rf = RandomForestClassifier(random_state=42)
rf_pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                              ('classifier', rf)
                             ])

rf_pipeline.fit(X_train, y_train)
rf_perf = performance_evaluation_report(rf_pipeline, X_test, 
                                        y_test, labels=LABELS, 
                                        show_plot=True,
                                        show_pr_curve=True)

# plt.savefig('images/ch9_im1.png', dpi=300)
plt.show()


# 3. Create a Gradient Boosting Trees Pipeline:

# In[9]:


gbt =  GradientBoostingClassifier(random_state=42)
gbt_pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                               ('classifier', gbt)
                              ])

gbt_pipeline.fit(X_train, y_train)
gbt_perf = performance_evaluation_report(gbt_pipeline, X_test, 
                                         y_test, labels=LABELS, 
                                         show_plot=True,
                                         show_pr_curve=True)

# plt.savefig('images/ch9_im2.png', dpi=300)
plt.show()


# 4. Create a xgBoost Pipeline:

# In[10]:


xgb = XGBClassifier(random_state=42)
xgb_pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                               ('classifier', xgb)
                              ])

xgb_pipeline.fit(X_train, y_train)
xgb_perf = performance_evaluation_report(xgb_pipeline, X_test, 
                                         y_test, labels=LABELS, 
                                         show_plot=True,
                                         show_pr_curve=True)

# plt.savefig('images/ch9_im3.png', dpi=300)
plt.show()


# 5. Create a LightGBM classifier Pipeline:

# In[11]:


lgbm = LGBMClassifier(random_state=42)
lgbm_pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                                ('classifier', lgbm)
                               ])

lgbm_pipeline.fit(X_train, y_train)
lgbm_perf = performance_evaluation_report(lgbm_pipeline, X_test, 
                                          y_test, labels=LABELS, 
                                          show_plot=True,
                                          show_pr_curve=True)

# plt.savefig('images/ch9_im4.png', dpi=300)
plt.show()


# ### There's more

# Below we go over the most important hyperparameters of the considered models and show a possible way of tuning them using Randomized Search. With more complex models, the training time is significantly longer than with the basic Decision Tree, so we need to find a balance between the time we want to spend on tuning the hyperparameters and the expected results. Also, bear in mind that changing the values of some parameters (such as learning rate or the number of estimators) can itself influence the training time of the models.
# 
# To have the results in a reasonable amount of time, we used the Randomized Search with 100 different sets of hyperparameters for each model (the number of actually fitted models is higher due to cross-validation). Just as in the recipe *Grid Search and Cross-Validation*, we used recall as the criterion for selecting the best model. Additionally, we used the scikit-learn compatible APIs of XGBoost and LightGBM to make the process as easy to follow as possible. For a complete list of hyperparameters and their meaning, please refer to corresponding documentations.

# In[ ]:


from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold
from sklearn import metrics
import numpy as np

N_SEARCHES = 100
k_fold = StratifiedKFold(5, shuffle=True, random_state=42)


# **Random Forest**

# When tuning the Random Forest classifier, we look at the following hyperparameters (there are more available for tuning):
# * `n_estimators` - the number of decision trees in a forest. The goal is to find a balance between improved accuracy and computational cost.
# * `max_features` - the maximum number of features considered for splitting a node. The default is the square root of the number of features. When None, all features are considered.
# * `max_depth` - the maximum number of levels in each decision tree
# * `min_samples_split` - the minimum number of observations required to split each node. When set to high it may cause underfitting, as the trees will not split enough times.
# * `min_samples_leaf` - the minimum number of data points allowed in a leaf. Too small a value might cause overfitting, while large values might prevent the tree from growing and cause underfitting.
# * `bootstrap` - whether to use bootstrapping for each tree in the forest
# 
# We define the grid below:

# In[ ]:


rf_param_grid = {'classifier__n_estimators': np.linspace(100, 1000, 10, dtype=int),
                 'classifier__max_features': ['log2', 'sqrt', None],
                 'classifier__max_depth': np.arange(3, 11, 1, dtype=int),
                 'classifier__min_samples_split': [2, 5, 10],
                 'classifier__min_samples_leaf': np.arange(1, 51, 2, dtype=int),
                 'classifier__bootstrap': [True, False]}


# And use the randomized search to tune the classifier:

# In[ ]:


rf_rs =  RandomizedSearchCV(rf_pipeline, rf_param_grid, scoring='recall', 
                                       cv=k_fold, n_jobs=-1, verbose=1, 
                                       n_iter=N_SEARCHES, random_state=42)

rf_rs.fit(X_train, y_train)

print(f'Best parameters: {rf_rs.best_params_}') 
print(f'Recall (Training set): {rf_rs.best_score_:.4f}') 
print(f'Recall (Test set): {metrics.recall_score(y_test, rf_rs.predict(X_test)):.4f}')


# In[ ]:


rf_rs_perf = performance_evaluation_report(rf_rs, X_test, 
                                           y_test, labels=LABELS, 
                                           show_plot=True,
                                           show_pr_curve=True)


# **Gradient Boosted Trees**

# As Gradient Boosted Trees are also an ensemble method built on top of decision trees, a lot of the parameters are the same as in the case of the Random Forest. The new one is the learning rate, which is used in the gradient descent algorithm to control the rate of descent towards the minimum of the loss function. When tuning the tree manually, we should consider this hyperparameter together with the number of estimators, as reducing the learning rate (the learning is slower), while increasing the number of estimators can increase the computation time significantly.
# 
# We define the grid as follows:

# In[ ]:


gbt_param_grid = {'classifier__n_estimators': np.linspace(100, 1000, 10, dtype=int),
                  'classifier__learning_rate': np.arange(0.05, 0.31, 0.05),
                  'classifier__max_depth': np.arange(3, 11, 1, dtype=int),
                  'classifier__min_samples_split': np.linspace(0.1, 0.5, 12),
                  'classifier__min_samples_leaf': np.arange(1, 51, 2, dtype=int),
                  'classifier__max_features':['log2', 'sqrt', None]}


# And run the randomized search:

# In[ ]:


gbt_rs =  RandomizedSearchCV(gbt_pipeline, gbt_param_grid, scoring='recall', 
                             cv=k_fold, n_jobs=-1, verbose=1, 
                             n_iter=N_SEARCHES, random_state=42)

gbt_rs.fit(X_train, y_train)

print(f'Best parameters: {gbt_rs.best_params_}') 
print(f'Recall (Training set): {gbt_rs.best_score_:.4f}') 
print(f'Recall (Test set): {metrics.recall_score(y_test, gbt_rs.predict(X_test)):.4f}')


# In[ ]:


gbt_rs_perf = performance_evaluation_report(gbt_rs, X_test, 
                                            y_test, labels=LABELS, 
                                            show_plot=True,
                                            show_pr_curve=True)


# **XGBoost**

# The scikit-learn API of XGBoost makes sure that the hyperparameters are named similarly to their equivalents other scikit-learn's classifiers. So the XGBoost native eta hyperparameter is called learning_rate in scikit-learn's API. 
# 
# The new hyperparameters we consider for this example are:
# * `min_child_weight` - indicates the minimum sum of weights of all observations required in a child. This hyperparameter is used for controlling overfitting. Cross-validation should be used for tuning.
# * `colsample_bytree` - indicates the fraction of columns to be randomly sampled for each tree.
# 
# We define the grid as:

# In[ ]:


xgb_param_grid = {'classifier__n_estimators': np.linspace(100, 1000, 10, dtype=int),
                  'classifier__learning_rate': np.arange(0.05, 0.31, 0.05),
                  'classifier__max_depth': np.arange(3, 11, 1, dtype=int),
                  'classifier__min_child_weight': np.arange(1, 8, 1, dtype=int),
                  'classifier__colsample_bytree': np.linspace(0.3, 1, 7)}


# For defining ranges of parameters that are restricted (such as colsample_bytree which cannot be higher than 1.0) it is better to use `np.linspace` rather than `np.arange`, because the latter allows for some inconsistencies when the step is defined as floating-point. For example, the last value might be 1.0000000002, which then causes an error while training the classifier.

# In[ ]:


xgb_rs =  RandomizedSearchCV(xgb_pipeline, xgb_param_grid, scoring='recall', 
                             cv=k_fold, n_jobs=-1, verbose=1, 
                             n_iter=N_SEARCHES, random_state=42)

xgb_rs.fit(X_train, y_train)

print(f'Best parameters: {xgb_rs.best_params_}') 
print(f'Recall (Training set): {xgb_rs.best_score_:.4f}') 
print(f'Recall (Test set): {metrics.recall_score(y_test, xgb_rs.predict(X_test)):.4f}')


# In[ ]:


xgb_rs_perf = performance_evaluation_report(xgb_rs, X_test, 
                                            y_test, labels=LABELS, 
                                            show_plot=True,
                                            show_pr_curve=True)


# **LightGBM**

# We tune the same parameters as in XGBoost, though more is definitely possible and encouraged. The grid is defined as follows:

# In[ ]:


lgbm_param_grid = {'classifier__n_estimators': np.linspace(100, 1000, 10, dtype=int),
                   'classifier__learning_rate': np.arange(0.05, 0.31, 0.05),
                   'classifier__max_depth': np.arange(3, 11, 1, dtype=int),
                   'classifier__colsample_bytree': np.linspace(0.3, 1, 7)}


# In[ ]:


lgbm_rs =  RandomizedSearchCV(lgbm_pipeline, lgbm_param_grid, scoring='recall', 
                              cv=k_fold, n_jobs=-1, verbose=1, 
                              n_iter=N_SEARCHES, random_state=42)

lgbm_rs.fit(X_train, y_train)

print(f'Best parameters: {lgbm_rs.best_params_}') 
print(f'Recall (Training set): {lgbm_rs.best_score_:.4f}') 
print(f'Recall (Test set): {metrics.recall_score(y_test, lgbm_rs.predict(X_test)):.4f}')


# In[ ]:


lgbm_rs_perf = performance_evaluation_report(lgbm_rs, X_test, 
                                             y_test, labels=LABELS, 
                                             show_plot=True,
                                             show_pr_curve=True)


# Below we present a summary of all the classifiers we have considered in the last 3 recipes.

# In[ ]:


results_dict = {'decision_tree_baseline': tree_perf,
                'random_forest': rf_perf,
                'random_forest_rs': rf_rs_perf,
                'gradient_boosted_trees': gbt_perf,
                'gradient_boosted_trees_rs': gbt_rs_perf,
                'xgboost': xgb_perf,
                'xgboost_rs': xgb_rs_perf,
                'light_gbm': lgbm_perf,
                'light_gbm_rs': lgbm_rs_perf}

results_comparison = pd.DataFrame(results_dict).T
results_comparison


# In[47]:


results_comparison = pd.read_csv('results_comparison.csv')
results_comparison.rename(columns={'Unnamed: 0': 'model'}, inplace=True)
results_comparison


# ## Using stacking for improved performance

# ### Getting ready

# Make sure you are using `scikit-learn` 0.22 and above for this recipe.

# ### How to do it...

# 1. Import the libraries:

# In[ ]:


import pandas as pd
from sklearn.model_selection import (train_test_split,
                                     StratifiedKFold)
from sklearn import metrics
from sklearn.preprocessing import StandardScaler

from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import StackingClassifier
from sklearn.linear_model import LogisticRegression


# 2. Load and preprocess data:

# In[8]:


RANDOM_STATE = 42

k_fold = StratifiedKFold(5, shuffle=True, random_state=42)

df = pd.read_csv('credit_card_fraud.csv')

X = df.copy()
y = X.pop('Class')

X_train, X_test, y_train, y_test = train_test_split(X, y, 
                                                    test_size=0.2, 
                                                    stratify=y, 
                                                    random_state=RANDOM_STATE)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)


# 3. Define a list of classifiers to consider:

# In[9]:


clf_list = [('dec_tree', DecisionTreeClassifier(random_state=RANDOM_STATE)),
            ('log_reg', LogisticRegression()),
            ('knn', KNeighborsClassifier()),
            ('naive_bayes', GaussianNB())]


# 4. Iterate over the selected models, fit them to the data and calculate recall using the test set:

# In[10]:


for model_tuple in clf_list:
    model = model_tuple[1]
    if 'random_state' in model.get_params().keys():
        model.set_params(random_state=RANDOM_STATE)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    recall = metrics.recall_score(y_pred, y_test)
    print(f"{model_tuple[0]}'s recall score: {recall:.4f}")


# 5. Define and fit the stacking classifier:

# In[11]:


lr = LogisticRegression()
stack_clf = StackingClassifier(clf_list, 
                               final_estimator=lr,
                               cv=k_fold,
                               n_jobs=-1)
stack_clf.fit(X_train, y_train)


# 6. Create predictions and evaluate the stacked ensemble:

# In[12]:


y_pred = stacking_clf.predict(X_test)
recall = metrics.recall_score(y_pred, y_test)
print(f"The stacked ensemble's recall score: {recall:.4f}")


# ## Investigating the feature importance

# ### Getting Ready

# Please run the code for the *Investigating advanced classifiers* recipe before this one (you do not need to run the *There's more* section).
# 
# This recipe requires `scikit-learn` version `0.22`.

# ### How to do it...

# 1. Import the libraries:

# In[9]:


# from sklearn.inspection import permutation_importance
from sklearn.base import clone 
from eli5.sklearn import PermutationImportance


# 2. Extract the classifier and preprocessor from the pipeline:

# In[10]:


# in case we have the fitted grid search object `rf_rs`, we extract the best pipeline
# rf_pipeline = rf_rs.best_estimator_

rf_classifier = rf_pipeline.named_steps['classifier']
preprocessor = rf_pipeline.named_steps['preprocessor']

# in case we want to manually assign hyperparameters based on previous grid search
# best_parameters =  {'n_estimators': 400, 'min_samples_split': 2, 
#                     'min_samples_leaf': 49, 'max_features': None, 
#                     'max_depth': 20, 'bootstrap': True, 'random_state': 42}
# rf_classifier = rf_classifier.set_params(**best_parameters)


# 3. Recover feature names from the preprocessing transformer and transform the training data:

# In[11]:


feat_names = preprocessor.named_transformers_['categorical']                          .named_steps['onehot']                          .get_feature_names(
    input_features=cat_features
)
feat_names = np.r_[num_features, feat_names]

X_train_preprocessed = pd.DataFrame(
    preprocessor.transform(X_train), 
    columns=feat_names
)


# 4. Extract the default feature importance and calculate the cumulative importance:

# In[12]:


rf_feat_imp = pd.DataFrame(rf_classifier.feature_importances_,
                           index=feat_names,
                           columns=['mdi'])
rf_feat_imp = rf_feat_imp.sort_values('mdi', ascending=False)
rf_feat_imp['cumul_importance_mdi'] = np.cumsum(rf_feat_imp.mdi)


# 5. Define a function for plotting top X features in terms of their importance:

# In[28]:


def plot_most_important_features(feat_imp, method='MDI', 
                                 n_features=10, bottom=False):
    '''
    Function for plotting the top/bottom x features in terms of their importance.
    
    Parameters
    ----------
    feat_imp : pd.Series
        A pd.Series with calculated feature importances
    method : str
        A string representing the method of calculating the importances.
        Used for the title of the plot.
    n_features : int
        Number of top/bottom features to plot
    bottom : boolean
        Indicates if the plot should contain the bottom feature importances.
    
    Returns
    -------
    ax : matplotlib.axes._subplots.AxesSubplot
        Ax cointaining the plot
    '''
    
    if bottom:
        indicator = 'Bottom'
        feat_imp = feat_imp.sort_values(ascending=True)
    else:
        indicator = 'Top'
        feat_imp = feat_imp.sort_values(ascending=False)
        
    ax = feat_imp.head(n_features).plot.barh()
    ax.invert_yaxis()
    ax.set(title=('Feature importance - '
                  f'{method} ({indicator} {n_features})'), 
           xlabel='Importance', 
           ylabel='Feature')
    
    return ax


# In[29]:


plot_most_important_features(rf_feat_imp.mdi, 
                             method='MDI')

plt.tight_layout()
plt.savefig('images/ch9_im7.png', dpi=300)
plt.show()


# 6. Plot the cumulative importance of the features:

# In[32]:


x_values = range(len(feat_names))

fig, ax = plt.subplots()

ax.plot(x_values, rf_feat_imp.cumul_importance_mdi, 'b-')
ax.hlines(y = 0.95, xmin=0, xmax=len(x_values), 
          color = 'g', linestyles = 'dashed')
ax.set(title='Cumulative Importances', 
       xlabel='Variable', 
       ylabel='Importance')

plt.tight_layout()
plt.savefig('images/ch9_im8.png', dpi=300)
plt.show()


# In[33]:


print(f'Top 10 features account for {100 * rf_feat_imp.head(10).mdi.sum():.2f}% of the total importance.')
print(f'Top {rf_feat_imp[rf_feat_imp.cumul_importance_mdi <= 0.95].shape[0]} features account for 95% of importance.')


# 7. Calculate and plot permutation importance:

# In[34]:


perm = PermutationImportance(rf_classifier, n_iter = 25, 
                             random_state=42)
perm.fit(X_train_preprocessed, y_train)
rf_feat_imp['permutation'] = perm.feature_importances_


# In[35]:


plot_most_important_features(rf_feat_imp.permutation, 
                             method='Permutation')

plt.tight_layout()
plt.savefig('images/ch9_im9.png', dpi=300)
plt.show()


# 8. Define a function for calculating the drop-column feature importance:

# In[36]:


def drop_col_feat_imp(model, X, y, random_state = 42):
    '''
    Function for calculating the drop column feature importance.
    
    Parameters
    ----------
    model : scikit-learn's model
        Object representing the estimator with selected hyperparameters.
    X : pd.DataFrame
        Features for training the model
    y : pd.Series
        The target
    random_state : int
        Random state for reproducibility
        
    Returns
    -------
    importances : list
        List containing the calculated feature importances in the order of appearing in X
    
    '''
    
    model_clone = clone(model)
    model_clone.random_state = random_state
    model_clone.fit(X, y)
    benchmark_score = model_clone.score(X, y)
    
    importances = []
    
    for col in X.columns:
        model_clone = clone(model)
        model_clone.random_state = random_state
        model_clone.fit(X.drop(col, axis = 1), y)
        drop_col_score = model_clone.score(X.drop(col, axis = 1), 
                                           y)
        importances.append(benchmark_score - drop_col_score)
    
    return importances


# 9. Calculate and plot the drop-column feature importance:

# In[39]:


rf_feat_imp['drop_column'] = drop_col_feat_imp(
    rf_classifier, 
    X_train_preprocessed, 
    y_train, 
    random_state = 42
)


# In[40]:


plot_most_important_features(rf_feat_imp.drop_column, 
                             method='Drop column')

plt.tight_layout()
plt.savefig('images/ch9_im10.png', dpi=300)
plt.show()


# In[41]:


plot_most_important_features(rf_feat_imp.drop_column, 
                             method='Drop column', 
                             bottom=True)

plt.tight_layout()
plt.savefig('images/ch9_im11.png', dpi=300)
plt.show()


# ## Investigating different approaches to handling imbalanced data

# ### How to do it...

# 1. Import the libraries:

# In[23]:


import pandas as pd
import seaborn as sns
from imblearn.over_sampling import RandomOverSampler, SMOTE, ADASYN
from imblearn.under_sampling import RandomUnderSampler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from collections import Counter
from chapter_9_utils import performance_evaluation_report


# 2. Load and prepare data:

# In[24]:


df = pd.read_csv('credit_card_fraud.csv')

X = df.copy()
y = X.pop('Class')

RANDOM_STATE = 42

X_train, X_test, y_train, y_test = train_test_split(X, y, 
                                                    test_size=0.2, 
                                                    stratify=y, 
                                                    random_state=RANDOM_STATE)


# In[25]:


y.value_counts(normalize=True)


# 3. Train the baseline model:

# In[26]:


rf = RandomForestClassifier(random_state=RANDOM_STATE, n_jobs=-1)
rf.fit(X_train, y_train)


# In[27]:


rf_perf = performance_evaluation_report(rf, X_test, y_test, 
                                        show_plot=True, 
                                        show_pr_curve=True)


# In[28]:


rf_perf


# 4. Undersample the data and train a Random Forest Classifier:

# In[29]:


rus = RandomUnderSampler(random_state=RANDOM_STATE)
X_rus, y_rus = rus.fit_resample(X_train, y_train)
print(f'The new class proportions are: {dict(Counter(y_rus))}')

rf.fit(X_rus, y_rus)
rf_rus_perf = performance_evaluation_report(rf, X_test, y_test, 
                                            show_plot=True, 
                                            show_pr_curve=True)


# In[30]:


rf_rus_perf


# 5. Oversample the data and train a Random Forest Classifier:

# In[31]:


ros = RandomOverSampler(random_state=RANDOM_STATE)
X_ros, y_ros = ros.fit_resample(X_train, y_train)
print(f'The new class proportions are: {dict(Counter(y_ros))}')

rf.fit(X_ros, y_ros)
rf_ros_perf = performance_evaluation_report(rf, X_test, y_test, 
                                            show_plot=True, 
                                            show_pr_curve=True)


# In[32]:


rf_ros_perf


# 6. Oversample using SMOTE:

# In[33]:


X_smote, y_smote = SMOTE(random_state=RANDOM_STATE).fit_resample(X_train, y_train)
print(f'The new class proportions are: {dict(Counter(y_smote))}')
rf.fit(X_smote, y_smote)
rf_smote_perf = performance_evaluation_report(rf, X_test, y_test, 
                                              show_plot=True, 
                                              show_pr_curve=True)


# In[34]:


rf_smote_perf


# 7. Oversample using ADASYN:

# In[35]:


X_adasyn, y_adasyn = ADASYN(random_state=RANDOM_STATE).fit_resample(X_train, y_train)
print(f'The new class proportions are: {dict(Counter(y_adasyn))}')
rf.fit(X_adasyn, y_adasyn)
rf_adasyn_perf = performance_evaluation_report(rf, X_test, y_test, 
                                               show_plot=True, 
                                               show_pr_curve=True)


# In[36]:


rf_adasyn_perf


# 8. Use sample weights in the Random Forest Classifier:

# In[37]:


rf_cw = RandomForestClassifier(random_state=RANDOM_STATE, 
                               class_weight='balanced',
                               n_jobs=-1)
rf_cw.fit(X_train, y_train)
rf_cw_perf = performance_evaluation_report(rf_cw, X_test, y_test, 
                                           show_plot=True, 
                                           show_pr_curve=True)


# In[38]:


rf_cw_perf


# ### There's more

# 1. Import the library:

# In[39]:


from imblearn.ensemble import BalancedRandomForestClassifier


# 2. Train the `BalancedRandomForestClassifier`:

# In[40]:


balanced_rf = BalancedRandomForestClassifier(
    random_state=RANDOM_STATE
)

balanced_rf.fit(X_train, y_train)
balanced_rf_perf = performance_evaluation_report(balanced_rf, 
                                                 X_test, y_test, 
                                                 show_plot=True, 
                                                 show_pr_curve=True)


# 3. Train the `BalancedRandomForestClassifier` with balanced classes:

# In[41]:


balanced_rf_cw = BalancedRandomForestClassifier(
    random_state=RANDOM_STATE, 
    class_weight='balanced',
    n_jobs=-1
)

balanced_rf_cw.fit(X_train, y_train)
balanced_rf_cw_perf = performance_evaluation_report(balanced_rf_cw, 
                                                    X_test, y_test, 
                                                    show_plot=True, 
                                                    show_pr_curve=True)


# 4. Group the performance results into a DataFrame:

# In[42]:


performance_results = {'random_forest': rf_perf,
                       'undersampled rf': rf_rus_perf,
                       'oversampled_rf': rf_ros_perf,
                       'smote': rf_smote_perf,
                       'adasyn': rf_adasyn_perf,
                       'random_forest_cw': rf_cw_perf,
                       'balanced_random_forest': balanced_rf_perf,
                       'balanced_random_forest_cw': balanced_rf_cw_perf}
pd.DataFrame(performance_results).T


# ## Bayesian Hyperparameter Optimization

# ### How to do it...

# 1. Load the libraries:

# In[49]:


import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from hyperopt import hp, fmin, tpe, STATUS_OK, Trials
from sklearn.model_selection import (cross_val_score, 
                                     StratifiedKFold)
from lightgbm import LGBMClassifier
from chapter_9_utils import performance_evaluation_report
import pickle


# 2. Define parameters for later use:

# In[69]:


N_FOLDS = 5
MAX_EVALS = 200


# 3. Load and prepare the data:

# In[70]:


df = pd.read_csv('credit_card_fraud.csv')

X = df.copy()
y = X.pop('Class')

X_train, X_test, y_train, y_test = train_test_split(X, y, 
                                                    test_size=0.2, 
                                                    stratify=y, 
                                                    random_state=42)


# 4. Define the objective function:

# In[71]:


def objective(params, n_folds = N_FOLDS, random_state=42):
    
    model = LGBMClassifier(**params)
    model.set_params(random_state=random_state)
    
    k_fold = StratifiedKFold(n_folds, shuffle=True, 
                             random_state=random_state)
    
    metrics = cross_val_score(model, X_train, y_train, 
                              cv=k_fold, scoring='recall')
    loss = -1 * metrics.mean()
    
    return {'loss': loss, 'params': params, 'status': STATUS_OK}


# 5. Define the search space:

# In[72]:


lgbm_param_grid = {
    'boosting_type': hp.choice('boosting_type', ['gbdt', 'dart', 'goss']),
    'max_depth': hp.choice('max_depth', [-1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),
    'n_estimators': hp.choice('n_estimators', [10, 50, 100, 
                                               300, 750, 1000]),
    'is_unbalance': hp.choice('is_unbalance', [True, False]),
    'colsample_bytree': hp.uniform('colsample_bytree', 0.3, 1),
    'learning_rate': hp.uniform ('learning_rate', 0.05, 0.3),
}


# 6. Run the Bayesian optimization:

# In[ ]:


trials = Trials()
best_set = fmin(fn= objective,
                space= lgbm_param_grid,
                algo= tpe.suggest,
                max_evals = MAX_EVALS,
                trials= trials)


# In[73]:


# load if already finished the search
#best_set = pickle.load(open('best_set.p', 'rb'))
best_set


# 7. Define the dictionaries for mapping the results to hyperparameter values:

# In[74]:


boosting_type = {0: 'gbdt', 1: 'dart', 2: 'goss'}
max_depth = {0: -1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 
             6: 7, 7: 8, 8: 9, 9: 10}
n_estimators = {0: 10, 1: 50, 2: 100, 3: 300, 4: 750, 5: 1000}
is_unbalance = {0: True, 1: False}


# 8. Fit a model using the best hyperparameters:

# In[75]:


lgbm_param_grid = {'boosting_type': hp.choice('boosting_type', ['gbdt', 'dart', 'goss']),
                   'max_depth': hp.choice('max_depth', [-1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),
                   'n_estimators': hp.choice('n_estimators', [10, 50, 100, 300, 750, 1000]),
                   'is_unbalance': hp.choice('is_unbalance', [True, False]),
                   'colsample_bytree': hp.uniform('colsample_bytree', 0.3, 1),
                   'learning_rate': hp.uniform ('learning_rate', 0.05, 0.3),
                  }


# In[76]:


best_lgbm = LGBMClassifier(
    boosting_type = boosting_type[best_set['boosting_type']], 
    max_depth = max_depth[best_set['max_depth']], 
    n_estimators = n_estimators[best_set['n_estimators']], 
    is_unbalance = is_unbalance[best_set['is_unbalance']],
    colsample_bytree = best_set['colsample_bytree'], 
    learning_rate = best_set['learning_rate']
)
best_lgbm.fit(X_train, y_train)


# 9. Evaluate on the test set:

# In[79]:


_ = performance_evaluation_report(best_lgbm, X_test, y_test, 
                                  show_plot=True, 
                                  show_pr_curve=True)

plt.savefig('images/ch9_im13.png', dpi=300)
plt.show()


# ### There's more

# 1. Import the libraries:

# In[50]:


from pandas.io.json import json_normalize
from hyperopt.pyll.stochastic import sample


# In[51]:


import pickle 
trials = pickle.load(open("trials_final.p", "rb"))


# 2. Parse all the information from `trials.results` into a DataFrame:

# In[52]:


results_df = pd.DataFrame(trials.results)
params_df = json_normalize(results_df['params'])

results_df = pd.concat([results_df.drop('params', axis=1), params_df], 
                       axis=1)
results_df['iteration'] = np.arange(len(results_df)) + 1
results_df.sort_values('loss')


# 3. Draw sample from the selected distribution of `colsample_bytree`:

# In[86]:


colsample_bytree_dist = []

for _ in range(10000):
    x = sample(lgbm_param_grid['colsample_bytree'])
    colsample_bytree_dist.append(x)


# 4. Plot the results:

# In[88]:


fig, ax = plt.subplots(1, 2, figsize = (16, 8))

sns.kdeplot(colsample_bytree_dist, 
            label='Sampling Distribution', 
            ax=ax[0])
sns.kdeplot(results_df['colsample_bytree'], 
            label='Bayesian Optimization', 
            ax=ax[0])
ax[0].set(title='Distribution of colsample_bytree', 
          xlabel='Value',
          ylabel='Density')
ax[0].legend()

sns.regplot('iteration', 'colsample_bytree', 
            data=results_df, ax=ax[1])
ax[1].set(title='colsample_bytree over Iterations', 
          xlabel='Iteration', 
          ylabel='Value')

plt.tight_layout()
plt.savefig('images/ch9_im14.png', dpi=300)
plt.show()


# 5. Plot the distribution of `n_estimators`:

# In[53]:


results_df['n_estimators'].value_counts()                           .plot                           .bar(title=('# of Estimators' 
                                      ' Distribution'))

# plt.tight_layout()
# plt.savefig('images/ch9_im15.png', dpi=300)
# plt.show()


# 6. Plot the evolution of the observed losses over iterations:

# In[90]:


fig, ax = plt.subplots()
ax.plot(results_df.iteration, results_df.loss, 'o')
ax.set(title='TPE Sequence of Losses', 
       xlabel='Iteration',
       ylabel='Loss')

plt.tight_layout()
plt.savefig('images/ch9_im16.png', dpi=300)
plt.show()

