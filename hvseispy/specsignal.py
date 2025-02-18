# matplotlib.use('Agg')

import matplotlib.pyplot as plt
# plt.rcParams['figure.dpi'] = 400
# plt.rcParams['figure.figsize'] = [10,10]
from matplotlib.patches import Rectangle

import numpy as np
from scipy.fft import rfft, rfftfreq
from scipy.signal import detrend
from scipy.signal import windows

from obspy.signal.util import smooth
from obspy import read
from time import perf_counter
import pykooh  # https://github.com/arkottke/pykooh
import warnings
warnings.filterwarnings("ignore")

def taper(
        north: np.ndarray,
        vertical: np.ndarray,
        east: np.ndarray,
        type: str,
        amount:float=1.0
        ) -> tuple:

    """Taper the signal as to avoid continuity problems with FFT

    :warning: **Not longer in use**, will be removed

    Args:
    ----
        - north (np.ndarray): North component of the acceleration data
        - vertical (np.ndarray): Vertical component of the acceleration data
        - east (np.ndarray): East component of the acceleration data
        - type (str): Window type to apply the taper. Available windows are {'barthann','bartlett','blackman','blackmanharris','bohman','boxcar','chebwin','cosine','exponential','flattop','hamming','hann','lanczos','nuttall','parzen','taylor','triang','tukey'}

    Returns:
        tuple: North, vertical and east components tapered. Also includes the window used for tapering

    Changelog:
        - 10/OCT/23:\n
            --> Added removal warning
        - 06/APR/24:\n
            --> Added taper amount option

    
    """
    north = np.array(north)
    vertical = np.array(vertical)
    east = np.array(east)

    try:
        w = windows.get_window(type, north.shape[-1])
    except ValueError:
        print('Window type not found, please choose one aviailable from the list')
        return
    
    w = 1-amount*(1-w)
    north = north*w
    vertical = vertical*w
    east = east*w

    return north, vertical, east, w

def window(
        data: np.ndarray|tuple,
        window_length: float,
        fs: float,
        overlap:float=0
        ) -> np.ndarray:
    
    """Split the signal into the given number of sections

    Args:
    ----
        data (ndarray): Signal data to be split into sections
        window_length (float): Length of analysis window in seconds
        fs (float): Sampling frequency
        overlap (float): Ammount of overlap  between segments as a decimal from 0 to 1.

    Returns:
    -------
        tuple: Tuple of north, vertical, east and window number
    
    Changelog:
    ---------
        - 13/SEP/2023:\n
            --> Added cropping function to keep equal dimensions
        - 24/OCT/2023:\n
            --> Added tapering function set to True by default
        - 25/OCT/2023:\n
            --> Changed the function so it's compatible with any array size
        - 06/APR/2024:\n
            --> Added overlap function \n
            --> Removed default cosine_taper function \n
            --> Cropping is no longer needed \n
            --> Improved overall precission and performance \n

    """
    # N = len(data[0])


    try:
        N = data[0].shape[-1]
    except IndexError:
        raise Warning("\nData doesn't have the right shape, did you pass all the channels?")
    
    section_length = int(window_length * fs)  # número de muestras por sección
    window_number = N//section_length  # numero de ventanas
    # print(f'Window number: {window_number}')
    # print(f'Extra windows due to overlap: {int(overlap * window_number)}')

    if len(data) != 1: # Si se está tratando con múltiples vectores al mism0 tiempo (e.g. múltiples canales de un sismograma)
        data_split = []
        for arr in data:
            arr_split = []

            # Corta los vectores en los índices especificados
                # Índices de corte para las ventanas
            idxs = np.arange(0, N, section_length, dtype=int)

                # Índices de inicio 
            starts = [i - i * overlap for i in idxs]

                # Prueba si se pueden agregar más ventanas debido al traslape
            if overlap * window_number > 1:

                # Agrega cuantas sean necesarias
                for _ in range(int(overlap * window_number)):
                    starts.append(starts[-1] + section_length)
                    
            starts = np.array(starts, dtype=int)
            ends = starts + section_length

                # Corta los vectores [s:e] con longitud section_length
            for s, e in zip(starts, ends):
                arr_split.append(arr[s:e])

                # Elimina la última ventana en caso de ser de menor tamaño
            if not np.all(arr_split == arr_split[0]):
                # try:
                arr_split = arr_split[:len(arr_split)-1]
                # except np.VisibleDeprecationWarning:
                #     arr_split = arr_split[:len(arr_split)-1]

            # Añade los vectores cortados a una lista
            data_split.append(arr_split)

        # Convierte la lista en un numpy array
        data_split = np.array(data_split)
    else:
        data_split = np.array_split(data, window_number)
        mindim = min(len(arr) for arr in data_split)
        data_split = np.array([arr[:mindim] for arr in data_split])

    return data_split

