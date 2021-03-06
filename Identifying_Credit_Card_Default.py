#!/usr/bin/env python
# coding: utf-8

# In[10]:


get_ipython().run_line_magic('matplotlib', 'inline')
get_ipython().run_line_magic('config', "InlineBackend.figure_format = 'retina'")


# In[11]:


import matplotlib.pyplot as plt
import warnings

plt.style.use('seaborn')
plt.rcParams['figure.figsize'] = [8, 4.5]
plt.rcParams['figure.dpi'] = 300
warnings.simplefilter(action='ignore', category=FutureWarning)


# In[3]:


import pandas as pd
import numpy as np
import random


# In[4]:


# downloading the data 
#!wget https://archive.ics.uci.edu/ml/machine-learning-databases/00350/default%20of%20credit%20card%20clients.xls


# In[ ]:


df = pd.read_excel('default of credit card clients.xls', skiprows=1, index_col=0)


# In[ ]:


# loading the data from Excel
df = pd.read_excel('default of credit card clients.xls', skiprows=1, index_col=0)

# rename columns
df.columns = df.columns.str.lower().str.replace(" ", "_")

months = ['sep', 'aug', 'jul', 'jun', 'may', 'apr']
variables = ['payment_status', 'bill_statement', 'previous_payment']
new_column_names = [x + '_' + y for x in variables for y in months]
rename_dict = {x: y for x, y in zip(df.loc[:, 'pay_0':'pay_amt6'].columns, new_column_names)}
df.rename(columns=rename_dict, inplace=True)


# creating dicts to map number to strings
gender_dict = {1: 'Male', 
               2: 'Female'}
education_dict = {0: 'Others',
                  1: 'Graduate school', 
                  2: 'University', 
                  3: 'High school', 
                  4: 'Others',
                  5: 'Others',
                  6: 'Others'}
marital_status_dict = {0: 'Others', 
                       1: 'Married', 
                       2: 'Single', 
                       3: 'Others'}
payment_status = {-2: 'Unknown',
                  -1: 'Payed duly',
                  0: 'Unknown',
                  1: 'Payment delayed 1 month',
                  2: 'Payment delayed 2 months',
                  3: 'Payment delayed 3 months',
                  4: 'Payment delayed 4 months',
                  5: 'Payment delayed 5 months',
                  6: 'Payment delayed 6 months',
                  7: 'Payment delayed 7 months',
                  8: 'Payment delayed 8 months',
                  9: 'Payment delayed >= 9 months'}

# # map numbers to strings
df.sex = df.sex.map(gender_dict)
df.education = df.education.map(education_dict)
df.marriage = df.marriage.map(marital_status_dict)

for column in [x for x in df.columns if ('status' in x)]:
    df[column] = df[column].map(payment_status)

# define the ratio of missing values to introduce
RATIO_MISSING = 0.005

# input missing values to selected columns
random_state = np.random.RandomState(42)
for column in ['sex', 'education', 'marriage', 'age']:
    df.loc[df.sample(frac=RATIO_MISSING, random_state=random_state).index, column] = ''

# reset index
df.reset_index(drop=True, inplace=True)

# save to csv
df.to_csv('credit_card_default.csv')


# In[3]:


import pandas as pd


# In[4]:


get_ipython().system('head -n 5 credit_card_default.csv')


# In[5]:


df = pd.read_csv('credit_card_default.csv', index_col=0, na_values='')
print(f'The DataFrame has {len(df)} rows and {df.shape[1]} columns.')
df.head()


# In[6]:


X = df.copy()
y = X.pop('default_payment_next_month')


# In[7]:


df.dtypes


# In[8]:


def get_df_memory_usage(df, top_columns=5):
    '''
    Function for quick analysis of a pandas DataFrame's memory usage.
    It prints the top `top_columns` columns in terms of memory usage 
    and the total usage of the DataFrame.
    
    Parameters
    ------------
    df : pd.DataFrame
        DataFrame to be inspected
    top_columns : int
        Number of top columns (in terms of memory used) to display
    '''
    print('Memory usage ----')
    memory_per_column = df.memory_usage(deep=True) / 1024 ** 2
    print(f'Top {top_columns} columns by memory (MB):')
    print(memory_per_column.sort_values(ascending=False)                            .head(top_columns))
    print(f'Total size: {memory_per_column.sum():.4f} MB')


