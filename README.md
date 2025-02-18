# HVSeisPy - Horizontal-to-Vertical Spectral Ratio (HVSR) Analysis Tool

## Overview

HVSeisPy is a Python package designed for performing Horizontal-to-Vertical Spectral Ratio (HVSR) analysis on seismic data. The package provides tools for reading seismic data, processing it, and calculating the HVSR, which is commonly used in seismology for site characterization and estimating the fundamental frequency of soil layers.

The package includes functionalities for:
- Reading seismic data from various file formats (e.g., SAC, MSEED, ASCII).
- Windowing and tapering seismic signals.
- Computing Fourier spectra and smoothing them using the Konno-Ohmachi algorithm.
- Calculating the HVSR and visualizing the results.

## Installation

Install HVSeisPy using `pip`:

```bash
pip install hvseispy
```

To install HVSeisPy, ensure you have Python 3.7 or later installed. You can install the required dependencies using `pip`:

```bash
pip install numpy scipy obspy matplotlib pykooh
```

Alternatively, clone the repository or download the scripts to your local machine:

```bash
git clone https://github.com/JOchoa51/HVSeisPy.git
cd HVSeisPy
```

## Usage

### Reading Seismic Data

HVSeisPy supports reading seismic data from SAC, MSEED, and ASCII files. Use the `read_sac`, `read_mseed`, or `read_file` functions from the `IO` module to load your data.

```python
from hvseispy.IO import read_sac, read_mseed, read_file

# Example: Reading SAC files
north, vertical, east = read_sac(['path_to_sac_file1', 'path_to_sac_file2'])

# Example: Reading MSEED files
north, vertical, east = read_mseed('path_to_mseed_file')

# Example: Reading ASCII files
north, vertical, east = read_file('path_to_ascii_file', skiprows=0)
```

### Processing Seismic Data

The `seismic` module provides functions for processing seismic data, including windowing, tapering, and calculating the HVSR.

```python
from hvseispy.seismic import hvsr

# Example: Calculating HVSR
hv_mean, hv, freq = hvsr(
    acc_data=[north, vertical, east],  # Input data as a list of numpy arrays
    dt=0.01,  # Sampling period in seconds
    win_len=20.0,  # Window length in seconds
    taper=('cosine', 0.05),  # Taper type and amount
    smooth_bandwidth=40.0,  # Smoothing bandwidth for Konno-Ohmachi smoothing
    overlap=0.5,  # Overlap between windows (0 to 1)
    fftmin=0.1,  # Minimum frequency for FFT
    fftmax=50.0,  # Maximum frequency for FFT
    hvmin=0.1,  # Minimum frequency for HVSR
    hvmax=10.0  # Maximum frequency for HVSR
)
```

### Plotting Results

The `plot_tools` module provides functions for visualizing seismic signals, FFT spectra, and HVSR results.

```python
from hvseispy.plot_tools import plot_signal, plot_fft, plot_hv

# Example: Plotting the seismic signal
fig = plot_signal(north, vertical, east, dt=0.01, name='Station_Name')

# Example: Plotting the FFT spectrum
fig = plot_fft([north, vertical, east], freq, name='Station_Name', fmin=0.1, fmax=50.0)

# Example: Plotting the HVSR
fig = plot_hv(hv_mean, hv, freq, fmin=0.1, fmax=10.0, name='Station_Name', plot_windows=True)
```

## Modules

### `IO.py`

This module contains functions for reading seismic data from different file formats:
- `read_sac`: Reads SAC files.
- `read_mseed`: Reads MSEED files.
- `read_file`: Reads ASCII files.
- `read_cires`: Reads specific CIRES format files (this is for a very specific file format, use `read_file` instead).

### `specsignal.py`

This module contains signal processing functions:
- `taper`: Applies a taper to the signal.
- `window`: Splits the signal into windows.
- `spectrum`: Computes the Fourier spectrum of the signal.
- `konnoohmachi_smoothing`: Smooths the spectrum using the Konno-Ohmachi algorithm.
- `konnoohmachi_smoothing_opt`: Optimized version of the Konno-Ohmachi smoothing function.

### `seismic.py`

This module contains the main functions for HVSR analysis:
- `hv_ratio`: Calculates the HVSR.
- `_process_hvsr`: Processes the seismic data and computes the HVSR.
- `hvsr`: High-level function for calculating HVSR from seismic data.

### `plot_tools.py`

This module contains functions for plotting seismic data and results:
- `plot_signal`: Plots the seismic signal.
- `plot_windows`: Plots the seismic signal with analysis windows.
- `plot_fft`: Plots the FFT spectrum.
- `plot_hv`: Plots the HVSR.

### `misc.py`

This module contains utility functions:
- `save_results`: Saves the HVSR and FFT results to a text file.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request if you have any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](https://mit-license.org/) file for details.

## Acknowledgments

- The Konno-Ohmachi smoothing algorithm is implemented using the `pykooh` library.
- The ObsPy library is used for reading seismic data formats.

## Contact

For any questions or feedback, please contact the maintainer at [ochoacontrerasjesus8@gmail.com].
