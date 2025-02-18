# matplotlib.use('Agg')
import matplotlib.pyplot as plt
# plt.rcParams['figure.dpi'] = 400
# plt.rcParams['figure.figsize'] = [10,10]
from matplotlib.patches import Rectangle

import numpy as np

import os
import colorsys

def plot_signal(
        north:np.ndarray,
        vertical:np.ndarray,
        east:np.ndarray,
        dt:float,
        name:str,
        **kwargs
        ) -> plt.figure:
    """Plots the three components of the provided acceleration data

    Args:
        north (np.ndarray): North component of the acceleration data
        vertical (np.ndarray): Vertical component of the acceleration data
        east (np.ndarray): East component of the acceleration data
        dt (float): Sampling period of the signal
        name (str): Name of the seismic station or path to the original file. Title of the plot
        kwargs: Additional arguments for the plot

    Returns:
        figure: matplotlib figure
    """    
    # Calculates the array with minimum length
    min_dim = min([len(north), len(vertical), len(east)])

    # crop the north, vertical and east array to min_dim length
    north = north[-min_dim:]
    vertical = vertical[-min_dim:]
    east = east[-min_dim:]

    n = len(north)
    # Creates a time array with the same length as the cropped arrays
    time = np.arange(0, n*dt, dt)
    time = time[-min_dim:]

    # Calculate the maximum value of the signal to set the limits of the plot
    maxvalue = np.maximum(np.abs(north), np.abs(east))
    maxvalue = np.maximum(maxvalue, np.abs(vertical))
    maxvalue = np.max(maxvalue)*1.2
    # minvalue = np.min(np.minimum(north, east))*1.2
    minvalue = -maxvalue

    nombre = os.path.basename(name)[:4]
    time_min = time/60
    fig, axes = plt.subplots(3, 1, sharex=True, figsize=(8, 10))
    ax = axes[0]
    ax.plot(time, north, **kwargs)
    ax.fill_between(time, north, where=(north > 0), color='black')
    # ax.set_title('North', fontsize=12)
    ax.set_ylim(minvalue, maxvalue)
    ax.set_ylabel(f'{nombre} N', rotation=0, labelpad=30)
    # ax.set_yticks([])

    ax = axes[1]
    ax.plot(time, vertical, **kwargs)
    ax.fill_between(time, vertical, where=(vertical > 0), color='black')
    # ax.set_title('Vertical', fontsize=12)
    ax.set_ylim(minvalue, maxvalue)
    ax.set_ylabel(f'{nombre} Z', rotation=0, labelpad=30)
    # ax.set_yticks([])

    ax = axes[2]
    ax.plot(time, east, **kwargs)
    ax.fill_between(time, east, where=(east > 0), color='black')
    # ax.set_title('East', fontsize=12)
    ax.set_ylim(minvalue, maxvalue)
    ax.set_ylabel(f'{nombre} E', rotation=0, labelpad=30)
    # ax.set_yticks([])

    fig.supxlabel('Time [s]', fontsize=12)
    plt.tick_params('x', labelsize=12)
     
    plt.subplots_adjust(hspace=0.5)
    

    return fig


def generate_hue(window_number: int) -> list:
    """
    Generate a list of HTML colors transitioning from red to purple.
    Args:
        window_number (int): The number of colors to generate.
    Returns:
        list: A list of HTML color strings representing a gradient from red to purple.
    """
       
    # list of window_number html colors from red to purple
    start_color = '#ff0000'  # Red
    end_color = '#cc00ff'  # Purple
    colors = [start_color]  # Start with the red color

    # Calculate the hue values for the rainbow spectrum
    start_hue = colorsys.rgb_to_hsv(int(start_color[1:3], 16), int(start_color[3:5], 16), int(start_color[5:7], 16))[0]
    end_hue = colorsys.rgb_to_hsv(int(end_color[1:3], 16), int(end_color[3:5], 16), int(end_color[5:7], 16))[0]

    for i in range(1, window_number - 1):
        # Interpolate the hue values between start and end hues
        hue = start_hue + (i / (window_number - 1)) * (end_hue - start_hue)

        # Convert the hue value back to RGB color
        rgb_color = colorsys.hsv_to_rgb(hue, 1, 1)

        # Convert the RGB color to HTML hexadecimal format
        color = '#{0:02X}{1:02X}{2:02X}'.format(int(rgb_color[0] * 255), int(rgb_color[1] * 255), int(rgb_color[2] * 255))
        colors.append(color)

    colors.append(end_color)

    return colors


