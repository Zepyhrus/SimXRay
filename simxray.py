import cv2

import numpy as np

from flask_socketio import SocketIO
from flask import Flask, request, redirect, url_for, render_template, Response
from redis import Redis


R = Redis()

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'sim X-ray machine'
app.config['DEBUG'] = True

sio = SocketIO(app)


@app.route('/', methods=['GET', 'POST'])
def index():
  if request.method == 'GET':
    return render_template('index.html')
  return redirect(url_for('index'))


def gen_frames(com):
  camera = cv2.VideoCapture(com)
  camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
  camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 960)

  while True:
    success, frame = camera.read()
    if not success:
      break
    else:
      h, w, c = frame.shape # 480, 640, 3
      frame = cv2.resize(frame[:, (w-h)//2:(w-h)//2+h, :], (1024, 1024))
      ret, buffer = cv2.imencode('.bmp', frame)
      frame = buffer.tobytes()
      R.set(str(com), frame)

      yield (b'--frame\r\n'
      b'Content-Type: image/bmp\r\n\r\n' + frame + b'\r\n')



@app.route('/video_feed?<int:com>')
def video_feed(com):
  return Response(gen_frames(com), mimetype='multipart/x-mixed-replace; boundary=frame')



@sio.on('snapshot')
def io_camera(message):
  frame = R.get(str(message['com']))

  with open(f'{message["com"]}.bmp', 'wb') as f:
    f.write(frame)


  return {'frame': frame}

if __name__ == '__main__':
  sio.run(app, host='0.0.0.0', port=5000)

