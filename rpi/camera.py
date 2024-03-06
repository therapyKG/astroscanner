import toupcam, io, tifffile, rawdev
import numpy as np

CAM_NOT_FOUND = 1
CAM_INIT_FAILED = 2
CAM_OPEN_FAILED = 3

class Cam:
    def __init__(self):
        self.hcam = None
        self.buf = None
        self.rawbuf = None
        self.total = 0
        self.flag_do_capture = 0

# the vast majority of callbacks come from toupcam.dll/so/dylib internal threads
    @staticmethod
    def cameraCallback(nEvent, ctx):
        if nEvent == toupcam.TOUPCAM_EVENT_IMAGE:
            ctx.CameraCallback(nEvent)

    def CameraCallback(self, nEvent):

        if nEvent == toupcam.TOUPCAM_EVENT_IMAGE and self.flag_do_capture == 1:
            try:
                #self.hcam.PullImageV3(self.buf, 0, 24, 0, None)
                self.hcam.PullImageV3(self.rawbuf, 0, 48, 0, None)
                rawdata = np.frombuffer(self.rawbuf, dtype='uint16').reshape((4168, 6224))
                binned_img = rawdev.process_raw_binning(rawdata)
                self.total += 1
                self.flag_do_capture = 0
                print('pull RAW ok, total = {}'.format(self.total))
                #print(rawdata)

                #img = rawdev.process_raw_binning(io.BytesIO(self.rawbuf))
                tifffile.imwrite("rpi/raw_binned.tif", binned_img.astype('uint16'), photometric='rgb')

            except toupcam.HRESULTException as ex:
                print('pull image failed, hr=0x{:x}'.format(ex.hr & 0xffffffff))
        else:
            #dump unused frames into buffer
            self.hcam.PullImageV3(self.buf, 0, 48, 0, None)
            print('dumped buffer, event callback: {}'.format(nEvent))

    def run(self):
        a = toupcam.Toupcam.EnumV2()
        if len(a) > 0:
            print('{}: flag = {:#x}, preview = {}, still = {}'.format(a[0].displayname, a[0].model.flag, a[0].model.preview, a[0].model.still))
            for r in a[0].model.res:
                print('\t = [{} x {}]'.format(r.width, r.height))
            self.hcam = toupcam.Toupcam.Open(a[0].id)
            print('high-fullwell ={:x}'.format(a[0].model.flag & toupcam.TOUPCAM_FLAG_HIGH_FULLWELL))
            print('raw bit size ={:x}'.format(a[0].model.flag & toupcam.TOUPCAM_FLAG_RAW16))
            if self.hcam:
                try:
                    width, height = self.hcam.get_Size()
                    bufsize = (width * 2) * height
                    rawbufsize = (width * 2) * height
                    print('image size: {} x {}, bufsize = {}'.format(width, height, rawbufsize))
                    self.buf = bytes(bufsize)
                    self.rawbuf = bytes(rawbufsize)
                    try:
                        self.hcam.put_Option(toupcam.TOUPCAM_OPTION_RAW, 1)

                        self.hcam.put_Option(toupcam.TOUPCAM_OPTION_PIXEL_FORMAT, toupcam.TOUPCAM_PIXELFORMAT_RAW16)
                        print("raw option = ", self.hcam.get_Option(toupcam.TOUPCAM_OPTION_PIXEL_FORMAT))

                        fanspeed = self.hcam.FanMaxSpeed()
                        toupcam.Toupcam.put_Option(self.hcam, toupcam.TOUPCAM_OPTION_FAN, fanspeed)

                        toupcam.Toupcam.put_Option(self.hcam, toupcam.TOUPCAM_OPTION_TEC, 1)
                        toupcam.Toupcam.put_Option(self.hcam, toupcam.TOUPCAM_OPTION_TECTARGET, 50)

                        toupcam.Toupcam.put_Option(self.hcam, toupcam.TOUPCAM_OPTION_HIGH_FULLWELL, 1)
                        toupcam.Toupcam.put_Option(self.hcam, toupcam.TOUPCAM_OPTION_LOW_NOISE, 1)

                    except toupcam.HRESULTException as e:
                        print('init failed, err=0x{:x}'.format(e.hr & 0xffffffff))
                    #print('max fan speed = {:x}'.format(fanspeed & 0xffffffff))
                    #input('press ENTER to continue.' )

                    if self.rawbuf:
                        try:
                            self.flag_do_capture = 1
                            #TODO: add wait for sensor to cool
                            self.hcam.StartPullModeWithCallback(self.cameraCallback, self)
                        except toupcam.HRESULTException as ex:
                            print('failed to start camera, hr=0x{:x}'.format(ex.hr & 0xffffffff))
                    #input('press ENTER to exit')

                except toupcam.HRESULTException as er:
                    print('failed and closed, err=0x{:x}'.format(er.hr & 0xffffffff))
                    self.hcam.Close()
                    self.hcam = None
                    self.buf = None

                print("####REACHED!#####")

                input('press ENTER to exit')

                self.hcam.Close()
                self.hcam = None
                self.buf = None
            else:
                print('failed to open camera')
        else:
            print('no camera found')

if __name__ == '__main__':
    app = Cam()
    app.run()