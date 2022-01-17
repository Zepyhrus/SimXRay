import cv2
import numpy as np


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



if __name__ == '__main__':
  cap_ap = cv2.VideoCapture(2)
  cap_lt = cv2.VideoCapture(2)

  w, h = 160, 120

  cap_ap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
  cap_ap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
  cap_lt.set(cv2.CAP_PROP_FRAME_WIDTH, w)
  cap_lt.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

  while True:
    success_ap, frame_ap = cap_ap.read()
    success_lt, frame_lt = cap_lt.read()

    if success_ap and success_lt:
      cv2.imshow('_', np.hstack((frame_ap, frame_lt)))
      if cv2.waitKey(1) == 27:
        break
    
    # if success_lt:
    #   cv2.imshow('_', frame_lt)
    #   if cv2.waitKey(1) == 27:
    #     break


  # for i in range(5):
  #   cap = cv2.VideoCapture(i)
  #   cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
  #   cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 960)
  #   # cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 5.0)
  #   # cap.set(cv2.CAP_PROP_EXPOSURE, 156)

  #   _, img = cap.read()
  #   if _:
  #     print(i)
  #     # img = cv2.resize(img[:, 160:1120, :], (1024, 1024))
  #     # # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  #     # cv2.imshow('__', img)
  #     # cv2.imshow('_', bgr2fluro_registration(img))

  #     # if cv2.waitKey(0) == 27:
  #     #   break








