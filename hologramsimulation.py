import numpy as np
from numpy.fft import fft2, fftshift, ifftshift, ifft2
import tifffile
import pandas as pd
import math 
from numpy import newaxis
import scipy.misc
import random
pi=math.pi
i=complex(0,1)

trainings=pd.DataFrame()
wavelength=0.5
numPixels = 512#512
gtRadius  = 50#50 # ground truth radius, pixels
gtPhase   = 0.75 # radians
gtCenter  = numPixels / 2 # assumes numPixels is even
W, H      = np.meshgrid(np.arange(0, numPixels), np.arange(0, numPixels)) # coordinates of the array indexes
pixelSize = 0.1 # microns
x = np.linspace(-pixelSize * numPixels / 2, pixelSize * numPixels / 2, num = numPixels, endpoint = True)
physicalRadius = gtRadius * pixelSize
dx = x[1] - x[0]    # Sampling period, microns
fS = 1 / dx         # Spatial sampling frequency, inverse microns
df = fS / numPixels # Spacing between discrete frequency coordinates, inverse microns
fx = np.arange(-fS / 2, fS / 2, step = df) # Spatial frequency, inverse microns
FX, FY = np.meshgrid(fx, fx)
numberofsteps=5
#distance = np.linspace(9,15,num=numberofsteps)
distance=np.linspace(9,15,num=numberofsteps)
folder="/home/lindsey/Desktop/test/"
particle_pose=0
particle_truncated=0
particle_difficult=0
samplenumber=3
frame=10
stacks=np.empty((frame,numPixels,numPixels))

def H2(fx, fy, z, wavelength=0.5):
    square_root = np.sqrt(np.abs(1 - (wavelength**2 * fx**2) - (wavelength**2 * fy**2)))
    temp = np.exp(1j * 2 * np.pi * z / wavelength * square_root)
    temp[np.isnan(temp)] = 0 # replace nan's with zeros
    return temp

for d in range(frame):
    Hologram=np.zeros((numPixels,numPixels))
    filename='{}.png'.format(d)
    my_file=open("/home/lindsey/Desktop/testing/testeannotations/{}.xml".format(d),"w+")
    my_file.write("<annotation>\n\t<folder>{}</folder>\n\t<filename>{}</filename>\n\t<size>\n\t\t<width>{}</width>\n\t\t<height>{}</height>\n\t\t<depth>{}</depth>\n\t</size>\n\t<segmented>0</segmented>".format(folder,filename, numPixels, numPixels, 0))
    for f in range(samplenumber):     
        randomdistance=random.choice(distance)
        print(randomdistance)
        xCenter=np.random.randint(1.5*gtRadius,numPixels-1.5*gtRadius)
        yCenter=np.random.randint(1.5*gtRadius,numPixels-1.5*gtRadius)
        gtMask = np.sqrt((W - xCenter)**2 + (H - yCenter)**2) <= gtRadius
        gt = np.ones((numPixels, numPixels), dtype=np.complex)
        gt[gtMask] = np.exp(1j * gtPhase)
        GT = ifftshift(fft2(fftshift(gt))) * dx**2
        gt_prime = fftshift(ifft2(ifftshift(GT * H2(FX, FY, randomdistance)))) / dx**2
        hologram = np.abs(gt_prime)**2
#        tifffile.imshow(hologram,cmap='gray')
        xmin=max(xCenter-80,0)
        xmax=min(xCenter+80,512)
        ymin=max(yCenter-80,0)
        ymax=min(yCenter+80,512)
        training=pd.DataFrame( {'frame':[d],'realdepth':randomdistance,'xCenter':[xCenter],'yCenter':[yCenter]} )
        trainings=trainings.append(training,ignore_index=True)
        my_file.write("\n\t<object>\n\t\t<name>{}</name>\n\t\t<pose>{}</pose>\n\t\t<truncated>{}</truncated>\n\t\t<difficult>{}</difficult>\n\t\t<bndbox>\n\t\t\t<xmin>{}</xmin>\n\t\t\t<ymin>{}</ymin>\n\t\t\t<xmax>{}</xmax>\n\t\t\t<ymax>{}</ymax>\n\t\t</bndbox>\n\t</object>".format(randomdistance, particle_pose, particle_truncated, particle_difficult, xmin, ymin, xmax, ymax))
        Hologram=hologram+Hologram
    my_file.write("\n</annotation>")
    my_file.close()
    scipy.misc.imsave('/home/lindsey/Desktop/testing/testimages/{}.png'.format(d),Hologram)
