import os
import cv2

import numpy as np

from pydicom.uid import ImplicitVRLittleEndian
from pynetdicom import AE, debug_logger, evt
from pynetdicom.sop_class import XRayAngiographicImageStorage



debug_logger()

PREX = '20210716-131024-391'



def handle_store(event, storage_dir):
  """Handle EVT_C_STORE events."""
  try:
    os.makedirs(storage_dir, exist_ok=True)
  except:
    return 0xC001

  ds = event.dataset

  print(len(ds.PixelData))

  if len(ds.PixelData) == 2097152:
    img = np.frombuffer(ds.PixelData, dtype=np.uint16)
    img = (img.reshape((ds.Rows, ds.Columns)) / 256).astype(np.uint8)
  elif len(ds.PixelData) == 3145728:
    img = np.frombuffer(ds.PixelData, dtype=np.uint8)
    img = img.reshape((ds.Rows, ds.Columns, 3))
  else:
    raise Exception('Not support pixel data format...')

  cv2.imwrite(os.path.join(storage_dir, ds.SOPInstanceUID + '.bmp'), img)
  
  return 0x0000

if __name__ == '__main__':
  handlers = [(evt.EVT_C_STORE, handle_store, ['out'])]

  ae = AE()
  ae.add_supported_context(XRayAngiographicImageStorage, ImplicitVRLittleEndian)

  ae.start_server(('0.0.0.0', 5104), block=True, evt_handlers=handlers) # 
