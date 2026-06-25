import os
import pickle
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

os.makedirs('models', exist_ok=True)

np.random.seed(42)
fake_accounts = np.random.normal(loc=[0, 10, 50, 2000, 2], scale=[0.1, 5, 30, 500, 2], size=(200, 5))
real_accounts = np.random.normal(loc=[1, 80, 1500, 400, 50], scale=[0.1, 20, 500, 150, 20], size=(200, 5))

X = np.vstack((fake_accounts, real_accounts))
X = np.clip(X, 0, None)
X[:, 0] = np.where(X[:, 0] > 0.5, 1, 0)

y = np.array([1]*200 + [0]*200) 

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

with open('models/account_model.pkl', 'wb') as f:
    pickle.dump(rf_model, f)

print("Success! The Profile Checker model has been trained and saved in the 'models' folder.")