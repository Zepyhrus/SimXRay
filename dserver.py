import os
import cv2

import numpy as np


if __name__ == '__main__':
  # 启动一个dicom server，用于接收来自X光机的dicom文件
  from pydicom.uid import ImplicitVRLittleEndian
  from pynetdicom import AE, debug_logger, evt
  from pynetdicom.sop_class import XRayAngiographicImageStorage
  from pynetdicom.sop_class import _VERIFICATION_CLASSES as VC

  debug_logger()

  def handle_store(event, storage_dir):
    """Handle EVT_C_STORE events."""
    try:
      os.makedirs(storage_dir, exist_ok=True)
    except:
      return 0xC001

    ds = event.dataset

    if len(ds.PixelData) == 2097152:
      img = np.frombuffer(ds.PixelData, dtype=np.uint16)
      img = (img.reshape((ds.Rows, ds.Columns)) / 256).astype(np.uint8)
    elif len(ds.PixelData) == 3145728:
      img = np.frombuffer(ds.PixelData, dtype=np.uint8)
      img = img.reshape((ds.Rows, ds.Columns, 3))
    else:
      raise Exception('Not support pixel data format...')
    img = np.rot90(img, 1) # TODO: -1 为实验室，1 为医院
    bmp = os.path.join(storage_dir, ds.SOPInstanceUID + '.bmp')
    print(bmp, 'saved...')
    cv2.imwrite(bmp, img)
    
    return 0x0000
  
  handlers = [(evt.EVT_C_STORE, handle_store, ['static/data'])]
  ae = AE()
  ae.add_supported_context(XRayAngiographicImageStorage, ImplicitVRLittleEndian)
  for key in VC:
    ae.add_supported_context(VC[key])


  print('server starting...')
  ae.start_server(('0.0.0.0', 5104), block=True, evt_handlers=handlers)
