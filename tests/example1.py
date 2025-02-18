import numpy as np
import matplotlib.pyplot as plt
from hvseispy import seismic, plot_tools, IO

# Read the file with data from the 3 channels.
# `data` contains 3 vectors with the acceleration data of each channel
# ! IMPORTANT: SpectraPy assumes that the channels are in order: [N, Z, E]

# data = np.loadtxt(r'hvseispy\data\Sample data\CO5620170908044918_nve100.txt', unpack=True)

data = IO.read_sac([r"hvseispy\data\Sample data\KO.KHMN..HNN.D.2023.037.064738.SAC",r"hvseispy\data\Sample data\KO.KHMN..HNZ.D.2023.037.064738.SAC",r"hvseispy\data\Sample data\KO.KHMN..HNE.D.2023.037.064738.SAC"])

# data = IO.read_mseed(r"hvseispy\data\Sample data\TK3126_100.mseed")
hvm, hv, freq = seismic.hvsr(acc_data=data,
                            dt=0.01, # inverse of the sampling rate
                            win_len=30, # length of the analysis window in seconds
                            taper=['cosine', 0.15], # taper window and application percentage (see function documentation for all accepted windows)
                            smooth_bandwidth=40, # constant of the konno-ohmachi smoothing window
                            overlap=0, # overlap between windows 
                            fftmin=0.1, # minimum frequency for FFT calculation
                            fftmax=50, # maximum frequency for FFT calculation (Nyquist frequency or lower)
                            hvmin=0.1, # minimum frequency for HV spectrum calculation
                            hvmax=50) # maximum frequency for HV spectrum calculation (Nyquist frequency or lower)

plot_tools.plot_hv(hvm, hv, freq,
                  fmin=0.1, # lower limit of the plot
                  fmax=50, # upper limit of the plot
                  name='station', # station name or spectrum identifier
                  plot_windows=True, # whether to draw all windows (if False, only plots the average window)
                  period_or_freq='freq', # plot the curves on a frequency or period axis
                  ) 

plt.show()
