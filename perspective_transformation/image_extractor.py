'''
ToDos: 
- loads and display image with OpenCV
- clicking into image user should be able to select four points
- selected region is wrapped into rectangle
- wraped result should be displayed
- pressing S in the result view, the image should be saved
- Paths to the input file and output destination and results resolution should be specified via terminal
''' 
import cv2
import sys
import numpy as np
import os

# check command line parameters
if len(sys.argv) != 5:
    print("Usage: python3 image_extractor.py <input_path> <output_path> <width> <height>")
    sys.exit(1)

input_file = sys.argv[1]
output_dest = sys.argv[2]

if not os.path.splitext(output_dest)[1]:
    output_dest += ".png"
    print(f"Ooooops, forgot the extension??? No worries, I will save it as: {output_dest}")

try:
    res_w = int(sys.argv[3])
    res_h = int(sys.argv[4])
except ValueError:
    print("Resolution needs to be numbers >:((((")
    sys.exit(1)

# global state variables
selected_points = []
img_clone = None
img_original = None

# sort points so they always map correctly to: 
# top-left, top-right, bottom-right, bottom-left
def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    
    # top-left will have smallest sum, bottom-right largest sum
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    
    # top-right will have smallest diff, bottom-left largest diff
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    
    return rect

# handle user clicking
def mouse_callback(event, x, y, flags, param):
    global selected_points, img_clone
    
    # grab point on left click
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(selected_points) < 4:
            selected_points.append([x, y])
            
            # draw a little green dot where clicked
            cv2.circle(img_clone, (x, y), 5, (50, 255, 50), -1) # type: ignore
            cv2.imshow("image", img_clone) # type: ignore
            print(f"Point {len(selected_points)} selected!")
            
            # if we got 4 points, time to warp!
            if len(selected_points) == 4:
                print("Got 4 points! Warping timeeee")
                process_warp()

# warp logic
def process_warp():
    global selected_points, img_original
    
    pts1 = np.array(selected_points, dtype="float32")
    pts1 = order_points(pts1)
    
    # map to desired resolution rectangle
    pts2 = np.float32([[0, 0], [res_w, 0], [res_w, res_h], [0, res_h]]) # type: ignore
    
    # calculate matrix and warp
    matrix = cv2.getPerspectiveTransform(pts1, pts2) # type: ignore
    warped_img = cv2.warpPerspective(img_original, matrix, (res_w, res_h)) # type: ignore
    
    cv2.imshow("result", warped_img)
    
    # wait for user input on the result window
    while True:
        key = cv2.waitKey(0) & 0xFF
        
        # esc to discard
        if key == ord('d') or key == ord('D'):
            print("Discarded >:(((( Let's try again.")
            reset_selection()
            break

        # s to save
        elif key == ord('s') or key == ord('S'):
            cv2.imwrite(output_dest, warped_img)
            print(f"Saved masterpiece to: {output_dest} !! Great job!!")
            reset_selection()
            break
            
        # x to exit
        elif key == ord('x') or key == ord('X'):
            print("Exiting completely... Bye bye!")
            cv2.destroyAllWindows()
            sys.exit(0)

# reset back to start
def reset_selection():
    global selected_points, img_clone
    selected_points = []
    img_clone = img_original.copy() # type: ignore
    try:
        cv2.destroyWindow("I like it, Picasso!!")
    except:
        pass
    cv2.imshow("image", img_clone)

# load that image
img_original = cv2.imread(input_file)

if img_original is None:
    print("Could not open image >:( Check your path!")
    sys.exit(1)

img_clone = img_original.copy()

# setup main window and callbacks
cv2.namedWindow("image")
cv2.setMouseCallback("image", mouse_callback)

print("\nReady. Time to make some nooooooise... wait, I mean extract some images!")
print("Click 4 corners to extract a region.")
cv2.imshow("image", img_clone)

# main loop
try:
    while True:
        key = cv2.waitKey(1) & 0xFF
        # esc on main window to quit entirely
        if key == ord('d') or key == ord('D') and len(selected_points) < 4:
            print("Canceled :(")
            break
except KeyboardInterrupt:
    print("Canceled :(")

cv2.destroyAllWindows()