# In[9]:


get_df_memory_usage(df, 5)


# In[10]:


df_cat = df.copy()
object_columns = df_cat.select_dtypes(include='object').columns
df_cat[object_columns] = df_cat[object_columns].astype('category')


# In[11]:


get_df_memory_usage(df_cat)


# In[12]:


column_dtypes = {'education': 'category', 
                 'marriage': 'category', 
                 'sex': 'category',
                 'payment_status_sep': 'category', 
                 'payment_status_aug': 'category', 
                 'payment_status_jul': 'category',       
                 'payment_status_jun': 'category', 
                 'payment_status_may': 'category', 
                 'payment_status_apr': 'category'}
df_cat2 = pd.read_csv('credit_card_default.csv', index_col=0, 
                      na_values='', dtype=column_dtypes)


# In[13]:


get_df_memory_usage(df_cat2)


# In[14]:


df_cat.equals(df_cat2)


# ## Exploratory Data Analysis

# In[15]:


import pandas as pd
import seaborn as sns
import numpy as np
import plotly.express as px
import plotly.io as pio


# In[18]:


df.describe().transpose().round(2)


# In[19]:


df.describe(include='object').transpose()


# In[20]:


fig, ax = plt.subplots()
sns.distplot(df.loc[df.sex=='Male', 'age'].dropna(), 
             hist=False, color='green', 
             kde_kws={'shade': True},
             ax=ax, label='Male')
sns.distplot(df.loc[df.sex=='Female', 'age'].dropna(), 
             hist=False, color='blue', 
             kde_kws={'shade': True},
             ax=ax, label='Female')
ax.set_title('Distribution of age')
ax.legend(title='Gender:')

plt.tight_layout()
# plt.savefig('images/ch8_im5.png')
plt.show()


# As mentioned in the text, we can create a histogram (together with the KDE), by calling:

# In[21]:


ax = sns.distplot(df.age.dropna(), )
ax.set_title('Distribution of age');


# In[22]:


plot_ = sns.countplot(x=df.age.dropna(), color='blue')

for ind, label in enumerate(plot_.get_xticklabels()):
    if int(float(label.get_text())) % 10 == 0:
        label.set_visible(True)
    else:
        label.set_visible(False)


# In[24]:


px.histogram(df, x='age', title = 'Distribution of age')


# In[23]:


pair_plot = sns.pairplot(df[['age', 'limit_bal', 'previous_payment_sep']])
pair_plot.fig.suptitle('Pairplot of selected variables', y=1.05)

plt.tight_layout()
# plt.savefig('images/ch8_im6.png', bbox_inches='tight')
plt.show()


# Additionally, we can separate the genders by specifying the `hue` argument:

# In[18]:


# pair_plot = sns.pairplot(df[['sex', 'age', 'limit_bal', 'previous_payment_sep']], 
#                          hue='sex')
# pair_plot.fig.suptitle('Pairplot of selected variables', y=1.05);


# In[25]:


def plot_correlation_matrix(corr_mat):
    '''
    Function for plotting the correlation heatmap. It masks the irrelevant fields.
    
    Parameters
    ----------
    corr_mat : pd.DataFrame
        Correlation matrix of the features.
    '''
    
    # temporarily change style
    sns.set(style='white')
    # mask the upper triangle
    mask = np.zeros_like(corr_mat, dtype=np.bool)
    mask[np.triu_indices_from(mask)] = True
    # set up the matplotlib figure
    fig, ax = plt.subplots()
    # set up custom diverging colormap
    cmap = sns.diverging_palette(240, 10, n=9, as_cmap=True)
    # plot the heatmap
    sns.heatmap(corr_mat, mask=mask, cmap=cmap, vmax=.3, center=0,
                square=True, linewidths=.5, 
                cbar_kws={'shrink': .5}, ax=ax)
    ax.set_title('Correlation Matrix', fontsize=16)
    # change back to darkgrid style
    sns.set(style='darkgrid')


# In[36]:


corr_mat = df.select_dtypes(include='number').corr()    
plot_correlation_matrix(corr_mat)

