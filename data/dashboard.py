import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def launch_dashboard(csv_file='pool_log.csv'):
    fig, ax = plt.subplots()
    def update(frame):
        ax.clear()
        try:
            df = pd.read_csv(csv_file)
            df['Timestamp'] = pd.to_datetime(df['Timestamp'])
            for col in df.columns[1:]:
                ax.plot(df['Timestamp'], df[col], label=col)
            ax.legend()
            ax.set_title("Pool Chemistry Over Time")
            ax.set_xlabel("Time")
            ax.set_ylabel("Value")
        except Exception as e:
            ax.text(0.5, 0.5, f"Error: {e}", ha='center')

    ani = FuncAnimation(fig, update, interval=5000)
    plt.show()
