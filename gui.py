# -*- coding: utf-8 -*-
"""

Data: hex signed data with 2's complement 

Data format: 

    [MSB] Q1(4x),I1(4x),Q0(4x),I0(4x) [LSB]

@author: asakotod

"""

#temp file generated in your local
fout='./output.txt'


# importing various libraries
import sys


from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import numpy as np   
from matplotlib.animation import FuncAnimation
from matplotlib.animation import TimedAnimation
import matplotlib.animation as animation

"""
Parameters to be tuned
"""
BUFFERDEPTH=100
PACKETSIZE=64
DATASIZE=16
DATASIZE_hex=int(DATASIZE/4)
VMAX=3
AMPCONVRATE= 21845#(digital data FS)/(amp FS[V]) e.g (2^16-1)/3V=65535/3=21845
Fs=1E6 #sampling freq 
tstep=1/Fs # step size
t=np.linspace(0,(BUFFERDEPTH*2)*tstep,BUFFERDEPTH*2)


''' convert 2's complement hex to dec '''
def twos_complement(hexstr,bits):
    value = int(hexstr,16)
    if value & (1 << (bits-1)):
        value -= 1 << bits
    return value

'''create binary number of n with length specified as bits '''
def bindigits(n, bits):
    s = bin(n & int("1"*bits, 2))[2:]
    return ("{0:0>%s}" % (bits)).format(s)

'''convert dec to hex signed as 2's compliment ''' 
def decToHex(number,bits):
    
    if number > 0 :
        bin_number = bindigits(number,bits)
    else:
        bin_number = bindigits((~abs(number) + 1),bits)
        
    hex_number = "{:04X}".format(int(bin_number,2))
    # print(int(hex_number,16))
    return hex_number


class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'CHIPS Phase2'
        self.left = 100
        self.top = 100
        self.width = 800
        self.height = 800
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        self.table_widget = MyTableWidget(self)
        self.setCentralWidget(self.table_widget)
        
        self.show()


class MyTableWidget(QWidget):
# class Window(QWidget):
    
    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)

        self.layout = QVBoxLayout(self)
        
        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tab1 = ReadTab()
        self.tab2 = WriteTab()
        self.tabs.resize(600,700)
        
        # Add tabs
        self.tabs.addTab(self.tab1,"Read Data")
        self.tabs.addTab(self.tab2,"Load Data")
           
        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        
        self.setGeometry(100, 100, 600, 700) # x,y,w,h
        self.setWindowTitle('DARPA CHIPS Phase2')
        self.resize(self.minimumSizeHint());

class WriteTab(QWidget):
       
    # constructor
    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)

        self.figure = plt.figure(figsize=(5,10),dpi=70)
        self.canvas = FigureCanvas(self.figure)

 
        rampButton = QPushButton("Ramp")
        sinButton  = QPushButton("Sine")
        sinButton.clicked.connect(self.plotSine)
        rampButton.clicked.connect(self.plotRamp)
        
        self.sinFreqVal=QLineEdit()
