from datetime import datetime

import argparse
from glob import glob
import os
import pydicom

import cv2

import numpy as np

from pynetdicom import AE, debug_logger
from pynetdicom.sop_class import XRayAngiographicImageStorage


parser = argparse.ArgumentParser()
parser.add_argument('--mode', '-m', default=0, type=int)

debug_logger()

PREX = '20210716-131024-391'


def sstamp():
  return datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]


def update_ds(ds, bmp):
  ds.PixelData = bmp.tobytes() if type(bmp) is np.ndarray else bmp

  for k in ['SOPInstanceUID', 'SeriesInstanceUID', 'StudyInstanceUID']:
    if k in ds:
      ds[k].value = '.'.join((ds[k].value.split('.')[:-1] + [sstamp()]))



if __name__ == '__main__':
  args = parser.parse_args()

  dicoms = glob(os.path.join(PREX, '*.dcm'))
  bmps = glob(os.path.join(PREX, '*.bmp'))

  print(len(dicoms), len(bmps))

  if args.mode == 0:
    # 实验室笔记本
    host, port = '192.168.1.11', 5104
    addr = (host, port)
  elif args.mode == 1:
    # 本机
    host, port = 'localhost', 11112
    addr = (host, port)
  else:
    raise Exception('不支持的Net DICOM模式')

  ae = AE()
  ae.add_requested_context(XRayAngiographicImageStorage)
  ae.ae_title = b'XA'
  print(f'associating {host, port}...')  
  assoc = ae.associate(host, port, ae_title=b'JDICOM')

  ds = pydicom.dcmread('./d.dcm')
  update_ds(ds, cv2.imread('./0.bmp'))


  if assoc.is_established:
    print('Association established with Echo SCP!')
    status = assoc.send_c_store(ds)
    assoc.release()
  else:
    # Association rejected, aborted or never connected
    print('Failed to associate')