import cv2
from flask.globals import current_app

import numpy as np

from flask_socketio import SocketIO
from flask import Flask, request, redirect, url_for, render_template, Response
from redis import Redis

from pydicom import dcmread
from pynetdicom import AE
from pynetdicom.sop_class import XRayAngiographicImageStorage
from dclient import update_ds


TEMPLATE = './template.dcm'
R = Redis(
  host='192.168.1.25',
  port=6379,
  db=1
)

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'sim X-ray machine'
app.config['DEBUG'] = True
app.config['AE'] = AE()
app.config['AE'].add_requested_context(XRayAngiographicImageStorage)
app.config['AE'].ae_title = b'XA'

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
      frame = frame[:, ::-1, :]
      frame = cv2.resize(frame[:, (w-h)//2:(w-h)//2+h, :], (1024, 1024))
      ret, buffer = cv2.imencode('.bmp', frame)
      R.set(str(com), frame.tobytes())

      yield (b'--frame\r\nContent-Type: image/bmp\r\n\r\n' + buffer.tobytes() + b'\r\n')



@app.route('/video_feed?<int:com>')
def video_feed(com):
  return Response(gen_frames(com), mimetype='multipart/x-mixed-replace; boundary=frame')



@sio.on('snapshot')
def io_camera(message):
  frame = R.get(str(message['com']))
  succeed = False
  answer = ''

  ds = dcmread('./template.dcm')
  update_ds(ds, frame)

  assoc = current_app.config['AE'].associate('', 5104, ae_title=b'JDICOM')
  
  if assoc.is_established:
    answer = assoc.send_c_store(ds)
    assoc.release()

    if answer.Status == 0:
      succeed = True

  return {'succeed': succeed, 'answer': str(answer)}

if __name__ == '__main__':
  sio.run(app, host='0.0.0.0', port=5004)

