# visualize_forest.py
# See exactly how Random Forest makes decisions

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

print("🌲 Random Forest — Under The Hood")
print("=" * 50)

# Load your trained model
model = joblib.load('fraud_detection_model.pkl')

# Create test transactions
transactions = pd.DataFrame([
    [3500, 3, 500],    # Obviously fraud
    [45, 14, 2],       # Obviously legit
    [800, 22, 150],    # Borderline case!
], columns=['amount', 'hour', 'distance_from_home'])

labels = ["Obviously Fraud", "Obviously Legit", "Borderline Case"]

print("\n🗳️ Watching 10 Trees Vote:\n")

for idx, (_, transaction) in enumerate(transactions.iterrows()):
    print(f"Transaction: {labels[idx]}")
    print(f"  Amount: ${transaction['amount']}")
    print(f"  Hour: {transaction['hour']}:00")
    print(f"  Distance: {transaction['distance_from_home']}km")

    # Watch individual trees vote
    fraud_votes = 0
    legit_votes = 0

    for i, tree in enumerate(model.estimators_[:10]):
        vote = tree.predict([transaction])[0]
        if vote == 1:
            fraud_votes += 1
        else:
            legit_votes += 1

    # Show all 100 trees
    all_fraud = sum(
        tree.predict([transaction])[0]
        for tree in model.estimators_
    )
    all_legit = 100 - all_fraud

    # Get probability
    proba = model.predict_proba([transaction])[0]

    print(f"\n  First 10 trees:")
    print(f"  🔴 Fraud votes: {fraud_votes}/10")
    print(f"  🟢 Legit votes: {legit_votes}/10")

    print(f"\n  All 100 trees:")
    print(f"  🔴 Fraud votes: {all_fraud}/100")
    print(f"  🟢 Legit votes: {all_legit}/100")

    print(f"\n  Final probability:")
    fraud_bar = "█" * int(proba[1] * 20)
    legit_bar = "█" * int(proba[0] * 20)
    print(f"  Fraud: {fraud_bar} {proba[1]:.1%}")
    print(f"  Legit: {legit_bar} {proba[0]:.1%}")

    # TD Bank decision
    if proba[1] > 0.80:
        action = "🚨 BLOCK + CALL CUSTOMER"
    elif proba[1] > 0.60:
        action = "⚠️  SMS VERIFICATION"
    elif proba[1] > 0.40:
        action = "👀 FLAG FOR REVIEW"
    else:
        action = "✅ ALLOW TRANSACTION"

    print(f"\n  TD Bank Action: {action}")
    print("-" * 50)

print("\n🌲 Feature Importance:")
print("(Which clue matters most?)\n")
features = ['amount', 'hour', 'distance_from_home']
for feature, importance in zip(
    features,
    model.feature_importances_
):
    bar = "█" * int(importance * 40)
    print(f"  {feature:20} {bar} {importance:.1%}")