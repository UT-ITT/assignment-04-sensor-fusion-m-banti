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

#if not os.path.splitext(output_dest)[1]:
#    output_dest += ".png"
#    print(f"Ooooops, forgot the extension??? No worries, I will save it as: {output_dest}")

# so since macbook is a lil stingy with paths and I tried it now several times I implemented guidlines
# for dummies like meyself


# user (me) parsed stupidly existing folder instead of a real file
if os.path.isdir(output_dest):
    output_dest = os.path.join(output_dest, "extracted_image.png")
    print(f"Oh, you gave me a folder (couldn't be me *cough* *cough*! I'll save the file inside it as: {output_dest}")
else:
    # check if folder part of path is available, otherwise create one
    output_dir = os.path.dirname(output_dest)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"Created a shiny new folder for you: {output_dir}")
        
    # safeguard for the OpenCV extension error that I got three time sin a row
    if not os.path.splitext(output_dest)[1]:
        output_dest += ".png"
        print(f"Ooooops, forgot the extension??? No worries, I will save it as: {output_dest}")

try:
    res_w = int(sys.argv[3])
    res_h = int(sys.argv[4])
except ValueError:
    print("Resolution needs to be numbers, not whatever this is (⇀‸↼‶) ")
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
            
            # warp the 4 points
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
    
    # Fixed window name to match the one you destroy in reset_selection!
    cv2.imshow("I like it, Picasso!!! (｡•̀ᴗ-)✧", warped_img)
    
    # wait for user input on the result window
    while True:
        key = cv2.waitKey(0) & 0xFF
        
        # d to discard
        if key == ord('d') or key == ord('D'):
            print("Discarded (╬ Ò﹏Ó). Let's try again.")
            reset_selection()
            break

        # s to save
        elif key == ord('s') or key == ord('S'):
            cv2.imwrite(output_dest, warped_img)
            print(f"Saved masterpiece to: {output_dest} !! Great job!! ٩(◕‿◕｡)۶")
            reset_selection()
            break
            
        # esc to exit completely
        elif key == 27:
            print("Exiting completely... Bye bye! (￣▽￣)ノ")
            cv2.destroyAllWindows()
            sys.exit(0)

# reset back to start
def reset_selection():
    global selected_points, img_clone
    selected_points = []
    img_clone = img_original.copy() # type: ignore
    try:
        cv2.destroyWindow("I like it, Picasso!!! (｡•̀ᴗ-)✧")
    except:
        pass
    cv2.imshow("image", img_clone)

# load that image
img_original = cv2.imread(input_file)

if img_original is None:
    print("Could not open image (」°ロ°)」Check your path!")
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
        if key == 27:
            print("Canceled (╥_╥)")
            break
            
        # d to discard if you mess up selecting points before reaching 4
        elif key == ord('d') or key == ord('D'):
            if len(selected_points) > 0:
                print("Discarded current points (╬ Ò﹏Ó). Let's try again.")
                reset_selection()
                
except KeyboardInterrupt:
    print("Canceled (╥_╥)")

cv2.destroyAllWindows()