def spectrum(
        north: np.ndarray,
		vertical: np.ndarray,
		east: np.ndarray,
		dt: float,
		fmin:float = 0.1,
		fmax:float = 50
        ) -> tuple:
    """Calculates the right-hand-side amplitude spectrum of the signal

    Args
    ----
        - north (ndarray): North-component signal
        - vertical (ndarray): Vertical-component signal
        - east (ndarray): East-component signal
        - dt (float): time precision
        - fmin (float): minimum frequency to calculate the FFT from. Defaults to 0.1
        - fmax (float): maximum frequency to calculate the FFT from. Defaults to 50

    Returns
    -------
        - tuple: Tuple that contains the north, vertical and east amplitude spectrums
        - array: Frequency array

    Changelog
    ---------
        - 09/SEP/2023: \n
            --> Changed lists comprehensions to np.apply_along_axis() function for simplicity and performance.\n
            --> Added code to crop the FFT and frequency arrays to the specified fmin and fmax
        - 11/SEP/2023: \n
            --> Added a loop to check whether the cutoff frequencies are inside the right interval
        - 25/SEP/2023:\n
            --> Changed the output type to numpy arrays. Now there are two outputs, one with the FFT data and another with the frequency array
        - 25/OCT/2023:\n
            --> Changed function name from `rhs_spectrum` to `spectrum`
    """
    # TODO: make it work with arrays of any dimension

    north = np.array(north)
    vertical = np.array(vertical)
    east = np.array(east)

    if north.ndim == 1:
        N = len(north)
    else:
        N = len(north[0])  # longitud de cada seccion
    freq = rfftfreq(N, dt)

    # Encuentra el índice del elemento más cercano a fmin y fmax
    fmin_loc = np.abs(freq-fmin)
    fmin_loc = np.argmin(fmin_loc)
    fmax_loc = np.abs(freq-fmax)
    fmax_loc = np.argmin(fmax_loc)

    # Comprueba que el valor de freq no sea menor o mayor que fmin y fmax
    while freq[fmin_loc] < fmin:
        fmin_loc += 1

    while freq[fmax_loc] > fmax:
        if freq[fmax_loc] == float(fmax):
            break
        fmax_loc -= 1

    # Cálculo y normalización de los espectros de Fourier
    if north.ndim != 1 and vertical.ndim != 1 and east.ndim != 1:
        fftnorth = np.apply_along_axis(
            func1d=lambda t: np.abs(rfft(t)/(N/2)), 
            axis=-1, 
            arr=north)
        fftvertical = np.apply_along_axis(
            func1d=lambda t: np.abs(rfft(t)/(N/2)), 
            axis=-1, 
            arr=vertical)
        ffteast = np.apply_along_axis(
            func1d=lambda t: np.abs(rfft(t)/(N/2)), 
            axis=-1, 
            arr=east)
    else:
        fftnorth = np.abs(rfft(north)/(N/2))
        fftvertical = np.abs(rfft(vertical)/(N/2))
        ffteast = np.abs(rfft(east)/(N/2))

    # Corta el vector de frecuencias desde fmin hasta fmax
    freq = freq[fmin_loc:fmax_loc]

    fftnorth = np.array(
        np.split(
            ary=fftnorth, 
            indices_or_sections=[fmin_loc, fmax_loc], 
            axis=-1)[1])
    fftvertical = np.array(
        np.split(
            ary=fftvertical, 
            indices_or_sections=[fmin_loc, fmax_loc], 
            axis=-1)[1])
    ffteast = np.array(
        np.split(
            ary=ffteast, 
            indices_or_sections=[fmin_loc, fmax_loc], 
            axis=-1)[1])


    return np.array([fftnorth, fftvertical, ffteast]), np.array(freq)

