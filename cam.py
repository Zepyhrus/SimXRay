import cv2
import numpy as np

from redis import Redis

def bgr2fluro_registration(img):
  disk = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

  I0 = img.astype(np.float64)
  I_r = I0[:, :, 2] - I0[:, :, 1]
  I_r = I_r.clip(0, 255)
  I_r = I_r / (np.max(I_r) + 1e-6)

  I_g = I0[:, :, 1] - I0[:, :, 2]
  I_g = I_g.clip(0, 255)
  I_g = I_g / (np.max(I_g) + 1e-6)

  I_g_shrink = cv2.erode(I_g, disk)
  I_r_dilate = cv2.dilate(I_r, disk)

  I_out = I_g_shrink + I_r_dilate
  I_out /= (np.max(I_out) + 1e-6)
  I_out = 1 - I_out

  return (I_out * 255).astype(np.uint8)


def cam_test():
  for i in range(6):
    cap = cv2.VideoCapture(i)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    # cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 5.0)
    # cap.set(cv2.CAP_PROP_EXPOSURE, 156)

    _, img = cap.read()
    if _:
      print(i)



if __name__ == '__main__':
  r = Redis.from_url('redis://localhost:6379/4')


  frame = r.get('4')

  print(len(frame))

  img = np.frombuffer(frame, dtype=np.uint8)
  img = img.reshape((1024, 1024, 3))
  img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  
  cv2.imshow('_', img)
  cv2.waitKey(0)
  








