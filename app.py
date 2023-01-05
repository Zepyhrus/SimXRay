import time, os
import cv2, numpy as np

from flask.globals import current_app
from flask_socketio import SocketIO
from flask import Flask, request, redirect, url_for, render_template, Response
from redis import Redis

import eventlet
eventlet.monkey_patch(socket=True)

from pydicom import dcmread
from pynetdicom import AE
from pynetdicom.sop_class import XRayAngiographicImageStorage
from dclient import update_ds, sstamp

from urx.toolbox import yload, undistort

TEMPLATE = './template.dcm'
REDIS_URL = 'redis://127.0.0.1:6379/4'
R = Redis.from_url(REDIS_URL)

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'sim X-ray machine'
app.config['AE'] = AE()
app.config['AE'].add_requested_context(XRayAngiographicImageStorage)
app.config['AE'].ae_title = b'XA'

sio = SocketIO(app, message_queue=REDIS_URL)

W, H = 1280, 960
AP, LT = 2, 4

cfg = yload('urx/cfg.yaml')


@app.route('/', methods=['GET', 'POST'])
def index():
  if request.method == 'GET':
    return render_template('index.html', size=960, ap=AP, lt=LT)
  return redirect(url_for('index'))


def gen_frames(com):
  camera = cv2.VideoCapture(com)
  camera.set(cv2.CAP_PROP_FRAME_WIDTH, W)
  camera.set(cv2.CAP_PROP_FRAME_HEIGHT, H)

  
  mtx = np.array(cfg['A_AP_webcam'] if com == AP else cfg['A_LT_webcam'])
  dist = np.array(cfg['D_AP_webcam'] if com == AP else cfg['D_LT_webcam'])

  while True:
    success, frame = camera.read()
    if not success:
      return
    
    # frame = frame[:, ::-1, :]
    frame = cv2.resize(frame[:, (W-H)//2:(W+H)//2, :], (1024, 1024))
    frame = undistort(frame, mtx, dist)
    # frame = (cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)).astype(np.uint16)  * 256
    
    _, buffer = cv2.imencode('.bmp', frame)

    R.set(str(com), frame.tobytes())

    yield (b'--frame\r\nContent-Type: image/bmp\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/video_feed?<int:com>')
def video_feed(com):
  return Response(gen_frames(com), mimetype='multipart/x-mixed-replace; boundary=frame')


@sio.on('snapshot')
def io_camera(message):
  print(message)

  frame = R.get(str(message['com']))
  succeed = False
  answer = ''

  ds = dcmread('./template.dcm')
  update_ds(ds, frame)

  assoc = current_app.config['AE'].associate('localhost', 5104, ae_title=b'JDICOM')
  
  if assoc.is_established:
    answer = assoc.send_c_store(ds)
    assoc.release()

    if answer.Status == 0:
      succeed = True

  return {'succeed': succeed, 'answer': str(answer)}

@sio.on('save-image')
def io_save():
  try:
    t = sstamp()
    save_dir = f'static/data/{t}'

    os.makedirs(save_dir, exist_ok=True)

    img_AP = np.frombuffer(R.get(str(AP)), dtype=np.uint8).reshape((1024, 1024, 3))
    img_LT = np.frombuffer(R.get(str(LT)), dtype=np.uint8).reshape((1024, 1024, 3))

    cv2.imwrite(os.path.join(save_dir, 'AP.png'), img_AP)
    cv2.imwrite(os.path.join(save_dir, 'LT.png'), img_LT)
    
    return {'succeed': True, 'message': f'saving to {save_dir}'}
  except Exception as ex:
    return {'succeed': False, 'message': str(ex)}

if __name__ == '__main__':
  sio.run(app, host='0.0.0.0', port=5004)

