import cv2, numpy as np

from dclient import AE, dcmread, update_ds, XRayAngiographicImageStorage
from urx.cam import Oly, Dalek
from urx.toolbox import CountsPerSec



if __name__ == '__main__':
  with  Oly(0, 2, (640, 480)) as o:
    o.simXRay()