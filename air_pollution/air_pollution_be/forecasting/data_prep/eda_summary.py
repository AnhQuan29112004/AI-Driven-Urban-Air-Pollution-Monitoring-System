from .extract import load_data
import matplotlib.pyplot as plt

df_uci = load_data("parquet_uci", "pm25")
df_hanoi = load_data("parquet_hanoi", "pm25")

print("UCI shape:", df_uci.shape)
print("Hanoi shape:", df_hanoi.shape)
print(df_uci.describe())

# Plot nhanh để check
df_uci['pm25'].plot(title="UCI PM2.5 (pre-train)")
plt.show()
df_hanoi['pm25'].plot(title="Hanoi PM2.5 (fine-tune)")
plt.show()