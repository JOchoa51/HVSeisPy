# matplotlib.use('Agg')
# plt.rcParams['figure.dpi'] = 400
# plt.rcParams['figure.figsize'] = [10,10]

import numpy as np
from scipy.signal import detrend
import warnings

from obspy import read


def read_sac(
        paths: str|list
        ):
    """Read MSEED files using the `read` function of ObsPy

    Args
    ----
        paths (list): List of routes of the files in order North, Vertical, East

    Returns
    -------
        list: A list of tuples with north, vertical and east signal components, one tuple per file
    """
    if isinstance(paths, list):
        Ds = []
        for path in paths:
            try:
                st = read(path)
            except FileNotFoundError:
                raise FileNotFoundError('File not found, check the path and try again')
                return

            D1 = detrend(np.array(st[0]) - np.mean(np.array(st[0])))
            Ds.append(D1)

        dimmin = np.min([len(arr) for arr in Ds])

        # Cut the signals to the smallest dimension found
        Ds_cut = [D[:dimmin] for D in Ds]
        return Ds_cut

    elif isinstance(paths, str):
        try:
            st = read(paths)
            if len(st) == 1:
                warnings.warn('Only one channel found, returning only one channel. H/V spectral ratio cannot be calculated\n')
        except FileNotFoundError:
            raise FileNotFoundError('File not found, check the path and try again')
            return

        D1 = detrend(np.array(st[0].data) - np.mean(np.array(st[0].data)))
        return D1



def read_mseed(name: str) -> tuple:
    """Read MSEED files using the `read` function of OpsPy

    Args
    ----
        name (str): Route of the file

    Returns
    -------
        tuple: A tuple of north, vertical and east components
    """
    

    try:
        st = read(name)
    except FileNotFoundError:
        raise FileNotFoundError('File not found, check the path and try again')

    # Access data for each channel
    e = st.select(channel="E")[0].data
    n = st.select(channel="N")[0].data
    z = st.select(channel="Z")[0].data

    N = detrend(n) - np.mean(n)
    Z = detrend(z) - np.mean(z)
    E = detrend(e) - np.mean(e)

    dimmin = np.min([len(N), len(Z), len(E)])

    # Cut the signals to the smallest dimension found
    N = N[:dimmin]
    Z = Z[:dimmin]
    E = E[:dimmin]

    return N, Z, E


def read_file(name: str, skiprows: int) -> tuple:
    """Read data from ASCII file, i.e. TXT files

    Args
    ----
        name (str): file path
        skiprows (float): rows to skip when reading, starting from 0.

    Returns
    -------
        tuple: A tuple of north, vertical and east components
    """
    try:
        N, V, E = np.loadtxt(name, skiprows=skiprows, unpack=True)
    except FileNotFoundError:
        raise FileNotFoundError('File not found, check the path and try again')

    N = detrend(np.array(N)) - np.mean(N)
    V = detrend(np.array(V)) - np.mean(V)
    E = detrend(np.array(E)) - np.mean(E)

    return N, V, E


def read_cires(name: str, header=False) -> tuple:
    # BUG: UnboundLocalError: cannot access local variable 'north' where it is not associated with a value
    """Function specifically designed to read data from accelerograms of CIRES

    Args
    ----
        name (str): Route of the file

    Returns
    -------
        tuple: A tuple of north, vertical and east components
    """
    warnings.warn('This function is an overly complex version of `read_file`, designed for a very specific file type. To make your life easier, please use `read_file` instead')
    try:
        # if header:
        with open(name, "r") as f:
            north = []
            vertical = []
            east = []
            header = []
            count = 0
            for line in f:
                count += 1
                if line.startswith('NOMBRE DE LA ESTACION'):
                    station_name = 'Station name: ' + line.split(":")[1]
                if line.startswith('CLAVE DE LA ESTACION'):
                    station_key = 'Station key: ' +  line.split(":")[1]
                    station_NamePlusKey = station_name + station_key
                    # print(station_NamePlusKey)
                # if 
                if line.startswith('HORA DE LA PRIMERA MUESTRA'):
                    initial_time = line.split(":")[1]
                    # print(initial_time)
                if count < 110:
                    header.append(line)
                    # Print header
                    # print(line.split("\n")[0])
                    # if line.split("\n")[0].startswith('NOMBRE DE LA ESTACION'):
                    #     print(line)
                else:
                    try:
                        north.append(float(line.split()[0]))
                        vertical.append(float(line.split()[1]))
                        east.append(float(line.split()[2]))
                    except ValueError:
                        s = line.split()[1].split("-")
                        if len(s) == 3:
                            vertical.append(-float(s[1]))
                            east.append(-float(s[2]))
                        elif len(s) == 2:
                            vertical.append(float(s[0]))
                            east.append(-float(s[1]))
    
        # else:
        #     header = None
        #     north, vertical, east = np.loadtxt(name, skiprows=109, unpack=True)

    except FileNotFoundError as fnf:
        raise FileNotFoundError('file not found')
    except ValueError as ve:
        raise ValueError('Error in the values')

    north = detrend(np.array(north))
    vertical = detrend(np.array(vertical))
    east = detrend(np.array(east))

    return north, vertical, east, header
