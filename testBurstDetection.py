# Import burst detection functions
from neurodsp.burst import detect_bursts_dual_threshold, compute_burst_stats

# Import simulation code for creating test data
from neurodsp.sim import sim_combined
from neurodsp.utils import set_random_seed, create_times

# Import utilities for loading and plotting data
from neurodsp.utils.download import load_ndsp_data
from neurodsp.plts.time_series import plot_time_series, plot_bursts

import matplotlib.pyplot as plt

# Set the random seed, for consistency simulating data
set_random_seed(0)

# Simulation settings
fs = 1000
n_seconds = 5

# Define simulation components
components = {'sim_synaptic_current' : {'n_neurons':1000, 'firing_rate':2,
                                        't_ker':1.0, 'tau_r':0.002, 'tau_d':0.02},
              'sim_bursty_oscillation' : {'freq' : 10, 'enter_burst' : .2, 'leave_burst' : .2}}

# Simulate a signal with a bursty oscillation with an aperiodic component & a time vector
sig = sim_combined(n_seconds, fs, components)
times = create_times(n_seconds, fs)

# Plot the simulated data
plot_time_series(times, sig, 'Simulated EEG')
plt.show()

# Settings for the dual threshold algorithm
amp_dual_thresh = (1, 2)
f_range = (8, 12)

# Detect bursts using dual threshold algorithm
bursting = detect_bursts_dual_threshold(sig, fs, amp_dual_thresh, f_range)

# Plot original signal and burst activity
plot_bursts(times, sig, bursting, labels=['Simulated EEG', 'Detected Burst'])
plt.show()

# Compute burst statistics
burst_stats = compute_burst_stats(bursting, fs)

# Print out burst statistic information
for key, val in burst_stats.items():
    print('{:15} \t: {}'.format(key, val))

# Download, if needed, and load example data file
sig = load_ndsp_data('sample_data_1.npy', folder='data')

# Set sampling rate, and create a times vector for plotting
fs = 1000
times = create_times(len(sig)/fs, fs)
# Set the frequency range to look for bursts
f_range = (8, 12)

# Detect bursts using the dual threshold algorithm
bursting = detect_bursts_dual_threshold(sig, fs, (3, 3), f_range)
# Plot original signal and burst activity
plot_bursts(times, sig, bursting, labels=['Data', 'Detected Burst'])
plt.show()

# Detect bursts using dual threshold algorithm
bursting = detect_bursts_dual_threshold(sig, fs, (1, 2), f_range)

# Plot original signal and burst activity
plot_bursts(times, sig, bursting, labels=['Data', 'Detected Burst'])
plt.show()

# Detect bursts
bursting = detect_bursts_dual_threshold(sig, fs, (1, 2), (13, 30))

# Plot original signal and burst activity
plot_bursts(times, sig, bursting, labels=['Data', 'Detected Burst'])
plt.show()

# Compute burst statistics
burst_stats = compute_burst_stats(bursting, fs)

# Print out burst statistic information
for key, val in burst_stats.items():
    print('{:15} \t: {}'.format(key, val))