#        self.sinFreqVal.setAlignment(Qt.AlignRight)
        self.sinFreqVal.setText("1000")
        
        self.sinAmpVal=QLineEdit()
        self.sinAmpVal.setText("1")

        self.rampRateVal=QLineEdit()
        self.rampRateVal.setText("100000")

        self.rampMaxVal=QLineEdit()
        self.rampMaxVal.setText("1")


        self.formLayout1=QFormLayout()
        self.formLayout1.addRow(QLabel("freq[kHz](<{maxf:.1f}MHz):".format(maxf=Fs/2*1E-6)), self.sinFreqVal)
        self.formLayout2=QFormLayout()
        self.formLayout2.addRow(QLabel("Amplitude[V](<{max2:.1f}V):".format(max2=VMAX/2)), self.sinAmpVal)
        self.formLayout3=QFormLayout()
        self.formLayout3.addRow(QLabel("Ramp Rate[V/sec]:"), self.rampRateVal)
        self.formLayout4=QFormLayout()
        self.formLayout4.addRow(QLabel("Max[V](<{max:.1f}V):".format(max=VMAX)), self.rampMaxVal)

        self.hbox1 = QHBoxLayout()
        self.hbox1.addLayout(self.formLayout1)
        self.hbox1.addLayout(self.formLayout2)

        self.hbox2 = QHBoxLayout()
        self.hbox2.addLayout(self.formLayout3)
        self.hbox2.addLayout(self.formLayout4)

        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addStretch()
        vbox.addWidget(sinButton)
        vbox.addLayout(self.hbox1)
        vbox.addWidget(rampButton)
        vbox.addLayout(self.hbox2)

        self.setLayout(vbox)

    def writeIQdata(self,yi,yq):

        i0=AMPCONVRATE*yi[0:BUFFERDEPTH*2:2]
        i1=AMPCONVRATE*yi[1:BUFFERDEPTH*2:2]
        q0=AMPCONVRATE*yq[0:BUFFERDEPTH*2:2]
        q1=AMPCONVRATE*yq[1:BUFFERDEPTH*2:2]
                
        dout=[]
        
        for i in range(BUFFERDEPTH):
            dout.append(decToHex(round(q1[i]),DATASIZE) + decToHex(round(i1[i]),DATASIZE) +decToHex(round(q0[i]),DATASIZE) + decToHex(round(i0[i]),DATASIZE))
            # dout.append('{0:04x}'.format(round(q1[i])) + '{0:04x}'.format(round(i1[i])) +'{0:04x}'.format(round(q0[i])) + '{0:04x}'.format(round(i0[i])))
 
        with open(fout,"w") as fo:
            for line in dout:        
                fo.writelines(line+"\n")    
        
        #close once
        fo.close()

    def plotIQdata(self,yi,yq):

        self.figure.clear()
        ax=self.figure.add_subplot(111)
        ax.cla()
        ax.plot(t*1E3,yi,'-*',t*1E3,yq,'--')  
        ax.set_title('Data to Load',fontweight='bold')
        ax.set_xlabel("time (ms)")
        
        # refresh canvas
        self.canvas.draw()
        
    def plotSine(self):
            
        fd1=float(self.sinFreqVal.text())*1E3 #[kHz]
        amp1=float(self.sinAmpVal.text())
         
        yi=amp1*np.sin(2*np.pi*fd1*t)
        yq=amp1*np.cos(2*np.pi*fd1*t)
        
        self.writeIQdata(yi,yq)
        self.plotIQdata(yi,yq)

    def plotRamp(self):
        minVal=twos_complement('8000', DATASIZE)/AMPCONVRATE
        rRate1=float(self.rampRateVal.text())
        rMax1=float(self.rampMaxVal.text())       
        yy=rRate1*t+minVal
        tadj=0

        for x in range(len(t)) :
            if rRate1*(t[x]-tadj)>rMax1:
                yy[x]=minVal
                tadj=t[x]
            else:
                yy[x]=rRate1*(t[x]-tadj)+minVal

        self.writeIQdata(yy,yy)
        self.plotIQdata(yy,yy)
        
class ReadTab(QWidget):
       
    # constructor
    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)

        animButton = QPushButton("Start/Stop reading output.txt")
        animButton.clicked.connect(self.anim_startstop)

        recordButton = QPushButton("Video record to output.gif")
        recordButton.clicked.connect(self.anim_save)


        # a figure instance to plot on
        self.figure = plt.figure(figsize=(5,5),dpi=70)
        self.canvas = FigureCanvas(self.figure)
        
       
        self.ax1=self.figure.add_subplot(221)
        self.ax2=self.figure.add_subplot(223)
        self.ax3=self.figure.add_subplot(224)
        self.ax4=self.figure.add_subplot(222)

        self.toolbar = NavigationToolbar(self.canvas, self)
        vbox = QVBoxLayout()
        vbox.addWidget(self.toolbar)
        vbox.addWidget(self.canvas)
        vbox.addWidget(animButton) # '1' is size of button
        vbox.addWidget(recordButton) # '1' is size of button

        self.setLayout(vbox)

        self.anim_running=True        
        self.anim = FuncAnimation(self.figure,self.animate_loop,frames=40,interval=100,repeat=True,blit=False)
        self.figure.tight_layout()        
        self.canvas.draw()
        

    def anim_save(self):
        writergif = animation.PillowWriter(fps=30)
        self.anim.save('output.gif',writer=writergif)       
        
    def anim_startstop(self):
        if self.anim_running: 
            self.anim.event_source.stop()
            self.anim_running=False

        else:
            self.anim.event_source.start()
            self.anim_running=True

    # Tran, real/imag FFT, IQ
    def plot1(self,t,yi,yq):
        
        Xi=np.fft.fft(yi)
        Xq=np.fft.fft(yq)
        N=len(Xi)
        f=np.fft.fftfreq(len(yi))*Fs
        f_plot=f/1E3 #[kHz]
        
        # plot data
        self.ax1.cla()
        self.ax1.plot(t,yi,'--',label='I')
        self.ax1.plot(t,yq,'-',label='Q')
        self.ax1.legend(loc='upper right')
        self.ax1.set_title('Transient',fontweight='bold')
        self.ax1.set_xlabel("time (s)")

        self.ax2.cla()
        self.ax2.stem(f_plot,Xi.real/N,'b',markerfmt=" ", basefmt='-b',label='real') 
        self.ax2.stem(f_plot,Xi.imag/N,'r',markerfmt=" ", basefmt='r',label='imag')  
        self.ax2.set_title('I-FFT',fontweight='bold')
        self.ax2.legend()
        self.ax2.set_xlabel("freq (KHz)")
        self.ax2.set_xlim([-50,50])

        self.ax3.cla()
        self.ax3.stem(f_plot,Xq.real/N,'b',markerfmt=" ", basefmt='-b',label='real') 
        self.ax3.stem(f_plot,Xq.imag/N,'r',markerfmt=" ", basefmt='r',label='imag')  
        self.ax3.set_title('Q-FFT',fontweight='bold')
        self.ax3.set_xlabel("time (s)")
        self.ax3.legend()
        self.ax3.set_xlabel("freq (KHz)")
        self.ax3.set_xlim([-50,50])

        self.ax4.cla()
        self.ax4.plot(yi,yq,'o')  
        self.ax4.set_title('IQ',fontweight='bold')
        self.ax4.set_xlabel("In-Phase")
        self.ax4.set_ylabel("Quad-Phase")
    

        self.figure.tight_layout()        
        self.canvas.draw()
    
    # Tran, abs FFT, IQ
    def plot2(self,t,yi,yq):

        Xi=np.fft.fft(yi)
        Xq=np.fft.fft(yq)
        N=len(Xi)
        f=np.fft.fftfreq(len(yi))*Fs
        f_plot=f/1E3 #[kHz]        
        
        self.ax1.cla()
        self.ax1.plot(t*1E6,yi,'--',label='I')
        self.ax1.plot(t*1E6,yq,'-',label='Q')
        self.ax1.legend(loc='upper right')
        self.ax1.set_title('Transient',fontweight='bold')
        self.ax1.set_xlabel("time (us)")
    
        self.ax2.cla()
        self.ax2.stem(f_plot,np.abs(Xi)/N,'r',markerfmt=" ", basefmt='r')  
        self.ax2.set_title('I-FFT',fontweight='bold')
        self.ax2.set_xlabel("freq (KHz)")
        self.ax2.set_xlim([-50,50])
        self.ax2.set_ylim([0,1])
   
        self.ax3.cla()
        self.ax3.stem(f_plot,np.abs(Xq)/N,'b',markerfmt=" ", basefmt='-b') 
        self.ax3.set_title('Q-FFT',fontweight='bold')
        self.ax3.set_xlabel("time (s)")
        self.ax3.set_xlabel("freq (KHz)")
        self.ax3.set_xlim([-50,50])
        self.ax3.set_ylim([0,1])
        
        self.ax4.cla()
        self.ax4.plot(yi,yq,'o')  
        self.ax4.set_title('IQ',fontweight='bold')
        self.ax4.set_xlabel("In-Phase")
        self.ax4.set_ylabel("Quad-Phase")
        
        self.figure.tight_layout()        
        self.canvas.draw()
           
    def reset(self):
        # self.figure.clear()

        yi2=[]
        yq2=[]
