import numpy as np
import matplotlib.pyplot as plt
from hvseispy import seismic, plot_tools

# Se lee el archivo con datos de los 3 canales.
# `data` contiene 3 vectores con los datos de aceleración de cada canal
# ! IMPORTANTE: SpectraPy asume que los canales están en orden: [N, Z, E]

data = np.loadtxt(r'hvseispy\data\Sample data\CO5620170908044918_nve100.txt', unpack=True)

hvm, hv, freq = seismic.hvsr(acc_data=data,
							dt=0.01, # inverso de la tasa de muestreo
							win_len=81.92, # longitud de la ventana de analisis en segundos
							taper=['cosine', 0.15], # ventana de taper y porcentaje de aplicación (ver documentacion de la funcion para todas las ventanas aceptadas)
							smooth_bandwidth=40, # constante de la ventana de suavizamiento konno-ohmachi
							overlap=0, # traslape entre ventanas 
							fftmin=0.1, # frecuencia minima de calculo de la FFT
							fftmax=50, # frecuencia minima de calculo de la FFT (frecuencia de Nyquist o menor)
							hvmin=0.1, # frecuencia minima de calculo del espectro HV
							hvmax=50) # frecuencia minima de calculo del espectro HV (frecuencia de Nyquist o menor)

PlotTools.plot_hv(hvm, hv, freq,
				  fmin=0.1, # limite inferior de la grafica
				  fmax=50, # limite superior de la grafica
				  name='DM12', # nombre de la estacion o identificador del espectro
				  plot_windows=True, # dibujar o no todas las ventanas (si es False, solamente grafica la ventana promedio)
				  period_or_freq='freq' # graficar las curvas en eje de frecuencias o de periodos
				  ) 

plt.show()
