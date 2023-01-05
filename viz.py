import cv2, numpy as np
from redis import Redis


if __name__ == '__main__':
  frame = cv2.imread('static/pattern.png')
  print(frame.shape)
  _, buffer = cv2.imencode('.bmp', frame)
  

  with Redis.from_url('redis://127.0.0.1:6379/4') as r:
    r.set(str(2), frame.tobytes())

  bf = r.get(str(2))

  print(len(buffer), len(bf))

  img = np.frombuffer(bf, dtype=np.uint8).reshape(frame.shape)

  cv2.imshow('_', img)
  cv2.waitKey(0)

