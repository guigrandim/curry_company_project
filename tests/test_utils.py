import pandas as pd
import pytest

from src.utils import clean_code, load_data


@pytest.fixture
def raw_df():
    return pd.DataFrame({
        'ID': ['1', '2', '3'],
        'Delivery_person_Age': ['25', '30', 'NaN'],
        'Delivery_person_Ratings': ['4.5', '4.0', '3.8'],
        'Restaurant_latitude': [19.0, 19.1, 19.2],
        'Restaurant_longitude': [72.8, 72.9, 73.0],
        'Delivery_location_latitude': [19.05, 19.15, 19.25],
        'Delivery_location_longitude': [72.85, 72.95, 73.05],
        'Order_Date': ['19-03-2022', '20-03-2022', '21-03-2022'],
        'Time_Orderd': ['11:30:00', '19:45:00', '08:00:00'],
        'Time_Order_picked': ['11:45:00', '20:00:00', '08:15:00'],
        'Weatherconditions': ['conditions Sunny ', 'conditions Stormy', 'conditions Sunny'],
        'Road_traffic_density': ['Low ', 'Jam', 'Medium'],
        'Vehicle_condition': [2, 1, 3],
        'Type_of_order': ['Snack ', 'Meal', 'Drinks'],
        'Type_of_vehicle': ['motorcycle', 'scooter', 'motorcycle'],
        'multiple_deliveries': ['0', '1', '0'],
        'Festival': ['No', 'No', 'Yes'],
        'City': ['Urban', 'Metropolitian', 'Semi-Urban'],
        'Time_taken(min)': ['(min) 24', '(min) 33', '(min) 18'],
    })


def test_clean_code_removes_nan_sentinel_rows(raw_df):
    cleaned = clean_code(raw_df.copy())

    assert (cleaned['Delivery_person_Age'] != 'NaN').all()
    assert len(cleaned) == len(raw_df) - 1


def test_clean_code_column_types(raw_df):
    cleaned = clean_code(raw_df.copy())

    assert pd.api.types.is_integer_dtype(cleaned['Delivery_person_Age'])
    assert pd.api.types.is_float_dtype(cleaned['Delivery_person_Ratings'])
    assert pd.api.types.is_datetime64_any_dtype(cleaned['Order_Date'])
    assert pd.api.types.is_integer_dtype(cleaned['Time_taken(min)'])


def test_clean_code_creates_distancia_km_column(raw_df):
    cleaned = clean_code(raw_df.copy())

    assert 'distancia_km' in cleaned.columns
    assert (cleaned['distancia_km'] > 0).all()


def test_clean_code_strips_whitespace(raw_df):
    cleaned = clean_code(raw_df.copy())

    assert not cleaned['Road_traffic_density'].str.startswith(' ').any()
    assert not cleaned['Road_traffic_density'].str.endswith(' ').any()


def test_load_data_returns_cleaned_full_dataset():
    df = load_data()

    assert len(df) > 0
    assert 'distancia_km' in df.columns
    assert (df['Delivery_person_Age'] != 'NaN').all()