def plot_windows(
        data: np.ndarray,
        window_length: float,
        dt: float,
        name: str,
        **kwargs
        ) -> plt.figure:
    """Plot the signal with the windows overlayed to visualize them

    Args:
    -----
        - data (np.ndarray): Array with the acceleration data for all three channels in order (North, vertical, east). Shape must be (3,N). 
        #TODO: give support for multiple array shapes
        - window_length (float): Length of the analysis window in seconds
        - dt (float): Sampling period of the signal
        - name (str): Name of the seismic station or path to the original analyzed file.
        - kwargs: Additional arguments for the plot

    Returns:
    --------
        plt.figure: matlplotlib figure
    """
    north = data[0]
    vertical = data[1]
    east = data[2]
    fs = 1/dt
    N = len(north)
    section_length = window_length * fs  # número de muestras por sección
    try:
        window_number = int(np.floor(N/section_length))  # numero de ventanas
    except ZeroDivisionError:
        window_number = 1  # numero de ventanas

    # list of window_number html colors from red to purple
    colors = generate_hue(window_number)

    nombre = os.path.basename(name)[:4]
    time = np.linspace(0, len(north)*dt, len(north))

    box_len = int(section_length)
    x_min = np.array([i*box_len for i in range(window_number)])*dt
    x_max = np.array([xmin + np.diff(x_min)[0] for xmin in x_min])

    y_max = np.max(np.maximum(np.abs(north), np.abs(east)))*1.2
    y_min = -y_max

    fig, axes = plt.subplots(3, 1, sharex=True)

    ax = axes[0]
    ax.plot(time, north, **kwargs)
    ax.fill_between(time, north, where=(north > 0), color='black')
    for xmx, xmn, c in zip(x_max, x_min, colors):
        ax.add_patch(Rectangle((xmn, y_min), xmx-xmn, y_max-y_min, alpha=0.4, facecolor=c, edgecolor='k'))
    ax.set_ylim(y_min, y_max)
    ax.set_ylabel(f'{nombre} N', rotation=0, labelpad=30)
    ax.set_yticks([])
    
    ax = axes[1]
    ax.plot(time, vertical, **kwargs)
    ax.fill_between(time, vertical, where=(vertical > 0), color='black')
    for xmx, xmn, c in zip(x_max, x_min, colors):
        ax.add_patch(Rectangle((xmn, y_min), xmx-xmn, y_max-y_min, alpha=0.4, facecolor=c, edgecolor='k'))
    ax.set_ylim(y_min, y_max)
    ax.set_ylabel(f'{nombre} Z', rotation=0, labelpad=30)
    ax.set_yticks([])

    ax = axes[2]
    ax.plot(time, east, **kwargs)
    ax.fill_between(time, east, where=(east > 0), color='black')
    for xmx, xmn, c in zip(x_max, x_min, colors):
        ax.add_patch(Rectangle((xmn, y_min), xmx-xmn, y_max-y_min, alpha=0.4, facecolor=c, edgecolor='k'))
    ax.set_ylim(y_min, y_max)
    ax.set_ylabel(f'{nombre} E', rotation=0, labelpad=30)
    ax.set_yticks([])
    
    fig.supxlabel('Time [s]', fontsize=12)
    plt.tick_params('x', labelsize=12)

    plt.subplots_adjust(hspace=0.5)
    # # plt.savefig(f'{name[:-4]}-SISMOGRAMA.png', dpi=400)
    
    # # plt.show()

    return fig

def plot_signal_windows(
        data: np.ndarray,
        dt: float,
        name: str,
        window_type:str = 'cosine',
        **kwargs
        ) -> plt.figure:
    """Plot each individual analysis window, ie, each individual section of the signal

    Args:
        - data (np.ndarray): Array with the acceleration data for all three channels in order (North, vertical, east). Shape must be (3,N). 
        - dt (float): Sampling period of the signal
        - name (str): Name of the seismic station or path of the analyzed file
        - window_type (str, optional): Window type for tapering. Available windows are: {'barthann','bartlett','blackman','blackmanharris','bohman','boxcar','chebwin','cosine','exponential','flattop','hamming','hann','lanczos','nuttall','parzen','taylor','triang','tukey'}. Defaults to 'cosine'.
        - kwargs: Additional arguments for the plot

    Returns:
        plt.figure: matplotlib figure
    """   
    north = data[0]
    vertical = data[1]
    east = data[2] 
    n = len(north[0])
    maxvalue = np.max(np.maximum(np.abs(north), np.abs(east)))*1.2
    # minvalue = np.min(np.minimum(north, east))*1.2
    minvalue = -maxvalue
    time = np.arange(0, n*dt, dt)
    nombre = os.path.basename(name)[:4]

    fig, axes = plt.subplots(3, 1, sharex=True)
    ax = axes[0]
    ax.plot(window_type, **kwargs)
    count = 0
    for i in north:
        count += 1
        ax.plot(time, i, label=str(count), lw=0.75)
    count = 0
    # ax.set_ylim(y_min, y_max)
    ax.set_ylim(minvalue, maxvalue)
    ax.set_ylabel(f'{nombre} Z', rotation=0, labelpad=30)
    ax.set_yticks([])
    
    ax = axes[1]
    ax.plot(window_type, **kwargs)
    for i in east:
        count += 1
        ax.plot(time, i, label=str(count), lw=0.75)
    count = 0
    ax.set_ylim(minvalue, maxvalue)
    ax.set_ylabel(f'{nombre} Z', rotation=0, labelpad=30)
    ax.set_yticks([])

    ax = axes[2]
    ax.plot(window_type, **kwargs)
    for i in vertical:
        count += 1
        ax.plot(time, i, lw=0.75)
    count = 0
    ax.set_ylim(minvalue, maxvalue)
    ax.set_ylabel(f'{nombre} Z', rotation=0, labelpad=30)
    ax.set_yticks([])
    
    fig.supxlabel('Time [s]', fontsize=12)
    plt.tick_params('x', labelsize=12)
    # plt.legend()
    plt.subplots_adjust(hspace=0.5)
    # plt.show()

    return fig

