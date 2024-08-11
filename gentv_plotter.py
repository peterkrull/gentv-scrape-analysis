from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import linregress
from statsmodels.tsa.stattools import acf
import time
import sys

if len(sys.argv) < 2:
    print("Please provide a file name as an argument.")
    sys.exit(1)

fig, axs = plt.subplots(2, 2, figsize=(15, 10))
while True:

    # Load data
    df = pd.read_csv(sys.argv[1])

    print(df)

    # Convert Unix timestamps to datetime
    df['time'] = pd.to_datetime(df['time'], unit='s')

    # Calculate time from the beginning of the measurement
    df['time_from_start'] = (df['time'] - df['time'].iloc[0]).dt.total_seconds()

    # Calculate derivative
    df['derivative'] = df['views'].diff() / df['time_from_start'].diff()

    # Average time between samples
    df['delta_time'] = df['time_from_start'].diff()

    print("Statistical summary:\n", df.describe())

    # Linear Regression Analysis
    slope, intercept, r_value, p_value, std_err = linregress(df['time_from_start'], df['views'])

    # Calculate the linear trend
    linear_trend = intercept + slope * df['time_from_start']

    # Subtract the linear trend from the original views data
    flat_views = df['views'] - linear_trend

    # Calculate centered moving average
    window = 100  # Adjust the window size as needed
    df['moving_avg'] = df['derivative'].rolling(window=window, center=True).mean()

    # Calculate time passed across entire dataset
    time_diff = df['time'][len(df['time'])-1] - df['time'][0]

    # Extract days, hours, minutes, and seconds
    days = time_diff.days
    hours = time_diff.seconds // 3600 # Subtract 2 hours for timezone difference
    minutes = (time_diff.seconds % 3600) // 60
    seconds = time_diff.seconds % 60

    # Construct the formatted string
    if time_diff.days > 0:
        time_passed = f"{days} days, {hours}:{minutes}:{int(seconds)} hours"
    else:
        time_passed = f"{hours}:{minutes}:{int(seconds)} hours"

    # Plot views over time
    axs[0, 0].plot(df['time_from_start'], df['views'])
    axs[0, 0].set_title(f'\'Views\' Over Time ({time_passed}) on gentv.com')
    axs[0, 0].set_xlabel('Time from Start (seconds)')
    axs[0, 0].set_ylabel('Views')

    # Plot derivative of views with moving average
    axs[0, 1].plot(df['time_from_start'], df['derivative'], label='Derivative')
    axs[0, 1].plot(df['time_from_start'], df['moving_avg'], label='Moving Average', color='orange')
    axs[0, 1].set_title('Derivative of Views with Moving Average')
    axs[0, 1].set_xlabel('Time from Start (seconds)')
    axs[0, 1].set_ylabel('Derivative [views/second]')
    axs[0, 1].set_ylim(0, 30)
    axs[0, 1].legend()

    # Plot spectrogram of derivative
    NFFT = 120  # Number of data points used in each block for the FFT
    noverlap = 110  # Number of points of overlap between blocks
    sampling_rate = 1.0 / df['time_from_start'].diff().mean()  # Calculate the sampling rate
    axs[1, 0].specgram((df['derivative'].to_numpy() - df['derivative'].mean()), NFFT=NFFT, Fs=sampling_rate, noverlap=noverlap, cmap='gist_ncar')
    axs[1, 0].set_title('Spectrogram of Derivative of Views')
    axs[1, 0].set_xlabel('Time from Start (seconds)')
    axs[1, 0].set_ylabel('Frequency (Hz)')

    # Compute and plot autocorrelation function
    acf_values = acf(flat_views, nlags=360)
    axs[1, 1].stem(range(len(acf_values)), acf_values)
    axs[1, 1].set_title('ACF(Views - Linear Trend)')
    axs[1, 1].set_xlabel('Lag [samples]')
    axs[1, 1].set_ylabel('Autocorrelation')

    # Print Linear Regression statistics
    print(f"Slope: {slope:.4f}")
    print(f"Intercept: {intercept:.4f}")
    print(f"R-squared: {r_value**2:.4f}")
    print(f"P-value: {p_value:.4f}")
    print(f"Standard Error: {std_err:.4f}")

    # Adjust layout
    plt.tight_layout()

    # Show the plots every 20 seconds
    print(time.time())
    plt.pause(20)
    axs[0,0].clear()
    axs[0,1].clear()
    axs[1,0].clear()
    axs[1,1].clear()
