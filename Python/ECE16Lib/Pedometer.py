from ECE16Lib.CircularList import CircularList
import ECE16Lib.DSP as filt
import numpy as np
import scipy.signal as sig
from ECE16Lib.Communication import Communication
from time import sleep

"""
A class to enable a simple step counter
"""
class Pedometer:
  """
  Encapsulated class attributes (with default values)
  """
  __steps = 0        # the current step count
  __l1 = None        # CircularList containing L1-norm
  __filtered = None  # CircularList containing filtered signal
  __num_samples = 0  # The length of data maintained
  __new_samples = 0  # How many new samples exist to process
  __fs = 0           # Sampling rate in Hz
  __b = None         # Low-pass coefficients
  __a = None         # Low-pass coefficients
  __thresh_low = 25   # Threshold
  __thresh_high = 200 # Threshold
  __thresh_low_jj = 100
  __thresh_high_jj = 1000

  """
  Initialize the class instance
  """
  # FOUR MAIN METHODS IN THIS CLASS 

  def __init__(self, num_samples, fs, data=None):
    self.__steps = 0
    self.__num_samples = num_samples
    self.__fs = fs
    self.__l1 = CircularList(data, num_samples)
    self.__ax = CircularList(data, num_samples)
    self.__filtered = CircularList([], num_samples)
    self.__b, self.__a = filt.create_filter(3, 1, "lowpass", fs)

  """
  Add new samples to the data buffer
  Handles both integers and vectors!
  """
  def add(self, ax, ay, az):
    l1 = filt.l1_norm(ax, ay, az)
    if isinstance(ax, int):
      num_add = 1
    else:
      num_add = len(ax)
      l1 = l1.tolist()

    self.__l1.add(l1)
    self.__ax.add(ax)
    self.__new_samples += num_add

  """
  Process the new data to update step count
  """

  # WE USE PROCESS 1 and PROCESS 2 as two different methods
  # because we have two different ways of processing data for challenges 1 and 2
  # process_2() uses velocity and distance calculation used in ch 1

  def process_1(self):
    # Grab only the new samples into a NumPy array
    x = np.array(self.__l1[ -self.__new_samples: ])

    # Filter the signal (detrend, LP, MA, etc…)
    ma = np.zeros(x.size)
    win = 20
    for i in np.arange(0,len(x)):
      if(i < win): # use mean until filter is "on"
        ma[i] = np.mean(x[:i+1])
      else:
        ma[i] = ma[i-1] + (x[i] - x[i-win])/win

    dt = x - ma
    fs = 50
    bl, al = sig.butter(3, 1, btype="lowpass", fs=fs)
    x = sig.filtfilt(bl, al, dt,padlen=0)
    # Store the filtered data
    self.__filtered.add(x.tolist())

    # Count the number of peaks in the filtered data
    count_1, peaks = filt.count_peaks(x,self.__thresh_low_jj,self.__thresh_high_jj)

    # Update the step count and reset the new sample count
    self.__steps += count_1
    self.__new_samples = 0

    # Return the step count, peak locations, and filtered data
    return self.__steps, peaks, np.array(self.__filtered)

  def process_2(self):
    # Grab only the new samples into a NumPy array
    x = np.array(self.__l1[ -self.__new_samples: ])
    # Filter the signal (detrend, LP, MA, etc…)
    ma = np.zeros(x.size)
    win = 20
    for i in np.arange(0,len(x)):
      if(i < win): # use mean until filter is "on"
        ma[i] = np.mean(x[:i+1])
      else:
        ma[i] = ma[i-1] + (x[i] - x[i-win])/win

    dt = x - ma
    fs = 50
    bl, al = sig.butter(3, 1, btype="lowpass", fs=fs)
    x = sig.filtfilt(bl, al, dt, padlen=0)
    # Store the filtered data
    self.__filtered.add(x.tolist())

    # computing distance and velocity
    velocity = 0
    for p in range(0,len(x)-1):
      if (x[p] > self.__thresh_low or x[p] < -self.__thresh_low):
        if x[p] > 40:
          x[p] = 40
        if x[p+1] > 40:
          x[p+1] = 40
        velocity+=(0.5*(1/self.__fs)*x[p]*x[(p+1)])

    distance = velocity *(1/self.__fs)*self.__new_samples
    self.__new_samples = 0
    return distance

  def process_ped(self):
    # Grab only the new samples into a NumPy array
    x = np.array(self.__l1[ -self.__new_samples: ])

    # Filter the signal (detrend, LP, MA, etc…)
    ma = np.zeros(x.size)
    win = 20
    for i in np.arange(0,len(x)):
      if(i < win): # use mean until filter is "on"
        ma[i] = np.mean(x[:i+1])
      else:
        ma[i] = ma[i-1] + (x[i] - x[i-win])/win

    dt = x - ma
    fs = 50
    bl, al = sig.butter(3, 1, btype="lowpass", fs=fs)
    x = sig.filtfilt(bl, al, dt,padlen=0)
    # Store the filtered data
    self.__filtered.add(x.tolist())

    # Count the number of peaks in the filtered data
    count_1, peaks = filt.count_peaks(x,self.__thresh_low,self.__thresh_high)

    # Update the step count and reset the new sample count
    self.__steps += count_1
    self.__new_samples = 0

    # Return the step count, peak locations, and filtered data
    return self.__steps, peaks, np.array(self.__filtered)

  def process_jj(self):
    # Grab only the new samples into a NumPy array
    x = np.array(self.__l1[ -self.__new_samples: ])

    # Filter the signal (detrend, LP, MA, etc…)
    ma = np.zeros(x.size)
    win = 20
    for i in np.arange(0,len(x)):
      if(i < win): # use mean until filter is "on"
        ma[i] = np.mean(x[:i+1])
      else:
        ma[i] = ma[i-1] + (x[i] - x[i-win])/win

    dt = x - ma
    fs = 50
    bl, al = sig.butter(3, 1, btype="lowpass", fs=fs)
    x = sig.filtfilt(bl, al, dt,padlen=0)
    # Store the filtered data
    self.__filtered.add(x.tolist())

    # Count the number of peaks in the filtered data
    count_1, peaks = filt.count_peaks(x,self.__thresh_low_jj,self.__thresh_high_jj)

    # Update the step count and reset the new sample count
    self.__steps += count_1
    self.__new_samples = 0

    # Return the step count, peak locations, and filtered data
    return self.__steps, peaks, np.array(self.__filtered)

  """
  Clear the data buffers and step count
  """
  def reset(self):
    self.__steps = 0
    self.__l1.clear()
    self.__ax.clear()
    self.__filtered = np.zeros(self.__num_samples)

  """
  Other Methods (not significant, just added to help with challenges 1 and 2)
  """

  def setup_comm(self,serial_name = None,baud_rate = None):
    self.__comms = Communication("COM7",115200)
    self.__comms.clear()
    self.__comms.send_message("counting")

  def receive_message(self):
    return self.__comms.receive_message()
  
  def turn_off(self):
    self.__comms.send_message("sleep")
    self.__comms.close()

  def increment(self):
    self.__comms.send_message("increment")

  def countdown(self):
    self.__comms.send_message("countdown")

  def post_countdown(self):
    self.__comms.clear()
    self.__comms.send_message("wearable")

  def add_l1(self,l1):
    if isinstance(l1,int):
      num_add = 1
    else:
      num_add = len(l1)
      l1 = l1.tolist()

    self.__l1.add(l1)
    self.__new_samples += num_add