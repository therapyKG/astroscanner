import io, tifffile
#from astropy.io import fits
import numpy as np

#input: binary buffer generated by camera api
#output: extracted RGB layers as a 3d ndarray
def process_raw(buffer):
    #open raw file and load raw pixel value into rawdata
    #rawdata = np.asarray(buffer, 'uint16').reshape((2084, 3112))
    #print("BINNED SHAPE: " + str(buffer.shape))
    rawdata = buffer.reshape(2084,3112)

    red_channel = rawdata[1::2, 1::2]

    g_0 = rawdata[0::2, 1::2]
    g_1 = rawdata[1::2, 0::2]
    green_channel = np.mean(np.array([g_0, g_1]), axis=0).astype('uint16')

    blue_channel = rawdata[0::2, 0::2]

    return np.asarray([red_channel, green_channel, blue_channel]).transpose(1,2,0)

#perform 2-binning on 3d rgb array for further SNR improvements
def bin(rgb_array):
    new_shape=[(int)(rgb_array.shape[1]/2), 2, (int)(rgb_array.shape[2]/2), 2]
    return np.asarray([rgb_array[i].reshape(new_shape).mean(-1).mean(1) for i in range(3)])

def process_raw_binning(buffer):
    rawdata = np.asarray(buffer, 'uint32')
    new_shape=[(int)(rawdata.shape[0]/4), 2, (int)(rawdata.shape[1]/4), 2]

    red_channel = rawdata[1::2, 1::2].reshape(new_shape).mean(-1).mean(1)

    g_0 = rawdata[0::2, 1::2]
    g_1 = rawdata[1::2, 0::2]
    green_channel = np.mean(np.array([g_0, g_1]), axis=0).reshape(new_shape).mean(-1).mean(1)

    blue_channel = rawdata[0::2, 0::2].reshape(new_shape).mean(-1).mean(1)

    return np.asarray([red_channel, green_channel, blue_channel]).transpose(1,2,0)

def process_low_res(buffer):
    pass

if __name__ == '__main__':
    buf = io.open("pins.fit", "rb")
    img = process_raw_binning(buf)
    print(img.shape)
    #tifffile.imwrite('rpi/pins.tif', img.astype('uint16'), photometric='rgb')