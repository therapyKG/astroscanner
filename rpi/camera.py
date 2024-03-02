import toupcam

CAM_NOT_FOUND = 1
CAM_INIT_FAILED = 2
CAM_OPEN_FAILED = 3

class Cam:
    def __init__(self):
        self.hcam = None
        self.buf = None
        self.total = 0
        self.flag_next_frame = 0

# the vast majority of callbacks come from toupcam.dll/so/dylib internal threads
    @staticmethod
    def cameraCallback(nEvent, ctx):
        if nEvent == toupcam.TOUPCAM_EVENT_IMAGE:
            ctx.CameraCallback(nEvent)

    def CameraCallback(self, nEvent):
        if nEvent == toupcam.TOUPCAM_EVENT_IMAGE:
            try:
                self.hcam.PullImageV3(self.buf, 0, 24, 0, None)
                self.flag_next_frame = 1
                self.total += 1
                print('pull image ok, total = {}'.format(self.total))
            except toupcam.HRESULTException as ex:
                print('pull image failed, hr=0x{:x}'.format(ex.hr & 0xffffffff))
        else:
            print('event callback: {}'.format(nEvent))

    def run(self):
        a = toupcam.Toupcam.EnumV2()
        if len(a) > 0:
            print('{}: flag = {:#x}, preview = {}, still = {}'.format(a[0].displayname, a[0].model.flag, a[0].model.preview, a[0].model.still))
            for r in a[0].model.res:
                print('\t = [{} x {}]'.format(r.width, r.height))
            self.hcam = toupcam.Toupcam.Open(a[0].id)
            print('high-fullwell={:x}'.format(a[0].model.flag & toupcam.TOUPCAM_FLAG_HIGH_FULLWELL))
            if self.hcam:
                try:
                    width, height = self.hcam.get_Size()
                    bufsize = toupcam.TDIBWIDTHBYTES(width * 24) * height
                    print('image size: {} x {}, bufsize = {}'.format(width, height, bufsize))
                    self.buf = bytes(bufsize)

                    try:
                        #toupcam.Toupcam.put_Option(self.hcam, toupcam.TOUPCAM_OPTION_RAW, 1)
                        fanspeed = self.hcam.FanMaxSpeed()
                        toupcam.Toupcam.put_Option(self.hcam, toupcam.TOUPCAM_OPTION_FAN, fanspeed)
                        toupcam.Toupcam.put_Option(self.hcam, toupcam.TOUPCAM_OPTION_TEC, 1)
                        toupcam.Toupcam.put_Option(self.hcam, toupcam.TOUPCAM_OPTION_TECTARGET, 50)

                        toupcam.Toupcam.put_Option(self.hcam, toupcam.TOUPCAM_OPTION_HIGH_FULLWELL, 1)

                    except toupcam.HRESULTException as e:
                        print('init failed, err=0x{:x}'.format(e.hr & 0xffffffff))
                    #print('max fan speed = {:x}'.format(fanspeed & 0xffffffff))
                    #input('press ENTER to continue.' )

                    if self.buf:
                        try:
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
                #self.hcam.Close()
                #self.hcam = None
                #self.buf = None
            else:
                print('failed to open camera')
        else:
            print('no camera found')

if __name__ == '__main__':
    app = Cam()
    app.run()