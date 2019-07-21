from . import lasercommands
import logging

def laser():
    global_dict = globals()
    for key, val in list(globals().items()):
        if isinstance(val, lasercommands.laser):
            key.EnableWhisperMode(False)
            key.EnableLaser(False)
            key.sercon.close()        
            del globals()[key]

def logs():
    global_dict = globals()
    for key, val in list(globals().items()):
        if isinstance(val, logging.Logger):
            logging.shutdown()
            del logger