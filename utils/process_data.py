# import pandas as pd
# import numpy as np
# from sklearn.preprocessing import StandardScaler
# from sklearn.model_selection import train_test_split

# # def load_and_preprocess_data(filepath):
    
# #     #load dataset
# #     df = pd.read_csv(filepath)
    
# #     #mood affecting features
# #     features = ['danceability', 'acousticness', 'energy', 'instrumentalness', 
# #                 'liveness', 'valence', 'loudness', 'speechiness', 'tempo']
    
# #     #standardize features
# #     scaler = StandardScaler()
# #     df[features] = scaler.fit_transform(df[features])
    
# #     return df, features

# # def prepare_training_data(df, features):
# #     #split data into features and target
# #     X = df[features]
# #     y = df['mood']
    
# #     #split into train and test sets
# #     X_train, X_test, y_train, y_test = train_test_split(
# #         X, y, test_size=0.2, random_state=42)
    
# #     return X_train, X_test, y_train, y_test


# # Add feature engineering and better validation
# def load_and_preprocess_data(filepath):
#     df = pd.read_csv(filepath)
    
#     # 1. Add engineered features
#     df['energy_valence_ratio'] = df['energy'] / (df['valence'] + 0.001)  # Avoid divide-by-zero
#     df['dance_valence_interaction'] = df['danceability'] * df['valence']
    
#     features = [
#         'danceability', 'acousticness', 'energy', 'instrumentalness',
#         'liveness', 'valence', 'loudness', 'speechiness', 'tempo',
#         'energy_valence_ratio', 'dance_valence_interaction'
#     ]
    
#     # 2. Robust scaling with outlier handling
#     df[features] = df[features].clip(lower=df[features].quantile(0.01), 
#                                    upper=df[features].quantile(0.99))
    
#     scaler = StandardScaler()
#     df[features] = scaler.fit_transform(df[features])
    
#     return df, features

# def prepare_training_data(df, features):
#     # Stratified split for imbalanced moods
#     X_train, X_test, y_train, y_test = train_test_split(
#         df[features], df['mood'], 
#         test_size=0.2, 
#         random_state=42,
#         stratify=df['mood']
#     )
#     return X_train, X_test, y_train, y_test



import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

def load_and_preprocess_data(filepath):
    # Load dataset
    df = pd.read_csv(filepath)
    
    # Define core features
    features = [
        'danceability', 'acousticness', 'energy', 'instrumentalness',
        'liveness', 'valence', 'loudness', 'speechiness', 'tempo'
    ]
    
    # 1. Handle missing values
    df[features] = df[features].fillna(df[features].median())
    
    # 2. Safe clipping (fixed version)
    for feature in features:
        lower = df[feature].quantile(0.01)
        upper = df[feature].quantile(0.99)
        df[feature] = df[feature].clip(lower=lower, upper=upper, axis=0)
    
    # 3. Feature engineering
    df['energy_valence_ratio'] = df['energy'] / (df['valence'] + 0.001)
    df['dance_valence_interaction'] = df['danceability'] * df['valence']
    features += ['energy_valence_ratio', 'dance_valence_interaction']
    
    # 4. Scaling
    scaler = StandardScaler()
    df[features] = scaler.fit_transform(df[features])
    
    return df, features

def prepare_training_data(df, features):
    # Stratified split for imbalanced data
    X_train, X_test, y_train, y_test = train_test_split(
        df[features], 
        df['mood'],
        test_size=0.2,
        random_state=42,
        stratify=df['mood']
    )
    return X_train, X_test, y_train, y_test