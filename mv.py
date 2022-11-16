import redis
import cv2
import numpy as np


if __name__ == '__main__':
  buffer = redis.from_url('redis://127.0.0.1:6379/4').get('0')
  img = np.frombuffer(buffer, dtype=np.uint8)
  img = img.reshape((1024, 1024, 3))
  img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  print(len(img))


  cv2.imshow('_', img)
  cv2.waitKey(0)