plt.tight_layout()
#plt.savefig('images/ch8_im7.png')
plt.show()


# In[26]:


df.select_dtypes(include='number').corr()[['default_payment_next_month']]


# In[27]:


ax = sns.violinplot(x='education', y='limit_bal', 
                    hue='sex', split=True, data=df)
ax.set_title('Distribution of limit balance per education level', 
             fontsize=16)

plt.tight_layout()
# plt.savefig('images/ch8_im8.png')
plt.show()


# In[19]:


# ax = sns.violinplot(x='education', y='limit_bal', 
#                     hue='sex', data=df)
# ax.set_title('Distribution of limit balance per education level', 
#              fontsize=16);


# In[29]:


ax = sns.countplot('default_payment_next_month', hue='sex', 
                   data=df, orient='h')
ax.set_title('Distribution of the target variable', fontsize=16)

plt.tight_layout()
# plt.savefig('images/ch8_im9.png')
plt.show()


# In[30]:


ax = df.groupby('education')['default_payment_next_month']        .value_counts(normalize=True)        .unstack()        .plot(kind='barh', stacked='True')
ax.set_title('Percentage of default per education level', 
             fontsize=16)
ax.legend(title='Default', bbox_to_anchor=(1,1)) 

plt.tight_layout()
# plt.savefig('images/ch8_im10.png')
plt.show()


# In[ ]:


# import pandas_profiling
# df.profile_report()


# ## Splitting the data into training and test sets

# In[15]:


from sklearn.model_selection import train_test_split


# In[22]:


X_train, X_test, y_train, y_test = train_test_split(X, y, 
                                                    test_size=0.2, 
                                                    random_state=42)


# In[23]:


X_train, X_test, y_train, y_test = train_test_split(X, y, 
                                                    test_size=0.2, 
                                                    shuffle=False)


# In[16]:


X_train, X_test, y_train, y_test = train_test_split(X, y, 
                                                    test_size=0.2, 
                                                    stratify=y, 
                                                    random_state=42)


# In[25]:


y_train.value_counts(normalize=True)


# In[26]:


y_test.value_counts(normalize=True)


# In[27]:


# # define the size of the validation and test sets
# VALID_SIZE = 0.1
# TEST_SIZE = 0.2

# # create the initial split - training and temp
# X_train, X_temp, y_train, y_temp = train_test_split(X, y, 
#                                                     test_size=(VALID_SIZE + TEST_SIZE), 
#                                                     stratify=y, 
#                                                     random_state=42)

# # calculate the new test size
# NEW_TEST_SIZE = np.around(TEST_SIZE / (VALID_SIZE + TEST_SIZE), 2)

# # create the valid and test sets
# X_valid, X_test, y_valid, y_test = train_test_split(X_temp, y_temp, 
#                                                     test_size=NEW_TEST_SIZE, 
#                                                     stratify=y_temp, 
#                                                     random_state=42)


# ## Dealing with missing values

# In[17]:


import pandas as pd 
import missingno
from sklearn.impute import SimpleImputer


# In[18]:


X.info()


# 3. Visualize the nullity of the DataFrame:

# In[19]:


missingno.matrix(X)

# plt.savefig('images/ch8_im12.png')
plt.show()


# In[20]:


NUM_FEATURES = ['age']
CAT_FEATURES = ['sex', 'education', 'marriage']


# In[21]:


for col in NUM_FEATURES:
    num_imputer = SimpleImputer(strategy='median')
    num_imputer.fit(X_train[[col]])
    X_train.loc[:, col] = num_imputer.transform(X_train[[col]])
    X_test.loc[:, col] = num_imputer.transform(X_test[[col]])


# In[22]:


# alternative method using pandas

# for feature in NUM_FEATURES:
#     median_value = X_train[feature].median()
#     X_train.loc[:, feature].fillna(median_value, inplace=True)
#     X_test.loc[:, feature].fillna(median_value, inplace=True)


# In[23]:


for col in CAT_FEATURES:
    cat_imputer = SimpleImputer(strategy='most_frequent')
    cat_imputer.fit(X_train[[col]])
    X_train.loc[:, col] = cat_imputer.transform(X_train[[col]])
    X_test.loc[:, col] = cat_imputer.transform(X_test[[col]])


