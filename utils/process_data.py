import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

def load_and_preprocess_data(filepath):
    #load dataset
    df = pd.read_csv(filepath)
    
    #define core features
    features = [
        'danceability', 'acousticness', 'energy', 'instrumentalness',
        'liveness', 'valence', 'loudness', 'speechiness', 'tempo'
    ]
    
    #handle missing values
    df[features] = df[features].fillna(df[features].median())
    
    
    for feature in features:
        lower = df[feature].quantile(0.01)
        upper = df[feature].quantile(0.99)
        df[feature] = df[feature].clip(lower=lower, upper=upper, axis=0)
    
    #feature engineering
    df['energy_valence_ratio'] = df['energy'] / (df['valence'] + 0.001)
    df['dance_valence_interaction'] = df['danceability'] * df['valence']
    features += ['energy_valence_ratio', 'dance_valence_interaction']
    
    #scaling
    scaler = StandardScaler()
    df[features] = scaler.fit_transform(df[features])
    
    return df, features

def prepare_training_data(df, features):
    #stratified split for imbalanced data
    X_train, X_test, y_train, y_test = train_test_split(
        df[features], 
        df['mood'],
        test_size=0.2,
        random_state=42,
        stratify=df['mood']
    )
    return X_train, X_test, y_train, y_test