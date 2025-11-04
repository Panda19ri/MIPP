#!/usr/bin/env python3
"""
Sample Data Generator for Medical Insurance Premium Prediction
This script generates realistic synthetic data for training the ML model.
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def generate_insurance_data(n_samples=1000, random_seed=42):
    """
    Generate synthetic insurance data for training the ML model.
    
    Args:
        n_samples (int): Number of samples to generate
        random_seed (int): Random seed for reproducibility
        
    Returns:
        pandas.DataFrame: Generated insurance data
    """
    np.random.seed(random_seed)
    random.seed(random_seed)
    
    print(f"Generating {n_samples} synthetic insurance records...")
    
    # Define realistic ranges and distributions
    data = []
    
    for i in range(n_samples):
        # Age: Normal distribution around 40, clipped to 18-64
        age = int(np.clip(np.random.normal(40, 12), 18, 64))
        
        # Gender: Roughly equal distribution
        gender = np.random.choice(['male', 'female'], p=[0.51, 0.49])
        
        # BMI: Normal distribution around 28, clipped to realistic range
        bmi = np.clip(np.random.normal(28, 6), 15, 50)
        
        # Children: Poisson distribution (most people have 0-2 children)
        children = np.clip(np.random.poisson(1), 0, 5)
        
        # Smoker: 20% smoking rate (realistic for developed countries)
        smoker = np.random.choice(['yes', 'no'], p=[0.2, 0.8])
        
        # Region: Equal distribution across regions
        region = np.random.choice(['northeast', 'southeast', 'southwest', 'northwest'])
        
        # Calculate premium based on realistic factors
        base_premium = 5000
        premium = base_premium
        
        # Age factor: Premium increases with age
        premium += (age - 18) * 50
        
        # BMI factor: Higher premiums for obesity and underweight
        if bmi > 30:
            premium += (bmi - 30) * 200  # Obesity penalty
        elif bmi < 18.5:
            premium += (18.5 - bmi) * 100  # Underweight penalty
        
        # Smoking factor: Major impact on premium
        if smoker == 'yes':
            premium += 15000 + np.random.normal(0, 2000)  # High smoking penalty with variance
        
        # Children factor: Each child adds to premium
        premium += children * 1000
        
        # Gender factor: Slight difference (realistic but minimal)
        if gender == 'male':
            premium += 200
        
        # Region factor: Different costs in different regions
        region_multipliers = {
            'northeast': 1.1,   # Higher cost region
            'southeast': 0.9,   # Lower cost region
            'southwest': 0.95,  # Moderate cost region
            'northwest': 1.05   # Moderate-high cost region
        }
        premium *= region_multipliers[region]
        
        # Add some realistic noise
        premium += np.random.normal(0, 1000)
        
        # Ensure minimum premium
        premium = max(premium, 1500)
        
        # Round to nearest dollar
        premium = round(premium, 2)
        
        # Create record
        record = {
            'age': age,
            'gender': gender,
            'bmi': round(bmi, 1),
            'children': children,
            'smoker': smoker,
            'region': region,
            'premium': premium
        }
        
        data.append(record)
        
        # Progress indicator
        if (i + 1) % 100 == 0:
            print(f"Generated {i + 1}/{n_samples} records...")
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Display statistics
    print("\nDataset Statistics:")
    print(f"Total records: {len(df)}")
    print(f"Age range: {df['age'].min()} - {df['age'].max()}")
    print(f"BMI range: {df['bmi'].min():.1f} - {df['bmi'].max():.1f}")
    print(f"Premium range: ${df['premium'].min():.2f} - ${df['premium'].max():.2f}")
    print(f"Average premium: ${df['premium'].mean():.2f}")
    print(f"Smoking rate: {(df['smoker'] == 'yes').mean():.1%}")
    print(f"Gender distribution:\n{df['gender'].value_counts()}")
    print(f"Region distribution:\n{df['region'].value_counts()}")
    
    return df

def add_realistic_variations(df):
    """Add more realistic variations to the data."""
    df = df.copy()
    
    # Add some correlation between age and BMI (older people tend to have higher BMI)
    age_bmi_correlation = 0.3
    for i in range(len(df)):
        age_factor = (df.loc[i, 'age'] - 30) / 50  # Normalized age factor
        bmi_adjustment = age_factor * 3 * age_bmi_correlation
        df.loc[i, 'bmi'] = max(15, df.loc[i, 'bmi'] + bmi_adjustment)
    
    # Add seasonal variation (if we had dates)
    # This could be expanded to include temporal patterns
    
    return df

def save_data(df, filename='insurance_data.csv'):
    """Save the generated data to CSV file."""
    df.to_csv(filename, index=False)
    print(f"\nData saved to {filename}")
    
    # Also save a smaller sample for testing
    test_sample = df.sample(n=100, random_state=42)
    test_filename = filename.replace('.csv', '_sample.csv')
    test_sample.to_csv(test_filename, index=False)
    print(f"Test sample saved to {test_filename}")

def generate_user_test_data():
    """Generate some test data for user interactions."""
    test_cases = [
        {
            'description': 'Young healthy non-smoker',
            'age': 25,
            'gender': 'female',
            'bmi': 22.0,
            'children': 0,
            'smoker': 'no',
            'region': 'southwest'
        },
        {
            'description': 'Middle-aged smoker with children',
            'age': 45,
            'gender': 'male',
            'bmi': 28.5,
            'children': 2,
            'smoker': 'yes',
            'region': 'northeast'
        },
        {
            'description': 'Older adult with high BMI',
            'age': 58,
            'gender': 'female',
            'bmi': 35.0,
            'children': 1,
            'smoker': 'no',
            'region': 'southeast'
        },
        {
            'description': 'Young smoker',
            'age': 22,
            'gender': 'male',
            'bmi': 24.0,
            'children': 0,
            'smoker': 'yes',
            'region': 'northwest'
        }
    ]
    
    return test_cases

def main():
    """Main function to generate and save sample data."""
    print("Medical Insurance Premium Prediction - Sample Data Generator")
    print("=" * 60)
    
    # Generate main dataset
    df = generate_insurance_data(n_samples=1000)
    
    # Add realistic variations
    df = add_realistic_variations(df)
    
    # Save data
    save_data(df)
    
    # Generate test cases
    test_cases = generate_user_test_data()
    print(f"\nGenerated {len(test_cases)} test cases for user testing:")
    for i, case in enumerate(test_cases, 1):
        print(f"{i}. {case['description']}")
        for key, value in case.items():
            if key != 'description':
                print(f"   {key}: {value}")
        print()
    
    print("Sample data generation completed successfully!")
    print("You can now train the ML model using this data.")

if __name__ == "__main__":
    main()