#        t=np.linspace(0,(BUFFERDEPTH*2)*tstep,BUFFERDEPTH*2)
                
        with open(fout,"r") as fi:
           din=[line.strip() for line in fi]
    
        fi.close()
       
        #print(din)
        for i in range(BUFFERDEPTH):
            yq2.append(twos_complement(din[i][DATASIZE_hex*2:DATASIZE_hex*3],16)/AMPCONVRATE)#q0
            yq2.append(twos_complement(din[i][:DATASIZE_hex],16)/AMPCONVRATE) #q1
            yi2.append(twos_complement(din[i][DATASIZE_hex*3:DATASIZE_hex*4],16)/AMPCONVRATE) #i0
            yi2.append(twos_complement(din[i][DATASIZE_hex:DATASIZE_hex*2],16)/AMPCONVRATE)#i1  
            
        self.plot2(t,yi2,yq2)       
        

    def animate(self):

        # self.figure.tight_layout()   
        self.anim = FuncAnimation(self.figure,self.animate_loop,frames=100,interval=100,repeat=True,blit=False)
        self.canvas.draw()

        # ani=FuncAnimation(plt.gcf(), animate, interval=10)

        # plt.tight_layout()
        # plt.show()
    def animate_loop(self,i):

        yi=[]
        yq=[]
        Xi=[]
        Xq=[]
        idx_start=0
        # print(f"{i}")
        with open(fout,"r") as fi:
           din=[line.strip() for line in fi]
        if len(din)>0: 
            for i in range(len(din)):
                yq.append(twos_complement(din[i][DATASIZE_hex*2:DATASIZE_hex*3],16)/AMPCONVRATE)#q0
                yq.append(twos_complement(din[i][:DATASIZE_hex],16)/AMPCONVRATE) #q1
                yi.append(twos_complement(din[i][DATASIZE_hex*3:DATASIZE_hex*4],16)/AMPCONVRATE) #i0
                yi.append(twos_complement(din[i][DATASIZE_hex:DATASIZE_hex*2],16)/AMPCONVRATE)#i1  
    
            if len(din)<BUFFERDEPTH: idx_start=0
            else: idx_start=(len(din)-BUFFERDEPTH)*2
                
            yi=yi[idx_start:len(din)*2:1]
            yq=yq[idx_start:len(din)*2:1]
            
            t=np.linspace(0,len(yi)*tstep,len(yi))
            self.plot2(t, yi, yq)
#        return

        
if __name__ == '__main__':

    app = QApplication(sys.argv)
    main=App()    
    sys.exit(app.exec_())
