import cv2
import cv2.aruco as aruco
import sys
import numpy as np
import pyglet
from pyglet.window import key
from DIPPID import SensorUDP

# network & logic constants
PORT = 5700
ACCEL_SCALAR = 5000.0
SMARTPHONE_MARKER_ID = 5

# globals
video_id = 0
saved_matrix = None
alpha = 0.5

# fusion tracking vars
p_cam = [0.0, 0.0]
p_pred = [0.0, 0.0]
velocity = [0.0, 0.0]

if len(sys.argv) > 1:
    video_id = int(sys.argv[1])

print(f"Starting camera from index {video_id} ... lets pray it works ( ̵˃﹏˂̵ )")
cam = cv2.VideoCapture(video_id)

# checking for webcam
if not cam.isOpened():
    print(f"Could not open webcam {video_id} (」°ロ°)」, check your cables!")
    sys.exit(1)

# check for webcam resolution
CAM_WIDTH = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
CAM_HEIGHT = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(f"Webcam initialized successfully! Resolution: {CAM_WIDTH}x{CAM_HEIGHT}")

# copied from example
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
aruco_params = aruco.DetectorParameters()
detector = aruco.ArucoDetector(aruco_dict, aruco_params)

# setup DIPPID sensor
print(f"Connecting to port {PORT}")
sensor = SensorUDP(PORT)

# user interaction DIPPID app
def on_button(value):
    global p_pred, p_cam, velocity
    if int(value) == 1:
        print("Resetting prediction! Back to square one (｡•̀ᴗ-)✧")
        p_pred[0] = p_cam[0]
        p_pred[1] = p_cam[1]
        velocity = [0.0, 0.0]

sensor.register_callback("button_1", on_button)
print("Ready. Time to make some nooooooise!")

# ordering aruco markers
def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect


win = pyglet.window.Window(CAM_WIDTH, CAM_HEIGHT, caption="Sensor Fusion (｡•̀ᴗ-)✧")

# graphics batch for fast rendering
main_batch = pyglet.graphics.Batch()

# shape elements
cam_dot = pyglet.shapes.Circle(x=p_cam[0], y=p_cam[1], radius=15, color=(255, 0, 0), batch=main_batch)
pred_dot = pyglet.shapes.Circle(x=p_pred[0], y=p_pred[1], radius=10, color=(0, 255, 0), batch=main_batch)
alpha_label = pyglet.text.Label(f'Weight Alpha: {alpha:.2f}', x=20, y=CAM_HEIGHT-40, 
                                font_size=14, batch=main_batch)

def update(dt):
    global saved_matrix, p_cam, p_pred, velocity, alpha
    
    ret, frame = cam.read()
    if not ret:
        print("Camera dropped a frame (╥_╥)")
        return
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # detect aruco markers
    corners, ids, _ = detector.detectMarkers(gray) # type: ignore
    
    # track board and calculate perspective transform
    if ids is not None:
        board_corners = []
        for i, marker_id in enumerate(ids):
            # filter out the smartphone marker from the board computation
            if marker_id[0] != SMARTPHONE_MARKER_ID:
                c = corners[i][0]
                board_corners.append([int(c[:, 0].mean()), int(c[:, 1].mean())])
        
        # if 4 markers for the board were detected, save the matrix
        if len(board_corners) == 4:
            pts1 = np.array(board_corners, dtype="float32")
            pts1 = order_points(pts1)
            pts2 = np.array([[CAM_WIDTH, 0], [0, 0], [0, CAM_HEIGHT], [CAM_WIDTH, CAM_HEIGHT]], dtype=np.float32)
            
            saved_matrix = cv2.getPerspectiveTransform(pts1, pts2)
            
        # track the smartphone marker
        idx_5 = np.where(ids == SMARTPHONE_MARKER_ID)[0]
        if len(idx_5) > 0 and saved_matrix is not None:
            c = corners[idx_5[0]][0]
            center = np.array([[[c[:, 0].mean(), c[:, 1].mean()]]], dtype=np.float32)
            
            # map camera pixel to warped board pixel
            mapped_pt = cv2.perspectiveTransform(center, saved_matrix)
            p_cam[0] = mapped_pt[0][0][0]
            p_cam[1] = mapped_pt[0][0][1]

    # get activity data from DIPPID
    accel = sensor.get_value("accelerometer")
    ax, ay = 0.0, 0.0
    
    if accel is not None:
        # multiply fixed scalar number to the accelerometer
        ax = accel.get("x", 0) * ACCEL_SCALAR
        # DIPPID Y axis needs to be inverted usually due to window coord spaces
        ay = -accel.get("y", 0) * ACCEL_SCALAR 
        
    # integration physics (accel -> velocity -> pos)
    velocity[0] += ax * dt
    velocity[1] += ay * dt
    
    p_accel_x = p_pred[0] + velocity[0] * dt
    p_accel_y = p_pred[1] + velocity[1] * dt
    
    # complementary filter logic!
    p_pred[0] = alpha * p_accel_x + (1.0 - alpha) * p_cam[0]
    p_pred[1] = alpha * p_accel_y + (1.0 - alpha) * p_cam[1]
    
    # update pyglet dot coordinates
    # (Note: Pyglet has origin at bottom-left, so we invert Y for proper mapping!)
    cam_dot.x, cam_dot.y = p_cam[0], CAM_HEIGHT - p_cam[1]
    pred_dot.x, pred_dot.y = p_pred[0], CAM_HEIGHT - p_pred[1]


@win.event
def on_draw():
    win.clear()
    main_batch.draw()

@win.event
def on_close():
    print("Bye bye! (￣▽￣)ノ...")
    cam.release()
    sensor.disconnect()
    
@win.event
def on_keypress(Symbol, Modifier):
    global alpha
    if Symbol == key.UP or Symbol == key.RIGHT:
        alpha = min(1.0, alpha + 0.05)
        print("More accelerometer weight incoming!!!")
    if Symbol == key.DOWN or Symbol == key.LEFT:
        alpha = max(0.0, alpha - 0.05)
        print("More camera weight incoming!!!")
        
    # update text rendering    
    alpha_label.text = f'Weight Alpha: {alpha:.2f}'
        
    if Symbol == key.Q or Symbol == key.ESCAPE:
        cam.release()
        sensor.disconnect()
        pyglet.app.exit()
    
if __name__ == "__main__":
    pyglet.clock.schedule_interval(update, 1/60.0)
    pyglet.app.run()