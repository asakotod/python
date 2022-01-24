# -*- coding: utf-8 -*-

'''
 SweepSineData.py
 
 sweep frequency from 10k to 40k of sine wave.
 keep on writing in to csv file.
 file size is limited to 500 lines

 Data format: 

    [MSB] Q1(4x),I1(4x),Q0(4x),I0(4x) [LSB]
'''

#temp file generated in your local
fout='./output.txt'

import numpy as np   
import time

fstart=10*1E3 #E3 kHz
fstep=10*1E3
fend=40*1E3 #E3 kHz
amp1=1
#BUFFERDEPTH=100
PACKETSIZE=64
DATASIZE=16
DATASIZE_hex=int(DATASIZE/4)
VMAX=3
AMPCONVRATE= 21845#(digital data FS)/(amp FS[V]) e.g (2^16-1)/3V=65535/3=21845
Fs=1E6 #sampling freq 
tstep=1/Fs # step size
fd1=fstart #[kHz]
amp1=1

MAXFILELINES = 200
BUFSIZE=200

'''create binary number of n with length specified as bits '''
def bindigits(n, bits):
#    s = bin(n & int("1"*bits, 2))[2:]
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

def putFIFO(fifo,i0,i1,q0,q1,DATASIZE,fifodepth):
    if len(fifo) >= fifodepth:
        fifo=fifo[1:]
        # fifo=tmp
        
    fifo.append(decToHex(round(q1),DATASIZE) + decToHex(round(i1),DATASIZE) +decToHex(round(q0),DATASIZE) + decToHex(round(i0),DATASIZE))
    return fifo

if __name__ == '__main__':

               
    dout=[]
 
    tt=0
    while True:
        with open(fout,"w") as fo:
            
            i0=AMPCONVRATE*amp1*np.sin(2*np.pi*fd1*tt)
            i1=AMPCONVRATE*amp1*np.sin(2*np.pi*fd1*(tt+tstep))
            q0=AMPCONVRATE*amp1*np.cos(2*np.pi*fd1*tt)
            q1=AMPCONVRATE*amp1*np.cos(2*np.pi*fd1*(tt+tstep))
 
            dout=putFIFO(dout,i0,i1,q0,q1,DATASIZE,MAXFILELINES)
             
            for line in dout:        
                fo.writelines(line+"\n") 
            
            tt = tt + tstep*2
            if int((tt/(tstep*2))) % BUFSIZE ==0: 
                if (fd1==fend):
                    fd1=fstart
                    print(f"reset to {fd1}Hz")

                else:
                    fd1=fd1+fstep
                    print(f"{fd1}Hz")
                    
        time.sleep(0.02)
        
    #     i0=AMPCONVRATE*amp1*np.sin(2*np.pi*fd1*tt)
    #     i1=AMPCONVRATE*amp1*np.sin(2*np.pi*fd1*(tt+tstep))
    #     q0=AMPCONVRATE*amp1*np.cos(2*np.pi*fd1*tt)
    #     q1=AMPCONVRATE*amp1*np.cos(2*np.pi*fd1*(tt+tstep))
    
    #     dout.append(decToHex(round(q1),DATASIZE) + decToHex(round(i1),DATASIZE) +decToHex(round(q0),DATASIZE) + decToHex(round(i0),DATASIZE))
         
    
    #     for line in dout:        
    #         fo.writelines(line+"\n")  
        
    #     tt = tt + tstep*2
        
  
