from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib
import os
from sklearn.model_selection import GridSearchCV

# def train_mood_classifier(X_train, y_train):
#     #initialize and train classifier
#     classifier = RandomForestClassifier(n_estimators=100, random_state=42)
#     classifier.fit(X_train, y_train)
    
#     return classifier

def train_mood_classifier(X_train, y_train):
    param_grid = {
        'n_estimators': [50, 100, 200],
        'max_depth': [None, 10, 20],
        'class_weight': ['balanced', None]
    }
    
    clf = GridSearchCV(
        RandomForestClassifier(random_state=42),
        param_grid,
        cv=5,
        scoring='f1_weighted'
    )
    clf.fit(X_train, y_train)
    
    print(f"Best params: {clf.best_params_}")
    return clf.best_estimator_




def evaluate_classifier(classifier, X_test, y_test):
    #make predictions
    y_pred = classifier.predict(X_test)
    
    #show classification results
    print(classification_report(y_test, y_pred))
    
# def save_classifier(classifier, filepath):
#     joblib.dump(classifier, filepath)
    

def save_classifier(classifier, filepath):
    # Save with compression for smaller files
    joblib.dump(classifier, filepath, compress=3)

def load_classifier(filepath):
    try:
        if os.path.exists(filepath):
            return joblib.load(filepath)
        return None
    except Exception as e:
        print(f"Error loading classifier: {e}")
        return None

def predict_mood(classifier, audio_features):
    #predict mood based on audio features
    return classifier.predict([audio_features])[0]