def plot_fft(
        data: np.ndarray,
        freq: np.ndarray,
        name: str,
        fmin: float,
        fmax: float,
        **kwargs
        ) -> plt.figure:
    """Plots the FFT spectrum 

    Args
    ----
        - data (np.ndarray): Array with the acceleration data for all three channels in order (North, vertical, east). Shape must be (3,N).
        - freq (ndarray): Frequency vector 
        - name (str): name of the file

    Changelog
    ---------
    - 08/SEP/2023:\n
        --> Corte del vector de frecuencias a los límites establecidos\n
        --> Corte de los vectores de datos a los límites establecidos
    - 09/SEP/2023: \n
        --> Removed the vector cropping function and moved it to the spectrum one
    """

    # Calcula el promedio de las ventanas
    north = np.r_[data[0]]
    vertical = np.r_[data[1]]
    east = np.r_[data[2]]

    if north.ndim != 1 and vertical.ndim != 1 and east.ndim != 1:
        n_mean = np.mean(north, axis=0)
        v_mean = np.mean(vertical, axis=0)
        e_mean = np.mean(east, axis=0)
    else:
        n_mean = north
        v_mean = vertical
        e_mean = east

    nombre = os.path.basename(name)[:4]

    plt.semilogx(freq, v_mean, color='r', label='Z', **kwargs)
    plt.semilogx(freq, n_mean, color='g', label='N', **kwargs)
    plt.semilogx(freq, e_mean, color='b', label='E', **kwargs)

    
    plt.title(f'{nombre} - FFT', fontsize=15)
    plt.xlabel("Frequency [Hz]", fontsize=12, labelpad=10)
    plt.ylabel('Amplitude', fontsize=12, labelpad=10)
    plt.xlim(fmin, fmax)
    plt.grid(ls='--', which='both')
    plt.legend()
    plt.tick_params('both', labelsize=12)

    # plt.savefig(f'{name[:-4]}-FFT.png', dpi=400)
    # plt.show()

    fig = plt.gcf()
    return fig

