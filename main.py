import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB


def get_data(filepath):
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        return None, None

    features = [
        'url_length', 'domain_length',
        'dot_count', 'hyphen_count', 'underscore_count', 'slash_count',
        'question_count', 'equal_count', 'at_count',
        'digits_count', 'letters_count',
        'has_ip', 'has_https',
        'digit_letter_ratio', 'suspicious_words', 'is_shortened'
    ]

    for col in features:
        if col in df.columns:
            print(f"Processing column: {col}")
            df[col] = df[col].replace([np.inf, -np.inf], 0)
            df[col] = df[col].fillna(0)
            df[col] = df[col].astype(int)
        else:
             df[col] = 0

    return df[features], df['is_phishing']

def train_episode(model, X_train, y_train):
    classes = np.unique(y_train)
    model.partial_fit(X_train, y_train, classes=classes)
    return model

def evaluate(model, X_test, y_test):
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\nAccuracy: {acc:.4f}")
    print("\nReport:")
    print(classification_report(y_test, y_pred))
    return acc, confusion_matrix(y_test, y_pred)

def save_plot(cm):
    if not os.path.exists('reports'):
        os.makedirs('reports')
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Legítimo', 'Phishing'], yticklabels=['Legítimo', 'Phishing'])
    plt.title('Matriz de Confusão')
    plt.ylabel('Real')
    plt.xlabel('Previsto')
    plt.savefig('reports/confusion_matrix.png')
    print("\nGráfico salvo em reports/confusion_matrix.png")

def main():
    print("Starting the pipeline...")

    if not os.path.exists('data/phishing_site_urls_cleaned.csv'):
        print("Data not found. Please run 'cleaning.ipynb' first to generate the dataset.")
        return

    X, y = get_data('data/phishing_site_urls_cleaned.csv')

    if X is None or X.empty:
        print("Data could not be loaded.")
        return

    print(f"Training with {X.shape[1]} features: {list(X.columns)}")

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    gnb = GaussianNB()

    model = train_episode(gnb, X_train, y_train)
    acc, cm = evaluate(model, X_test, y_test)

    print(f"Model trained with accuracy: {acc:.4f}")
    save_plot(cm)

if __name__ == "__main__":
    main()
