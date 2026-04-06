
#!/usr/bin/env python
# coding: utf-8
import pandas as pd
import numpy as np
import sklearn
import pickle

from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline


print(f'pandas=={pd.__version__}')
print(f'numpy=={np.__version__}')
print(f'sklearn=={sklearn.__version__}')





def load_data():
    data = 'https://raw.githubusercontent.com/alexeygrigorev/mlbookcamp-code/master/chapter-03-churn-prediction/WA_Fn-UseC_-Telco-Customer-Churn.csv'
    df = pd.read_csv(data)
        
    # Clean column names
    df.columns = df.columns.str.lower().str.replace(' ', '_', regex=False)

    # Include both object and string columns
    categorical_columns = list(df.select_dtypes(include=['object', 'string']).columns)

    # Clean text columns
    for c in categorical_columns:
        df[c] = df[c].astype(str).str.lower().str.strip().str.replace(' ', '_', regex=False)

    # Convert totalcharges
    df['totalcharges'] = pd.to_numeric(df['totalcharges'], errors='coerce').fillna(0)

    # Convert target
    df['churn'] = (df['churn'] == 'yes').astype(int)
    
    return df






def train_model(df):
    numerical = ['tenure', 'monthlycharges', 'totalcharges']

    categorical = [
        'gender',
        'seniorcitizen',
        'partner',
        'dependents',
        'phoneservice',
        'multiplelines',
        'internetservice',
        'onlinesecurity',
        'onlinebackup',
        'deviceprotection',
        'techsupport',
        'streamingtv',
        'streamingmovies',
        'contract',
        'paperlessbilling',
        'paymentmethod',
    ]


    pipeline= make_pipeline(
        DictVectorizer(),
        LogisticRegression(solver='liblinear')
    )



    train_dict = df[categorical + numerical].to_dict(orient='records')
    y_train = df.churn

    
    pipeline.fit(train_dict , y_train)
    return pipeline

def save_model(file_name, model):
    with open(file_name, 'wb') as f_out:
        pickle.dump(model,f_out)
        print(f'model saved to {file_name}') 

df =load_data()
# Check target conversion
print(df['churn'].value_counts())
# expected:
# 0    5174
# 1    1869
pipeline = train_model(df)

save_model('model.bin', pipeline)