# In[24]:


# alternative method using pandas

# for feature in CAT_FEATURES:
#     mode_value = X_train[feature].mode().values[0]
#     X_train.loc[:, feature].fillna(mode_value, inplace=True)
#     X_test.loc[:, feature].fillna(mode_value, inplace=True)


# In[25]:


X_train.info()


# ## Encoding categorical variables

# In[34]:


import pandas as pd
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.compose import ColumnTransformer


# In[35]:


COL = 'education'

X_train_copy = X_train.copy()
X_test_copy = X_test.copy()

label_enc = LabelEncoder()
label_enc.fit(X_train_copy[COL])
X_train_copy.loc[:, COL] = label_enc.transform(X_train_copy[COL])
X_test_copy.loc[:, COL] = label_enc.transform(X_test_copy[COL])


# In[36]:


CAT_FEATURES = X_train.select_dtypes(include='object')                       .columns                       .to_list()


# In[37]:


one_hot_encoder = OneHotEncoder(sparse=False, 
                                handle_unknown='error', 
                                drop='first')


# In[38]:


one_hot_transformer = ColumnTransformer(
    [("one_hot", one_hot_encoder, CAT_FEATURES)]
    #,remainder='passthrough'
)


# In[39]:


one_hot_transformer.fit(X_train)


# In[40]:


col_names = one_hot_transformer.get_feature_names()

X_train_cat = pd.DataFrame(one_hot_transformer.transform(X_train), 
                           columns=col_names, 
                           index=X_train.index)
X_train_ohe = pd.concat([X_train, X_train_cat], axis=1)                 .drop(CAT_FEATURES, axis=1)

X_test_cat = pd.DataFrame(one_hot_transformer.transform(X_test), 
                          columns=col_names, 
                          index=X_test.index)
X_test_ohe = pd.concat([X_test, X_test_cat], axis=1)                .drop(CAT_FEATURES, axis=1)


# #### Using `pandas.get_dummies` for one-hot encoding

# In[53]:


pd.get_dummies(X_train, prefix_sep='_', drop_first=True)


# #### Specifying possible categories for OneHotEncoder

# In[54]:


one_hot_encoder = OneHotEncoder(
    categories=[['Male', 'Female', 'Unknown']], 
    sparse=False, 
    handle_unknown='error', 
    drop='first'
)

one_hot_transformer = ColumnTransformer(
    [("one_hot", one_hot_encoder, ['sex'])]
)

one_hot_transformer.fit(X_train)
one_hot_transformer.get_feature_names()


# #### Category Encoders library

# In[55]:


import category_encoders as ce


# In[56]:


one_hot_encoder_ce = ce.OneHotEncoder(use_cat_names=True)


# In[57]:


one_hot_encoder_ce.fit(X_train)
X_train_ce = one_hot_encoder_ce.transform(X_train)
X_train_ce.head()


# In[58]:


target_encoder = ce.TargetEncoder(smoothing=0)
target_encoder.fit(X_train.sex, y_train)
target_encoder.transform(X_train.sex).head()


# ## Fitting a decision tree classifier

# In[41]:


from sklearn.tree import DecisionTreeClassifier, export_graphviz
from sklearn import metrics

from chapter_8_utils import performance_evaluation_report

from io import StringIO
import seaborn as sns
from ipywidgets import Image
import pydotplus 


# In[42]:


tree_classifier = DecisionTreeClassifier(random_state=42)
tree_classifier.fit(X_train_ohe, y_train)
y_pred = tree_classifier.predict(X_test_ohe)


# In[43]:


LABELS = ['No Default', 'Default']
tree_perf = performance_evaluation_report(tree_classifier, 
                                          X_test_ohe, 
                                          y_test, labels=LABELS, 
                                          show_plot=True)

plt.tight_layout()
# plt.savefig('images/ch8_im14.png')
plt.show()


# In[44]:


tree_perf


# In[66]:


small_tree = DecisionTreeClassifier(max_depth=3, 
                                    random_state=42)
small_tree.fit(X_train_ohe, y_train)

tree_dot = StringIO()
export_graphviz(small_tree, feature_names=X_train_ohe.columns,
                class_names=LABELS, rounded=True, out_file=tree_dot,
                proportion=False, precision=2, filled=True)
