import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import os

class InsurancePremiumPredictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.label_encoders = {}
        
    def prepare_data(self):
        """Generate sample insurance data for training"""
        np.random.seed(42)
        n_samples = 1000
        
        # Generate synthetic data
        ages = np.random.randint(18, 65, n_samples)
        genders = np.random.choice(['male', 'female'], n_samples)
        bmis = np.random.normal(28, 6, n_samples)
        bmis = np.clip(bmis, 15, 50)  # Realistic BMI range
        children = np.random.poisson(1, n_samples)
        children = np.clip(children, 0, 5)
        smokers = np.random.choice(['yes', 'no'], n_samples, p=[0.2, 0.8])
        regions = np.random.choice(['northeast', 'southeast', 'southwest', 'northwest'], n_samples)
        
        # Create premium based on realistic factors
        base_premium = 5000
        premiums = []
        
        for i in range(n_samples):
            premium = base_premium
            
            # Age factor
            premium += (ages[i] - 18) * 50
            
            # BMI factor
            if bmis[i] > 30:
                premium += (bmis[i] - 30) * 200
            elif bmis[i] < 18.5:
                premium += (18.5 - bmis[i]) * 100
                
            # Smoking factor
            if smokers[i] == 'yes':
                premium += 15000
                
            # Children factor
            premium += children[i] * 1000
            
            # Gender factor (slight difference)
            if genders[i] == 'male':
                premium += 500
                
            # Region factor
            region_multipliers = {
                'northeast': 1.1,
                'southeast': 0.9,
                'southwest': 0.95,
                'northwest': 1.05
            }
            premium *= region_multipliers[regions[i]]
            
            # Add some noise
            premium += np.random.normal(0, 1000)
            premium = max(premium, 1000)  # Minimum premium
            
            premiums.append(premium)
        
        # Create DataFrame
        data = pd.DataFrame({
            'age': ages,
            'gender': genders,
            'bmi': bmis,
            'children': children,
            'smoker': smokers,
            'region': regions,
            'premium': premiums
        })
        
        return data
    
    def preprocess_features(self, data):
        """Preprocess features for training"""
        # Create a copy to avoid modifying original data
        processed_data = data.copy()
        
        # Encode categorical variables
        categorical_columns = ['gender', 'smoker', 'region']
        
        for col in categorical_columns:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
                processed_data[col] = self.label_encoders[col].fit_transform(processed_data[col])
            else:
                processed_data[col] = self.label_encoders[col].transform(processed_data[col])
        
        return processed_data
    
    def train_model(self):
        """Train the insurance premium prediction model"""
        print("Generating training data...")
        data = self.prepare_data()
        
        # Save sample data
        os.makedirs('data', exist_ok=True)
        data.to_csv('data/insurance_data.csv', index=False)
        
        # Separate features and target
        X = data.drop('premium', axis=1)
        y = data['premium']
        
        # Preprocess features
        X_processed = self.preprocess_features(X)
        
        # Scale numerical features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X_processed)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # Train model
        print("Training Random Forest model...")
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.model.fit(X_train, y_train)
        
        # Evaluate model
        train_predictions = self.model.predict(X_train)
        test_predictions = self.model.predict(X_test)
        
        train_mae = mean_absolute_error(y_train, train_predictions)
        test_mae = mean_absolute_error(y_test, test_predictions)
        train_r2 = r2_score(y_train, train_predictions)
        test_r2 = r2_score(y_test, test_predictions)
        
        print(f"Training MAE: {train_mae:.2f}")
        print(f"Test MAE: {test_mae:.2f}")
        print(f"Training R²: {train_r2:.3f}")
        print(f"Test R²: {test_r2:.3f}")
        
        # Save model and scaler
        os.makedirs('models', exist_ok=True)
        joblib.dump(self.model, 'models/insurance_model.pkl')
        joblib.dump(self.scaler, 'models/scaler.pkl')
        joblib.dump(self.label_encoders, 'models/label_encoders.pkl')
        
        print("Model saved successfully!")
        
    def load_model(self):
        """Load trained model"""
        try:
            self.model = joblib.load('models/insurance_model.pkl')
            self.scaler = joblib.load('models/scaler.pkl')
            self.label_encoders = joblib.load('models/label_encoders.pkl')
            print("Model loaded successfully!")
        except FileNotFoundError:
            print("Model files not found. Training new model...")
            self.train_model()
    
    def predict(self, age, gender, bmi, children, smoker, region):
        """Make prediction for given input"""
        if self.model is None:
            self.load_model()
        
        # Create input DataFrame
        input_data = pd.DataFrame({
            'age': [age],
            'gender': [gender],
            'bmi': [bmi],
            'children': [children],
            'smoker': [smoker],
            'region': [region]
        })
        
        # Preprocess input
        input_processed = self.preprocess_features(input_data)
        input_scaled = self.scaler.transform(input_processed)
        
        # Make prediction
        prediction = self.model.predict(input_scaled)[0]
        
        return round(prediction, 2)

# Example usage and testing
if __name__ == "__main__":
    predictor = InsurancePremiumPredictor()
    
    # Train the model
    predictor.train_model()
    
    # Test prediction
    test_prediction = predictor.predict(
        age=30,
        gender='male',
        bmi=25.0,
        children=1,
        smoker='no',
        region='northeast'
    )
    
    print(f"\nTest Prediction: ${test_prediction:.2f}")