def plot_hv(
        HV_mean:np.ndarray,
        HV:np.ndarray,
        freq:np.ndarray,
        fmin:float,
        fmax:float,
        name:str = None,
        plot_windows:bool = True,
        period_or_freq:str = 'freq',
        **kwargs
        ) -> plt.figure:
    """Generates a plot for the HV Spectral Ratio, indicating all the analysis windows and the position of the maximum amplitude 

    Args:
    ----
        - HV_mean (np.ndarray): 1D HV spectrum with the mean value of all the windows. If there's only one window, HV and HV_mean will be the same.
        - HV (np.ndarray): HV spectrum of all the windows. It can be a 2D array
        - freq (np.ndarray): Frequency array
        - fmin (float): Minimum frequency for the plot
        - fmax (float): Maximum frequency for the plot
        - name (str): Name of the analyzed seismic station or path of the original analyzed file. Title of the plot.
        - plot_windows (bool, optional): Whether to show all the analysis windows or not. If False, only the mean value is visible. Defaults to True.
        - period_or_freq (str, optional): Whether to plot HVSR against period or frequency. Defaults to 'freq'.
        - kwargs: Additional arguments for the plot

    Returns:
    -------
        fig: matplotlib figure with the HV Spectral Ratio graph
    
    Changelog:
    ---------
        - 09/SEP/23:\n
            --> Changed xmin, xmax to fmin, fmax
            --> Added textbox to the upper right corner to indicate frequency and amplitude
        - 14/SEP/23:\n
            --> Added the option to plot against frequency or period
        - 6/APR/24:\n
            --> Now the standard deviation of the peaks and curves are visible
        - 7/APR/24:\n
            --> The color of the curves is now the same as the corresponding window
    """    

    maxval = np.nanargmax(HV_mean)

    if name is None:
        nombre = ''
    elif name is not None:
        nombre = name
    elif os.path.basename(name).endswith('.txt') or '.' not in os.path.basename(name):
        nombre = os.path.basename(name)[:4]
    else:
        nombre = os.path.basename(name.split(".")[0])

    ytext = round(np.nanmax(HV_mean), 4)

    colors = generate_hue(len(HV))

    if period_or_freq == 'period':
        period = 1/freq

        if plot_windows==True and HV.ndim != 1:
            for hv, c in zip(HV, colors):
                plt.semilogx(period, hv, lw=0.5, zorder=10, c=c, **kwargs)
        
        stdev = np.std(period[np.argmax(HV, axis=-1)])
        ax = plt.gca()
        ax.add_patch(Rectangle(
                                xy=(period[np.argmax(HV_mean)]-stdev, 0),
                                width=stdev,
                                height=np.max(HV.ravel())*1.1,
                                facecolor='#cccccc', 
                                linewidth=0, 
                                alpha=1, 
                                zorder=5
                            ),
                    )
        ax.add_patch(Rectangle(
                                xy=(period[np.argmax(HV_mean)], 0),
                                width=stdev,
                                height=np.max(HV.ravel())*1.1,
                                facecolor='#999999', 
                                linewidth=0, 
                                alpha=1, 
                                zorder=5
                            ),
                    )

        plt.semilogx(period, HV_mean, color='k', lw=1.5, zorder=10, **kwargs)

        plt.semilogx(period, HV_mean+np.std(HV.astype(float), axis=0), c='k', ls='--', zorder=10, **kwargs)
        plt.semilogx(period, HV_mean-np.std(HV.astype(float), axis=0), c='k', ls='--', zorder=10, **kwargs)

        xtext = round(period[maxval], 4)
        xtext_coord = 0.275
        plot_text = f'T = {xtext} s \n Amp = {ytext}'
        plt.xlabel("Period [s]", fontsize=12, labelpad=10)

    else:
        if plot_windows==True and HV.ndim != 1:
            for hv, c in zip(HV, colors):
                plt.semilogx(freq, hv, lw=0.5, zorder=10, c=c, **kwargs)

        stdev = np.std(freq[np.argmax(HV, axis=-1)])
        ax = plt.gca()
        # ax.add_patch(Rectangle(
        #                         xy=(freq[np.argmax(HV_mean)]-stdev, 0),
        #                         width=stdev,
        #                         height=np.max(HV.ravel())*1.1,
        #                         facecolor='#cccccc', 
        #                         linewidth=0, 
        #                         alpha=1, 
        #                         zorder=5
        #                     ),
        #             )
        # ax.add_patch(Rectangle(
        #                         xy=(freq[np.argmax(HV_mean)], 0),
        #                         width=stdev,
        #                         height=np.max(HV.ravel())*1.1,
        #                         facecolor='#999999', 
        #                         linewidth=0, 
        #                         alpha=1, 
        #                         zorder=5
        #                     ),
        #             )
        plt.semilogx(freq, HV_mean, color='k', lw=1.5, zorder=10, **kwargs)

        hvm_plus_std, hvm_minus_std = HV_mean+np.std(HV.astype(float), axis=0), HV_mean-np.std(HV.astype(float), axis=0)
        plt.semilogx(freq, hvm_plus_std, c='k', ls='--', zorder=10, **kwargs)
        plt.semilogx(freq, hvm_minus_std, c='k', ls='--', zorder=10, **kwargs)

        xtext = round(freq[maxval], 4)
        xtext_coord = 0.95
        plot_text = f'f = {xtext} Hz \n Amp = {ytext}'
        plt.xlabel("Frequency [Hz]", fontsize=12, labelpad=10)


    plt.text(x=xtext_coord, y=0.95, s=plot_text, bbox=dict(facecolor='white', edgecolor='black', pad=5.0), transform=plt.gca().transAxes, ha='right', va='top')

    plt.ylabel('H/V', fontsize=12, labelpad=10)
    plt.xlim(fmin, fmax)
    plt.ylim(0, np.max(hvm_plus_std)*1.105)
    plt.title(f'{nombre} - H/V', fontsize=15)
    plt.grid(ls='--', which='both', zorder=-10)
    plt.tick_params('both', labelsize=12)
    # plt.legend()

    # plt.savefig(f'{name[:-4]}-HV.png', dpi=400)
    # plt.show()

    fig = plt.gcf()
    return fig
