import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta

timestamps = []
temperatures = []
o_p="D:/ttn-mqtt/ttn-mqtt/result.txt"
with open(o_p, 'r') as file:
    for line in file:
        parts = line.strip().split(' temperature: ')
        timestamp = datetime.fromisoformat(parts[0])
        temperature = float(parts[1])
        timestamps.append(timestamp)
        temperatures.append(temperature)

df = pd.DataFrame({
    'timestamp': timestamps,
    'temperature': temperatures
})
df = df.sort_values('timestamp')

end_time = df['timestamp'].max()
start_time = end_time - timedelta(minutes=20)
mask = (df['timestamp'] >= start_time) & (df['timestamp'] <= end_time)
df_filtered = df.loc[mask]

plt.figure(figsize=(12, 6))
plt.plot(df_filtered['timestamp'], df_filtered['temperature'], 
         'b-', linewidth=2, label='Temperature')
plt.plot(df_filtered['timestamp'], df_filtered['temperature'], 
         'bo', markersize=4)

plt.title('Temperature Measurements', 
          fontsize=14, pad=15)
plt.xlabel('Time (HH:MM:SS)', fontsize=12)
plt.ylabel('Temperature (°C)', fontsize=12)
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M:%S'))
plt.xticks(rotation=45)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()

avg_temp = df_filtered['temperature'].mean()
max_temp = df_filtered['temperature'].max()
min_temp = df_filtered['temperature'].min()
stats_text = (f'Statistics:\n'
             f'Average: {avg_temp:.1f}°C\n'
             f'Maximum: {max_temp:.1f}°C\n'
             f'Minimum: {min_temp:.1f}°C')
plt.text(0.02, 0.98, stats_text,
         transform=plt.gca().transAxes,
         verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

plt.tight_layout()
plt.savefig('results.png', dpi=300, bbox_inches='tight')
plt.show()