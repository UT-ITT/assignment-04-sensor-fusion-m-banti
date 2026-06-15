import cv2
import cv2.aruco as aruco
import sys

# so this script checks what dictionary you need to use for the AR_game.py
# originally I wanted it to be dynamically in the AR_game.py but my markers couldn't be found correctly
# and I was wasting a lot of time so I thought maybe I just outsource it to an own script and then
# I can change manually the line of code in AR_game.py (I know automated would be cooler but I'm not so good in python haha)
# it will show you a range and recommends to you the highest range to select as aruco dictionary

# some dictionaries from: https://pyimagesearch.com/2020/12/21/detecting-aruco-markers-with-opencv-and-python/
ARUCO_DICTS = {
    "4X4_50": aruco.DICT_4X4_50,
    "4X4_250": aruco.DICT_4X4_250,
    "5X5_50": aruco.DICT_5X5_50,
    "5X5_250": aruco.DICT_5X5_250,
    "6X6_50": aruco.DICT_6X6_50,
    "6X6_250": aruco.DICT_6X6_250,
    "7X7_50": aruco.DICT_7X7_50,
    "ORIGINAL": aruco.DICT_ARUCO_ORIGINAL
}

video_id = 0
if len(sys.argv) > 1:
    video_id = int(sys.argv[1])

cap = cv2.VideoCapture(video_id)

if not cap.isOpened():
    print("Could not open camera!")
    sys.exit(1)

print("Lets check what Aruco Markers we have here...")

found_ranges = set()

while True:
    ret, frame = cap.read()
    if not ret:
        break
        
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    active_dict_range = "Searching..."
    
    matches_this_frame = []
    
    best_corners = None
    best_ids = None
    
    # scan every dictionary every frame
    for dict_name, dict_constant in ARUCO_DICTS.items():
        aruco_dict = aruco.getPredefinedDictionary(dict_constant)
        aruco_params = aruco.DetectorParameters()
        detector = aruco.ArucoDetector(aruco_dict, aruco_params)
        
        corners, ids, _ = detector.detectMarkers(gray) # type: ignore
        
        if ids is not None:
            matches_this_frame.append(dict_name)
            # Save the coordinates to draw later
            best_corners = corners
            best_ids = ids
            
    if matches_this_frame and best_ids is not None:
        # get highest dict for recommended dict selection
        highest_dict = matches_this_frame[-1]
        # figure out range
        if len(matches_this_frame) == 1:
            range_string = matches_this_frame[0]
        else: 
            range_string = f"{matches_this_frame[0]} to {matches_this_frame[-1]}"
        
        active_dict_range = f"Active range: {range_string}"
        
        if range_string not in found_ranges:
            print(f"Match found, you can use a dictionary in following range: {range_string}. Choose highest dictionary = {highest_dict}")
            found_ranges.add(range_string)
        
        aruco.drawDetectedMarkers(frame, best_corners, best_ids) # type: ignore
        
        # grab top-left corner of first marker
        c = best_corners[0][0] # type: ignore
        top_left_x = int(c[0][0])
        top_left_y = int(c[0][1])
        
        # draw yellow range directly UNDER blue ID
        cv2.putText(frame, range_string, (top_left_x - 40, top_left_y + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            
    if active_dict_range == "Searching...":
        cv2.putText(frame, active_dict_range, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    else:
        cv2.putText(frame, active_dict_range, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(frame, f"Choose highest dictionary: {highest_dict}", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2) # type: ignore

    cv2.imshow("Dictionary", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()