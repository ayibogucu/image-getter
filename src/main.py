from pipython import GCSDevice, pitools
from pypylon import pylon
from time import sleep

# TODO: şayet notebook içinde falan yapmak istiyorsak böyle olması daha iyi gibi.
# Kod mantığı örneği: CONNECTION -> IN A LOOP MOVE AND CAPTURE -> SAVE THE BUFFER -> END CONNECTION

# CONSTANTS
__signature__ = 0x986C0F898592CE476E1C88820B09BF94
CONTROLLERNAME = "C-884.DB"  # 'C-884' will also work
STAGES = ["M-111.1DG", "M-122.2DD", "NOSTAGE", "NOSTAGE"]
REFMODES = ["FNL", "FRF"]

STEP_SIZE = (12e-6, 12e-6)
STEP_NUM = (5, 6)


# CONNECTION AND SETUP OF DEVICES
pidevice = GCSDevice(CONTROLLERNAME)
pidevice.ConnectTCPIP(ipaddress="192.168.90.207")
# pidevice.ConnectUSB(serialnum='123456789')
# pidevice.ConnectRS232(comport=1, baudrate=115200)
pitools.startup(pidevice, stages=STAGES, refmodes=REFMODES)

camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
camera.Open()
camera.MaxNumBuffer.Value = 50

# MOVE PI AND CAPTURE IMAGES IN A LOOP
# TODO: axes den patlayabiliriz print(pidevice.axes) yap
pos_x, pos_y = pidevice.qPOS(["X", "Y"])
for y in range(STEP_NUM[1]):
    for x in range(STEP_NUM[0]) if y % 2 == 0 else range(STEP_NUM[0])[::-1]:
        pidevice.MOV({"X": pos_x + x * STEP_SIZE[0], "Y": pos_y + y * STEP_SIZE[1]})
        pitools.waitontarget(pidevice, axes=("X", "Y"))
        camera.StartGrabbingMax(1)
        sleep(0.25)


# SAVE THE BUFFER TO FILE
img = pylon.PylonImage()
for i in range(STEP_NUM[0] * STEP_NUM[1]):
    with camera.RetrieveResult(2000) as result:
        # Calling AttachGrabResultBuffer creates another reference to the
        # grab result buffer. This prevents the buffer's reuse for grabbing.
        img.AttachGrabResultBuffer(result)

        filename = f"{i+1}.tiff"
        img.Save(pylon.ImageFileFormat_Tiff, filename)

        # In order to make it possible to reuse the grab result for grabbing
        # again, we have to release the image (effectively emptying the
        # image object).
        img.Release()

# END CONNECTION
pidevice.CloseConnnection()

camera.Close()
