from datetime import datetime, timedelta
import random

# 1. Simulate the data pattern (Busy Oct, Empty Nov-Dec, Busy Jan)
data = []

# October 2025: Active
start_oct = datetime(2025, 10, 1).date()
for i in range(30):
    data.append({'date': start_oct + timedelta(days=i), 'revenue': random.randint(50000, 200000)})

# HUGE GAP (Nov, Dec missing)

# Jan 2026: Active again
start_jan = datetime(2026, 1, 1).date()
for i in range(15):
    data.append({'date': start_jan + timedelta(days=i), 'revenue': random.randint(50000, 200000)})

print(f"Total simulated records: {len(data)}")
print(f"Date range: {data[0]['date']} to {data[-1]['date']}\n")

# 2. RUN LOGIC FROM seasonal_model.py
sorted_data = sorted(data, key=lambda x: x['date'])
        
cutoff_index = 0
for i in range(1, len(sorted_data)):
    prev_date = sorted_data[i-1]['date']
    curr_date = sorted_data[i]['date']
    delta = (curr_date - prev_date).days
    
    if delta > 21: # Gap > 21 days
        print(f"  -> GAP DETECTED! {prev_date} to {curr_date} ({delta} days)")
        cutoff_index = i

if cutoff_index > 0:
    original_len = len(sorted_data)
    sorted_data = sorted_data[cutoff_index:]
    print(f"\nRESULT: Filtered! Old size: {original_len} -> New size: {len(sorted_data)}")
    print(f"New start date: {sorted_data[0]['date']}")
else:
    print("\nFAIL: No gap detected.")