def standard_smoothing(
		data: list,
		smoothie: int
        ) -> tuple:
    """Smooths the data by calculating a moving average. Wraps Obspy's smooth function

    Args
    ----
        - data (list): List with the data to be smoothed. Can be one or multiple signals
        - smoothie (int): number of past/future values to calculate moving average

    Returns
    -------
        tuple: tuple containing the smoothed data
    """
    amp = []
    s = perf_counter()
    for i in data:
        amp.append(smooth(i, smoothie=smoothie))
    amp = np.array(amp, dtype=object)

    e = perf_counter()
    # print(f'{round(e-s, 4)} s')

    return amp

def konnoohmachi_smoothing(
        data: np.ndarray,
		freq: np.ndarray,
		bandwidth:float = 40
        ) -> np.ndarray:
    """Smooths the data using Konno-Ohmachi (1998) algorithm. Wraps PyKooh's smooth function

    Args
    ----
        - data (ndarray): Vector data to be smoothed
        - freq (ndarray): Frequency vector
        - bandwidth (int): Strength of the filter. A lower bandwidth is a stronger smoothing.

    Returns
    -------
        - tuple: smoothed spectrum

    Notes
    -----
        # TODO:
        Maybe will be removed in future versions
    """
    warnings.warn('This function will be removed in future versions. Use `konnoohmachi_smoothing_opt` instead', DeprecationWarning)
    smooth = []
    count = 0
    s = perf_counter()  # Cuenta el tiempo de ejecución del ciclo
    for i in data:
        # WITH PYKOOH (better performance than Obspy)
        smooth.append(pykooh.smooth(freq, freq, i, b=bandwidth))

        # print(f'Ventana {count} lista')

    # Convierte lista en numpy array
    smooth = np.array(smooth, dtype=object)

    e = perf_counter()
    # print(f'{round(e-s, 4)} s transcurridos')

    return smooth


def konnoohmachi_smoothing_opt(
        data: np.ndarray,
		freq: np.ndarray,
		bandwidth:float = 40,
		axis=-1
        ) -> np.ndarray:
    """Smooths the data using Konno-Ohmachi (1998) algorithm.\n
    Optimized version with numpy vectorization and cython for smoothing.\n
    Up to 2x faster than normal version when already allocated in memory

    Args
    ----
        - data (ndarray): Data vector to be smoothed
        - freq (ndarray): Frequency vector
        - bandwidth (int): Strength of the filter. A lower bandwidth is a stronger smoothing. Defaults to 40.
        - axis (int): Axis along which the data will be smoothed. Defaults to -1

    Returns
    -------
        - ndarray: smoothed data
    
    Changelog
    ---------
    - 10/SEP/23:\n
        --> Added the function
    - 24/SEP/23:\n
        --> Added support for arrays of any dimension
    """

    data_smooth = np.apply_along_axis(
                    func1d=lambda t: pykooh.smooth(freq, freq, t, b=bandwidth, use_cython=True), 
                    arr=data, 
                    axis=axis
                )
    return data_smooth

def konnoohmachi_matlab(
        signal: np.ndarray,
		freq_array: np.ndarray,
		smooth_coeff: float = 40
        ) -> np.ndarray:
    """
    This function is defined only for compatibility with the Matlab version of the Konno-Ohmachi smoothing function. \n
    Function taken from \n
    Hamdullah Livaoglu (2023). Konno-Ohmachi smoothing function for ground motion spectra (https://www.mathworks.com/matlabcentral/fileexchange/68205-konno-ohmachi-smoothing-function-for-ground-motion-spectra), MATLAB Central File Exchange. Retrieved septiembre 12, 2023.

    Notes
    -----
    Added 12/SEP/2023
    
    """
    x = signal
    f = freq_array
    f_shifted = f / (1 + 1e-4)
    L = len(x)
    y = np.zeros(L)

    for i in range(L):
        if i != 0 and i != L - 1:
            z = f_shifted / f[i]
            w = ((np.sin(smooth_coeff * np.log10(z)) / smooth_coeff) / np.log10(z)) ** 4
            w[np.isnan(w)] = 0
            y[i] = np.sum(w * x) / np.sum(w)
    
    y[0] = y[1]
    y[-1] = y[-2]
    
    return y