tree_graph = pydotplus.graph_from_dot_data(tree_dot.getvalue())  
tree_graph.set_dpi(300) 
# tree_graph.write_png('images/ch8_im15.png')
Image(value=tree_graph.create_png())


# In[45]:


y_pred_prob = tree_classifier.predict_proba(X_test_ohe)[:, 1]


# In[46]:


precision, recall, thresholds = metrics.precision_recall_curve(y_test, 
                                                               y_pred_prob)


# In[47]:


ax = plt.subplot()
ax.plot(recall, precision, 
        label=f'PR-AUC = {metrics.auc(recall, precision):.2f}')
ax.set(title='Precision-Recall Curve', 
       xlabel='Recall', 
       ylabel='Precision')
ax.legend()

plt.tight_layout()
# plt.savefig('images/ch8_im16.png')
plt.show()


# ## Implementing scikit-learn's pipelines

# In[1]:


import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.tree import DecisionTreeClassifier
from sklearn.pipeline import Pipeline
from chapter_8_utils import performance_evaluation_report


# In[2]:


df = pd.read_csv('credit_card_default.csv', index_col=0, 
                 na_values='')

X = df.copy()
y = X.pop('default_payment_next_month')

X_train, X_test, y_train, y_test = train_test_split(X, y, 
                                                    test_size=0.2, 
                                                    stratify=y, 
                                                    random_state=42)


# In[3]:


num_features = X_train.select_dtypes(include='number')                       .columns                       .to_list()
cat_features = X_train.select_dtypes(include='object')                       .columns                       .to_list()


# In[4]:


num_pipeline = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median'))
])


# In[5]:


cat_list = [list(X_train[col].dropna().unique()) for col in cat_features]

cat_pipeline = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('onehot', OneHotEncoder(categories=cat_list, sparse=False, 
                             handle_unknown='error', drop='first'))
])


# In[6]:


preprocessor = ColumnTransformer(transformers=[
    ('numerical', num_pipeline, num_features),
    ('categorical', cat_pipeline, cat_features)],
    remainder='drop')


# In[7]:


dec_tree = DecisionTreeClassifier(random_state=42)

tree_pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                                ('classifier', dec_tree)])


# In[8]:


tree_pipeline.fit(X_train, y_train)


# In[12]:


LABELS = ['No Default', 'Default']
tree_perf = performance_evaluation_report(tree_pipeline, X_test, 
                                          y_test, labels=LABELS, 
                                          show_plot=True)

plt.tight_layout()
# plt.savefig('images/ch8_im17.png')
plt.show()


# In[12]:


tree_perf


# In[13]:


from sklearn.base import BaseEstimator, TransformerMixin


# In[14]:


class OutlierRemover(BaseEstimator, TransformerMixin):
    def __init__(self, n_std=3):
        self.n_std = n_std
    
    def fit(self, X, y = None):
        if np.isnan(X).any(axis=None):
            raise ValueError('''There are missing values in the array! 
                                Please remove them.''')

        mean_vec = np.mean(X, axis=0)
        std_vec = np.std(X, axis=0)
        
        self.upper_band_ = mean_vec + self.n_std * std_vec
        self.lower_band_ = mean_vec - self.n_std * std_vec
        self.n_features_ = len(self.upper_band_)
        
        return self 
    
    def transform(self, X, y = None):
        X_copy = pd.DataFrame(X.copy())
        
        upper_band = np.repeat(
            self.upper_band_.reshape(self.n_features_, -1), 
            len(X_copy), 
            axis=1).transpose()
        lower_band = np.repeat(
            self.lower_band_.reshape(self.n_features_, -1), 
            len(X_copy), 
            axis=1).transpose()
        
        X_copy[X_copy >= upper_band] = upper_band
        X_copy[X_copy <= lower_band] = lower_band
        
        return X_copy.values


# In[15]:


num_pipeline = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    ('outliers', OutlierRemover())
])


# In[16]:


preprocessor = ColumnTransformer(transformers=[
    ('numerical', num_pipeline, num_features),
    ('categorical', cat_pipeline, cat_features)],
    remainder='drop')

dec_tree = DecisionTreeClassifier(random_state=42)

