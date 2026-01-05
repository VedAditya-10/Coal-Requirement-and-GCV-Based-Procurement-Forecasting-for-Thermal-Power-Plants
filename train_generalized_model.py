import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import lightgbm as lgb
import pickle
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("GENERALIZED PLF PREDICTION MODEL")
print("="*80)

df = pd.read_csv('FINAL_MERGED_DATA.csv')
print(f"\nDataset: {df.shape}")

if 'Actual avg PLF' in df.columns:
    df['PLF'] = df['Actual avg PLF']
    if df['PLF'].max() > 1:
        df['PLF'] = df['PLF'] / 100

df = df[df['Capacity'].notna()]
print(f"After filtering (with Capacity): {df.shape}")

df = df.sort_values(['plant_key', 'Year', 'Month'])
df['date'] = pd.to_datetime(df[['Year', 'Month']].assign(day=1))

print("\n[1] Creating Technology Features...")
tech_map = {'Subcritical': 0, 'Supercritical': 1, 'Ultra Supercritical': 2}
df['technology_encoded'] = df['Technology'].map(tech_map).fillna(0)

def get_capacity_band(capacity):
    if capacity < 500:
        return 'Small'
    elif capacity < 1500:
        return 'Medium'
    else:
        return 'Large'

df['capacity_band'] = df['Capacity'].apply(get_capacity_band)
band_map = {'Small': 0, 'Medium': 1, 'Large': 2}
df['capacity_band_encoded'] = df['capacity_band'].map(band_map)

df['capacity_normalized'] = (df['Capacity'] - df['Capacity'].mean()) / df['Capacity'].std()

print("\n[2] Creating Seasonality Features...")
df['month_sin'] = np.sin(2 * np.pi * df['Month'] / 12)
df['month_cos'] = np.cos(2 * np.pi * df['Month'] / 12)
df['quarter'] = df['Month'].apply(lambda x: (x-1)//3 + 1)
df['is_summer'] = df['Month'].isin([4, 5, 6]).astype(int)
df['is_monsoon'] = df['Month'].isin([7, 8, 9]).astype(int)
df['is_winter'] = df['Month'].isin([11, 12, 1, 2]).astype(int)

print("\n[3] Creating Technology-Month Averages...")
tech_month_avg = df.groupby(['Technology', 'Month'])['PLF'].mean().reset_index()
tech_month_avg.columns = ['Technology', 'Month', 'avg_plf_tech_month']
df = df.merge(tech_month_avg, on=['Technology', 'Month'], how='left')

band_month_avg = df.groupby(['capacity_band', 'Month'])['PLF'].mean().reset_index()
band_month_avg.columns = ['capacity_band', 'Month', 'avg_plf_band_month']
df = df.merge(band_month_avg, on=['capacity_band', 'Month'], how='left')

print("\n[4] Creating Optional Historical Features (for existing plants)...")
df['PLF_lag1'] = df.groupby('plant_key')['PLF'].shift(1)
df['PLF_lag3'] = df.groupby('plant_key')['PLF'].shift(3)
df['PLF_rolling_mean_3'] = df.groupby('plant_key')['PLF'].transform(
    lambda x: x.rolling(window=3, min_periods=1).mean().shift(1)
)

print(f"\nFinal dataset shape: {df.shape}")

base_features = [
    'technology_encoded',
    'capacity_normalized',
    'capacity_band_encoded',
    'Month', 'quarter', 'month_sin', 'month_cos',
    'is_summer', 'is_monsoon', 'is_winter',
    'avg_plf_tech_month',
    'avg_plf_band_month',
]

enhanced_features = base_features + [
    'PLF_lag1',
    'PLF_lag3',
    'PLF_rolling_mean_3',
]

print("\n" + "="*80)
print("TRAINING BASE MODEL (for new plants)")
print("="*80)

df_base = df[base_features + ['PLF', 'date']].dropna()
print(f"Base model training data: {df_base.shape}")

split_date = df_base['date'].quantile(0.8)
train_base = df_base[df_base['date'] < split_date]
test_base = df_base[df_base['date'] >= split_date]

X_train_base = train_base[base_features]
y_train_base = train_base['PLF']
X_test_base = test_base[base_features]
y_test_base = test_base['PLF']

print(f"Train: {len(train_base)}, Test: {len(test_base)}")

params = {
    'objective': 'regression',
    'metric': 'rmse',
    'boosting_type': 'gbdt',
    'num_leaves': 31,
    'learning_rate': 0.05,
    'feature_fraction': 0.9,
    'verbose': -1,
}

train_data_base = lgb.Dataset(X_train_base, label=y_train_base)
valid_data_base = lgb.Dataset(X_test_base, label=y_test_base, reference=train_data_base)

base_model = lgb.train(
    params,
    train_data_base,
    num_boost_round=500,
    valid_sets=[train_data_base, valid_data_base],
    callbacks=[lgb.early_stopping(50), lgb.log_evaluation(100)]
)

y_pred_base = np.clip(base_model.predict(X_test_base), 0, 1)
rmse_base = np.sqrt(mean_squared_error(y_test_base, y_pred_base))
mae_base = mean_absolute_error(y_test_base, y_pred_base)
r2_base = r2_score(y_test_base, y_pred_base)

print(f"\n[BASE MODEL RESULTS]")
print(f"RMSE: {rmse_base:.4f} ({rmse_base*100:.2f}% error)")
print(f"MAE: {mae_base:.4f}")
print(f"R²: {r2_base:.4f}")

print("\n" + "="*80)
print("TRAINING ENHANCED MODEL (for existing plants)")
print("="*80)

df_enhanced = df[enhanced_features + ['PLF', 'date']].dropna()
print(f"Enhanced model training data: {df_enhanced.shape}")

split_date_enh = df_enhanced['date'].quantile(0.8)
train_enh = df_enhanced[df_enhanced['date'] < split_date_enh]
test_enh = df_enhanced[df_enhanced['date'] >= split_date_enh]

X_train_enh = train_enh[enhanced_features]
y_train_enh = train_enh['PLF']
X_test_enh = test_enh[enhanced_features]
y_test_enh = test_enh['PLF']

print(f"Train: {len(train_enh)}, Test: {len(test_enh)}")

train_data_enh = lgb.Dataset(X_train_enh, label=y_train_enh)
valid_data_enh = lgb.Dataset(X_test_enh, label=y_test_enh, reference=train_data_enh)

enhanced_model = lgb.train(
    params,
    train_data_enh,
    num_boost_round=500,
    valid_sets=[train_data_enh, valid_data_enh],
    callbacks=[lgb.early_stopping(50), lgb.log_evaluation(100)]
)

y_pred_enh = np.clip(enhanced_model.predict(X_test_enh), 0, 1)
rmse_enh = np.sqrt(mean_squared_error(y_test_enh, y_pred_enh))
mae_enh = mean_absolute_error(y_test_enh, y_pred_enh)
r2_enh = r2_score(y_test_enh, y_pred_enh)

print(f"\n[ENHANCED MODEL RESULTS]")
print(f"RMSE: {rmse_enh:.4f} ({rmse_enh*100:.2f}% error)")
print(f"MAE: {mae_enh:.4f}")
print(f"R²: {r2_enh:.4f}")

print("\n" + "="*80)
print("SAVING MODELS")
print("="*80)

base_model.save_model('plf_base_model.txt')
enhanced_model.save_model('plf_enhanced_model.txt')

metadata = {
    'base_features': base_features,
    'enhanced_features': enhanced_features,
    'base_metrics': {'rmse': rmse_base, 'mae': mae_base, 'r2': r2_base},
    'enhanced_metrics': {'rmse': rmse_enh, 'mae': mae_enh, 'r2': r2_enh},
    'tech_month_avg': tech_month_avg.to_dict('records'),
    'band_month_avg': band_month_avg.to_dict('records'),
    'capacity_stats': {
        'mean': float(df['Capacity'].mean()),
        'std': float(df['Capacity'].std())
    },
    'tech_map': tech_map,
    'band_map': band_map,
}

with open('generalized_model_metadata.pkl', 'wb') as f:
    pickle.dump(metadata, f)

print("✓ Saved: plf_base_model.txt")
print("✓ Saved: plf_enhanced_model.txt")
print("✓ Saved: generalized_model_metadata.pkl")

print("\n" + "="*80)
print("[SUCCESS] Models ready for forecasting!")
print("="*80)
print(f"\nBase Model (new plants): RMSE = {rmse_base:.4f}")
print(f"Enhanced Model (existing plants): RMSE = {rmse_enh:.4f}")
