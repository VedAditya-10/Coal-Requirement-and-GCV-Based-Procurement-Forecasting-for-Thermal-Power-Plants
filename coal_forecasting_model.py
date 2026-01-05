import pandas as pd
import numpy as np
from datetime import datetime
import calendar

print("Loading dataset...")
df = pd.read_csv('FINAL_MERGED_DATA.csv')
print(f"Loaded {len(df):,} rows")

def get_days_in_month(year, month):
    return calendar.monthrange(year, month)[1]

def calculate_electricity_generation(capacity_mw, plf, days_in_month):
    if pd.isna(capacity_mw) or pd.isna(plf):
        return None
    
    if plf > 1:
        plf = plf / 100
    
    electricity_kwh = capacity_mw * plf * 24 * days_in_month * 1000
    return electricity_kwh

def calculate_coal_requirement(electricity_kwh, heat_rate_kcal_kwh, gcv_kcal_kg, aux_consumption_pct):
    if pd.isna(electricity_kwh) or pd.isna(heat_rate_kcal_kwh) or pd.isna(gcv_kcal_kg):
        return None
    
    if aux_consumption_pct > 1:
        aux_consumption = aux_consumption_pct / 100
    else:
        aux_consumption = aux_consumption_pct
    
    coal_kg = (electricity_kwh * heat_rate_kcal_kwh) / (gcv_kcal_kg * (1 - aux_consumption))
    coal_tonnes = coal_kg / 1000
    
    return coal_tonnes

def forecast_coal_demand(plant_key, year, month, target_plf=None, target_energy_mwh=None):
    if target_plf is None and target_energy_mwh is None:
        raise ValueError("Either target_plf or target_energy_mwh must be provided")
    
    if target_plf is not None and target_energy_mwh is not None:
        raise ValueError("Provide only one: target_plf OR target_energy_mwh")
    
    plant_data = df[df['plant_key'] == plant_key].iloc[0]
    
    capacity_mw = plant_data['Capacity']
    heat_rate = plant_data.get('Actual SHR', 2750)
    gcv = plant_data['Estimated_GCV_kcal_per_kg']
    coal_grade = plant_data['Coal_Grade']
    aux_consumption = plant_data.get('Auxiliary consumption (%)', 8.0)
    
    days = get_days_in_month(year, month)
    
    if target_plf is not None:
        electricity_kwh = calculate_electricity_generation(capacity_mw, target_plf, days)
        plf_used = target_plf if target_plf <= 1 else target_plf / 100
    else:
        electricity_kwh = target_energy_mwh * 1000
        plf_used = electricity_kwh / (capacity_mw * 24 * days * 1000)
    
    coal_required_tonnes = calculate_coal_requirement(
        electricity_kwh, heat_rate, gcv, aux_consumption
    )
    
    result = {
        'plant_key': plant_key,
        'plant_name': plant_data.get('Name of TPS', plant_key),
        'year': year,
        'month': month,
        'days_in_month': days,
        'capacity_mw': capacity_mw,
        'target_plf': plf_used,
        'electricity_generated_kwh': electricity_kwh,
        'electricity_generated_mwh': electricity_kwh / 1000,
        'heat_rate_kcal_kwh': heat_rate,
        'estimated_gcv_kcal_kg': gcv,
        'coal_grade': coal_grade,
        'auxiliary_consumption_pct': aux_consumption,
        'coal_required_tonnes': coal_required_tonnes,
    }
    
    return result


if __name__ == "__main__":
    print("\n" + "="*80)
    print("COAL DEMAND FORECASTING MODEL - DEMO")
    print("="*80)
    
    print("\n[Example 1] Forecast using Target PLF")
    print("-" * 80)
    
    result1 = forecast_coal_demand(
        plant_key='DADRI_NCTPP',
        year=2024,
        month=6,
        target_plf=0.75
    )
    
    print(f"Plant: {result1['plant_name']}")
    print(f"Period: {result1['month']}/{result1['year']}")
    print(f"Capacity: {result1['capacity_mw']:.0f} MW")
    print(f"Target PLF: {result1['target_plf']*100:.1f}%")
    print(f"\nOutputs:")
    print(f"  Electricity Generated: {result1['electricity_generated_mwh']:,.0f} MWh")
    print(f"  Coal Grade: {result1['coal_grade']}")
    print(f"  GCV: {result1['estimated_gcv_kcal_kg']:.0f} kcal/kg")
    print(f"  Coal Required: {result1['coal_required_tonnes']:,.0f} tonnes")
    
    print("\n[Example 2] Forecast using Target Energy")
    print("-" * 80)
    
    result2 = forecast_coal_demand(
        plant_key='VINDHYACHAL_STPS',
        year=2024,
        month=7,
        target_energy_mwh=500000
    )
    
    print(f"Plant: {result2['plant_name']}")
    print(f"Period: {result2['month']}/{result2['year']}")
    print(f"Capacity: {result2['capacity_mw']:.0f} MW")
    print(f"Target Energy: {result2['electricity_generated_mwh']:,.0f} MWh")
    print(f"Achieved PLF: {result2['target_plf']*100:.1f}%")
    print(f"\nOutputs:")
    print(f"  Coal Grade: {result2['coal_grade']}")
    print(f"  GCV: {result2['estimated_gcv_kcal_kg']:.0f} kcal/kg")
    print(f"  Coal Required: {result2['coal_required_tonnes']:,.0f} tonnes")
    
    print("\n[Example 3] Batch Forecasting")
    print("-" * 80)
    
    plants_to_forecast = ['DADRI_NCTPP', 'RIHAND_STPS', 'VINDHYACHAL_STPS']
    target_plf = 0.80
    
    batch_results = []
    for plant in plants_to_forecast:
        try:
            result = forecast_coal_demand(plant, 2024, 8, target_plf=target_plf)
            batch_results.append(result)
        except Exception as e:
            print(f"  Error forecasting {plant}: {e}")
    
    batch_df = pd.DataFrame(batch_results)
    
    print(f"\nForecasted {len(batch_df)} plants for August 2024 at {target_plf*100:.0f}% PLF:")
    print(batch_df[['plant_key', 'capacity_mw', 'electricity_generated_mwh', 
                    'coal_grade', 'coal_required_tonnes']].to_string(index=False))
    
    print(f"\nTotal coal required: {batch_df['coal_required_tonnes'].sum():,.0f} tonnes")
    
    print("\n" + "="*80)
    print("[SUCCESS] Forecasting model ready!")
    print("="*80)