tree_pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                                ('classifier', dec_tree)])

tree_pipeline.fit(X_train, y_train)

tree_perf = performance_evaluation_report(tree_pipeline, X_test, 
                                          y_test, labels=LABELS, 
                                          show_plot=True)

plt.tight_layout()
# plt.savefig('images/ch8_im18.png')
plt.show()


# In[17]:


tree_perf


# ## Tuning hyperparameters using grid search and cross-validation

# In[18]:


from sklearn.model_selection import (GridSearchCV, cross_val_score, 
                                     RandomizedSearchCV, cross_validate, 
                                     StratifiedKFold)
from sklearn import metrics


# In[19]:


k_fold = StratifiedKFold(5, shuffle=True, random_state=42)


# In[20]:


cross_val_score(tree_pipeline, X_train, y_train, cv=k_fold)


# In[21]:


cross_validate(tree_pipeline, X_train, y_train, cv=k_fold, 
               scoring=['accuracy', 'precision', 'recall', 
                        'roc_auc'])


# In[22]:


param_grid = {'classifier__criterion': ['entropy', 'gini'],
              'classifier__max_depth': range(3, 11),
              'classifier__min_samples_leaf': range(2, 11), 
              'preprocessor__numerical__outliers__n_std': [3, 4]}


# In[23]:


classifier_gs = GridSearchCV(tree_pipeline, param_grid, scoring='recall', 
                             cv=k_fold, n_jobs=-1, verbose=1)

classifier_gs.fit(X_train, y_train)


# In[24]:


print(f'Best parameters: {classifier_gs.best_params_}') 
print(f'Recall (Training set): {classifier_gs.best_score_:.4f}') 
print(f'Recall (Test set): {metrics.recall_score(y_test, classifier_gs.predict(X_test)):.4f}')


# In[25]:


LABELS = ['No Default', 'Default']
tree_gs_perf = performance_evaluation_report(classifier_gs, X_test, 
                                             y_test, labels=LABELS, 
                                             show_plot=True)

plt.tight_layout()
plt.savefig('images/ch8_im20.png')
plt.show()


# In[26]:


tree_gs_perf


# In[27]:


classifier_rs = RandomizedSearchCV(tree_pipeline, param_grid, scoring='recall', 
                                   cv=k_fold, n_jobs=-1, verbose=1, 
                                   n_iter=100, random_state=42)
classifier_rs.fit(X_train, y_train)


# In[28]:


print(f'Best parameters: {classifier_rs.best_params_}') 
print(f'Recall (Training set): {classifier_rs.best_score_:.4f}') 
print(f'Recall (Test set): {metrics.recall_score(y_test, classifier_rs.predict(X_test)):.4f}')


# In[29]:


tree_rs_perf = performance_evaluation_report(classifier_rs, X_test, 
                                             y_test, labels=LABELS, 
                                             show_plot=True)

plt.tight_layout()
plt.savefig('images/ch8_im21.png')
plt.show()


# In[30]:


tree_rs_perf


# In[31]:


from sklearn.linear_model import LogisticRegression


# In[32]:


param_grid = [{'classifier': [LogisticRegression()],
               'classifier__penalty': ['l1', 'l2'],
               'classifier__C': np.logspace(0, 3, 10, 2),
               'preprocessor__numerical__outliers__n_std': [3, 4]},
              {'classifier': [DecisionTreeClassifier(random_state=42)],
               'classifier__criterion': ['entropy', 'gini'],
               'classifier__max_depth': range(3, 11),
               'classifier__min_samples_leaf': range(2, 11),
               'preprocessor__numerical__outliers__n_std': [3, 4]}]


# In[33]:


classifier_gs_2 = GridSearchCV(tree_pipeline, param_grid, scoring='recall', 
                               cv=k_fold, n_jobs=-1, verbose=1)

classifier_gs_2.fit(X_train, y_train)

print(f'Best parameters: {classifier_gs_2.best_params_}') 
print(f'Recall (Training set): {classifier_gs_2.best_score_:.4f}') 
print(f'Recall (Test set): {metrics.recall_score(y_test, classifier_gs_2.predict(X_test)):.4f}')


# In[ ]:





# In[ ]:





# In[ ]:




