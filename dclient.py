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
  return datetime.now().strftime('%Y%m%d%H%M%S')+'.00.00'


def update_ds(ds, bmp):
  ds.PixelData = bmp.tobytes() if type(bmp) is np.ndarray else bmp
  current_sstamp = sstamp()

  for k in ['SOPInstanceUID', 'SeriesInstanceUID', 'StudyInstanceUID']:
    if k in ds:
      ds[k].value = '.'.join((ds[k].value.split('.')[:-1] + [current_sstamp]))
  
  ds['ContentDate'].value = current_sstamp[:6]
  ds['ContentTime'].value = current_sstamp[6:]



if __name__ == '__main__':
  args = parser.parse_args()

  dicoms = glob(os.path.join(PREX, '*.dcm'))
  bmps = glob(os.path.join(PREX, '*.bmp'))

  print(len(dicoms), len(bmps))


  host, port = 'localhost', 5104
  addr = (host, port)

  ae = AE()
  ae.add_requested_context(XRayAngiographicImageStorage)
  ae.ae_title = b'XA'
  print(f'associating {host, port}...')  
  assoc = ae.associate(host, port, ae_title=b'JDICOM')

  ds = pydicom.dcmread('./template.dcm')
  update_ds(ds, cv2.imread('out/1.2.840.113780.990001.92728050044.20211226112452.1.40.bmp'))


  if assoc.is_established:
    print('Association established with Echo SCP!')
    status = assoc.send_c_store(ds)
    assoc.release()
  else:
    # Association rejected, aborted or never connected
    print('Failed to associate')