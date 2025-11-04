import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import LinearRegression
from xgboost import XGBRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    mean_absolute_percentage_error,
    r2_score
)
import matplotlib.pyplot as plt
import joblib
import os


class InsurancePremiumPredictor:
    def __init__(self):
        self.models = {}
        self.scaler = None
        self.label_encoders = {}
        os.makedirs('models', exist_ok=True)
        os.makedirs('data', exist_ok=True)

    def prepare_data(self):
        """Generate synthetic insurance data for training"""
        np.random.seed(42)
        n_samples = 1000

        ages = np.random.randint(18, 65, n_samples)
        genders = np.random.choice(['male', 'female'], n_samples)
        bmis = np.random.normal(28, 6, n_samples)
        bmis = np.clip(bmis, 15, 50)
        children = np.random.poisson(1, n_samples)
        children = np.clip(children, 0, 5)
        smokers = np.random.choice(['yes', 'no'], n_samples, p=[0.2, 0.8])
        regions = np.random.choice(['northeast', 'southeast', 'southwest', 'northwest'], n_samples)

        base_premium = 5000
        premiums = []

        for i in range(n_samples):
            premium = base_premium
            premium += (ages[i] - 18) * 50
            if bmis[i] > 30:
                premium += (bmis[i] - 30) * 200
            elif bmis[i] < 18.5:
                premium += (18.5 - bmis[i]) * 100
            if smokers[i] == 'yes':
                premium += 15000
            premium += children[i] * 1000
            if genders[i] == 'male':
                premium += 500
            region_multipliers = {
                'northeast': 1.1,
                'southeast': 0.9,
                'southwest': 0.95,
                'northwest': 1.05
            }
            premium *= region_multipliers[regions[i]]
            premium += np.random.normal(0, 1000)
            premium = max(premium, 1000)
            premiums.append(premium)

        data = pd.DataFrame({
            'age': ages,
            'gender': genders,
            'bmi': bmis,
            'children': children,
            'smoker': smokers,
            'region': regions,
            'premium': premiums
        })

        data.to_csv('data/insurance_data.csv', index=False)
        return data

    def preprocess_features(self, data):
        processed_data = data.copy()
        categorical_columns = ['gender', 'smoker', 'region']
        for col in categorical_columns:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
                processed_data[col] = self.label_encoders[col].fit_transform(processed_data[col])
            else:
                processed_data[col] = self.label_encoders[col].transform(processed_data[col])
        return processed_data

    def adjusted_r2(self, r2, n, p):
        """Compute Adjusted R²"""
        return 1 - (1 - r2) * (n - 1) / (n - p - 1)

    def train_model(self):
        """Train multiple models and compare their performance"""
        print("🔄 Generating and preparing training data...")
        data = self.prepare_data()
        X = data.drop('premium', axis=1)
        y = data['premium']

        X_processed = self.preprocess_features(X)
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X_processed)

        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

        # Define multiple models
        model_dict = {
            "LinearRegression": LinearRegression(),
            "DecisionTree": DecisionTreeRegressor(max_depth=10, random_state=42),
            "RandomForest": RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1),
            "XGBoost": XGBRegressor(n_estimators=200, learning_rate=0.1, max_depth=5, random_state=42)
        }

        results = []

        print("\n⚙️ Training Models and Evaluating Performance...")
        for name, model in model_dict.items():
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)

            # Compute metrics
            mae = mean_absolute_error(y_test, y_pred)
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            mape = mean_absolute_percentage_error(y_test, y_pred) * 100
            r2 = r2_score(y_test, y_pred)
            adj_r2 = self.adjusted_r2(r2, len(y_test), X_test.shape[1])

            results.append((name, mae, mse, rmse, mape, r2, adj_r2))

            self.models[name] = model
            joblib.dump(model, f'models/{name}.pkl')

            print(
                f"✅ {name} → MAE: {mae:.2f}, RMSE: {rmse:.2f}, MAPE: {mape:.2f}%, "
                f"R²: {r2:.3f}, Adjusted R²: {adj_r2:.3f}"
            )

        # Save preprocessing
        joblib.dump(self.scaler, 'models/scaler.pkl')
        joblib.dump(self.label_encoders, 'models/label_encoders.pkl')

        print("\n📦 All models and preprocessing files saved successfully!")

        # Create comparison DataFrame
        results_df = pd.DataFrame(results, columns=['Model', 'MAE', 'MSE', 'RMSE', 'MAPE(%)', 'R²', 'Adjusted R²'])
        print("\n📊 Model Comparison:\n", results_df)

        # Plot metrics comparison
        self.plot_model_comparison(results_df)

        # Plot feature relations
        self.plot_feature_relations(data)

    def plot_model_comparison(self, results_df):
        """Plot all metrics comparison for trained models"""
        metrics = ['MAE', 'RMSE', 'MAPE(%)', 'R²', 'Adjusted R²']
        colors = ['#FF9999', '#66B2FF', '#99FF99', '#FFD580', '#C2C2F0']

        plt.figure(figsize=(15, 8))

        for i, metric in enumerate(metrics):
            plt.subplot(2, 3, i + 1)
            plt.bar(results_df['Model'], results_df[metric], color=colors[i], edgecolor='black')
            plt.title(f'{metric} Comparison')
            plt.xlabel('Model')
            plt.ylabel(metric)
            plt.grid(axis='y', linestyle='--', alpha=0.7)

            # Display values above bars
            for idx, val in enumerate(results_df[metric]):
                plt.text(idx, val, f"{val:.2f}", ha='center', va='bottom', fontsize=9)

        plt.tight_layout()
        plt.suptitle('📊 Model Performance Comparison', fontsize=16, y=1.03)
        plt.show()

    def plot_feature_relations(self, data):
        """Plot relationships between features and premium"""
        features = ['age', 'bmi', 'children']
        plt.figure(figsize=(15, 4))
        for i, feature in enumerate(features):
            plt.subplot(1, 3, i + 1)
            plt.scatter(data[feature], data['premium'], alpha=0.6, color='teal')
            plt.title(f'{feature} vs Premium')
            plt.xlabel(feature)
            plt.ylabel('Premium')
            plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()
        plt.suptitle("📈 Feature vs Premium Relationships", fontsize=15, y=1.02)
        plt.show()

    def load_model(self):
        """Load trained models and preprocessing files"""
        try:
            self.models = {}
            for name in ["LinearRegression", "DecisionTree", "RandomForest", "XGBoost"]:
                model_path = f"models/{name}.pkl"
                if os.path.exists(model_path):
                    self.models[name] = joblib.load(model_path)
            self.scaler = joblib.load('models/scaler.pkl')
            self.label_encoders = joblib.load('models/label_encoders.pkl')
            print("✅ All models loaded successfully!")
        except FileNotFoundError:
            print("⚠️ No models found. Training new models...")
            self.train_model()

    def predict(self, age, gender, bmi, children, smoker, region):
        """Predict premiums using all trained models"""
        if not self.models:
            self.load_model()

        input_data = pd.DataFrame({
            'age': [age],
            'gender': [gender],
            'bmi': [bmi],
            'children': [children],
            'smoker': [smoker],
            'region': [region]
        })

        input_processed = self.preprocess_features(input_data)
        input_scaled = self.scaler.transform(input_processed)

        predictions = {}
        for name, model in self.models.items():
            pred = model.predict(input_scaled)[0]
            predictions[name] = round(pred, 2)

        return predictions


# -------------------------------------------------------
# STANDALONE TEST
# -------------------------------------------------------
if __name__ == "__main__":
    predictor = InsurancePremiumPredictor()
    predictor.train_model()

    results = predictor.predict(age=35, gender='male', bmi=27.5, children=2, smoker='no', region='northwest')
    print("\n🔍 Prediction Results:")
    for model, value in results.items():
        print(f"{model}: ₹{value}")
