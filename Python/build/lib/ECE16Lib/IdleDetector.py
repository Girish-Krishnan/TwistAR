from ECE16Lib.Communication import Communication
from ECE16Lib.CircularList import CircularList
from matplotlib import pyplot as plt
import time
import numpy as np
from sys import exit

class IdleDetector():
    def __init__(self,num_samples,N,plot_1,plot_2):
        self.state = "initial"

        self.num_samples = num_samples               # 5 seconds of data @ 50Hz
        self.__refresh_time = 0.5              
        self.num_seconds = N
        self.__times = CircularList([], self.num_samples)
        self.__ax = CircularList([], self.num_samples)
        self.__ay = CircularList([], self.num_samples)
        self.__az = CircularList([], self.num_samples)
        self.__L1 = CircularList([], self.num_samples)
        self.__avg_L1 = CircularList([], self.num_samples)
        self.__average_x = CircularList([], self.num_samples)
        self.__delta_x = CircularList([], self.num_samples)
        self.__L2 = CircularList([], self.num_samples)
        self.__L_inf = CircularList([], self.num_samples)
        self.plot_1 = plot_1
        self.plot_2 = plot_2

    def __setup_comm(self):
        self.__comms = Communication("COM7", 115200)
        self.__comms.clear()                   # just in case any junk is in the pipes
        # self.__comms.send_message("loading")  # begin sending data

    def __plot(self):
          title_1 = ""
          var_1 = self.__L1
          title_2 = ""
          var_2 = self.__avg_L1
          if (self.plot_1 == "ax"):
              title_1 = "Acceleration, x-axis"
              var_1 = self.__ax
          elif (self.plot_1 == "ay"):
              title_1 = "Acceleration, y-axis"
              var_1 = self.__ay
          elif (self.plot_1 == "az"):
              title_1 = "Acceleration, z-axis"
              var_1 = self.__az
          elif (self.plot_1 == "L1"):
              title_1 = "L1-norm"
              var_1 = self.__L1
          elif (self.plot_1 == "avg_L1"):
              title_1 = "Average L1-norm"
              var_1 = self.__avg_L1
          elif (self.plot_1 == "L2"):
              title_1 = "L2-norm"
              var_1 = self.__L2
          elif (self.plot_1 == "avg_x"):
              title_1 = "Average Acceleration, x-axis"
              var_1 = self.__average_x
          elif (self.plot_1 == "delta_x"):
              title_1 = "Change in Acceleration, x-axis"
              var_1 = self.__delta_x
          elif (self.plot_1 == "L_inf"):
              title_1 = "L-infinity norm"
              var_1 = self.__L_inf
        
          if (self.plot_2 == "ax"):
              title_2 = "Acceleration, x-axis"
              var_2 = self.__ax
          elif (self.plot_2 == "ay"):
              title_2 = "Acceleration, y-axis"
              var_2 = self.__ay
          elif (self.plot_2 == "az"):
              title_2 = "Acceleration, z-axis"
              var_2 = self.__az
          elif (self.plot_2 == "L1"):
              title_2 = "L1-norm"
              var_2 = self.__L2
          elif (self.plot_2 == "avg_L1"):
              title_2 = "Average L1-norm"
              var_2 = self.__avg_L1
          elif (self.plot_2 == "L2"):
              title_2 = "L2-norm"
              var_2 = self.__L2
          elif (self.plot_2 == "avg_x"):
              title_2 = "Average Acceleration, x-axis"
              var_2 = self.__average_x
          elif (self.plot_2 == "delta_x"):
              title_2 = "Change in Acceleration, x-axis"
              var_2 = self.__delta_x
          elif (self.plot_2 == "L_inf"):
              title_2 = "L-infinity norm"
              var_2 = self.__L_inf

          plt.tight_layout()
          plt.subplot(211)
          plt.cla()
          plt.plot(var_1)
          plt.title(title_1)
          plt.subplot(212)
          plt.cla()
          plt.plot(var_2)
          plt.title(title_2)
          plt.show(block=False)
          plt.pause(0.001)

    def add_data(self,x1,x2,x3,x4,x5,x6):
        self.__times.add(int(x1))
        self.__ax.add(int(x2))
        self.__ay.add(int(x3))
        self.__az.add(int(x4))
        self.__L1.add(abs(int(x1))+abs(int(x2))+abs(int(x3)))
        self.__avg_L1.add(sum(self.__L1[(-self.num_seconds*50):])/len(self.__L1[(-self.num_seconds*50):]))
        self.__average_x.add(sum(self.__ax[(-self.num_seconds*50):])/len(self.__ax[(-self.num_seconds*50):]))
        self.__delta_x.add(self.__ax[-1]-self.__ax[-2])
        self.__L2.add(np.linalg.norm([self.__ax[-1],self.__ay[-1],self.__az[-1]]))
        self.__L_inf.add(max(self.__ax[-1],self.__ay[-1],self.__az[-1]))

    def L1(self):
        return self.__L1[-1], self.__avg_L1[-1]

    def main(self):
        self.__setup_comm()
        try:
            prev_active = 0
            prev_active_state = 1
            inactive_start = 0
            start_active = time.time()
            # self.__comms.send_message("initial")
            while(True):
                message = self.__comms.receive_message()
                if(message != None):
                    try:
                        (m1, m2, m3, m4, m5, m6) = message.split(',')
                    except ValueError:        # if corrupted data, skip the sample
                        continue

                   # add the new values to the circular lists
                    self.__times.add(int(m1))
                    self.__ax.add(int(m2))
                    self.__ay.add(int(m3))
                    self.__az.add(int(m4))
                    self.__L1.add(abs(self.__ax[-1])+abs(self.__ay[-1])+abs(self.__az[-1]))
                    self.__avg_L1.add(sum(self.__L1[(-self.num_seconds*50):])/len(self.__L1[(-self.num_seconds*50):]))
                    self.__average_x.add(sum(self.__ax[(-self.num_seconds*50):])/len(self.__ax[(-self.num_seconds*50):]))
                    self.__delta_x.add(self.__ax[-1]-self.__ax[-2])
                    self.__L2.add(np.linalg.norm([self.__ax[-1],self.__ay[-1],self.__az[-1]]))
                    self.__L_inf.add(max(self.__ax[-1],self.__ay[-1],self.__az[-1]))

                current_time_idle = time.time()
                if (current_time_idle - prev_active > self.__refresh_time):
                    prev_active = current_time_idle

                    # plot two variables:
                    # self.__plot()

                    if(abs(self.__L1[-1] - self.__avg_L1[-1]) > 100):
                        if (prev_active_state == 1) and (self.__L1[-1] > 1000):
                            start_active = time.time()
                        prev_active_state = 0
                    else:
                        if prev_active_state == 0:
                            if (time.time() - start_active >= 1):
                                #print("Active for 1+ seconds")
                                self.__comms.send_message("active")
                            inactive_start = time.time()
                        elif (inactive_start != 0):
                            if (time.time() - inactive_start >= 5):
                                #print("Inactive for 5+ seconds")
                                self.__comms.send_message("inactive")
                        prev_active_state = 1

        except(Exception, KeyboardInterrupt) as e:
            print(e)                     # Exiting the program due to exception
        finally:
            self.__comms.send_message("sleep")  # stop sending data
            self.__comms.close()
            exit()
