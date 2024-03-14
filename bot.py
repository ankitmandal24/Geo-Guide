"""
# Team Id : <1742>
# Author List : <Ankit Mandal,Vikas Kumar,B Sai Sannidh Rayalu,Shashwat Bokhad>
#
# Filename: <bot.py>
# Theme: <GEOGUIDE>
# Functions: <read_csv(str), write_csv(int, int, str), tracker(int, dict), fdirection(int, float, float), cartx(int, int, int, int), findqd(int, int, int , int), eventx(str, str), calca(float, float), calkm(int, int, int, int), process_aruco_markers(list, int, cv2.aruco_Detector, cv2.Video_Capture, str, int, str, list, socket.socket), show_live_feed(cv2.Video_Capture)>

# Global Variables: <botid, cap, aruco_dict, parameters, detector, csv_path, my_file, data, data_into_list, event_coordinates, priority_lst, pathx, ip, port, kp, arucolst, conn>
"""
import cv2
import numpy as np
import time
import socket
import math
import csv
from time import sleep
import threading
import warnings

# Filter out the DeprecationWarning
warnings.filterwarnings("ignore", category=DeprecationWarning)


botid = 100                                  #  Integer representing the ID of the robot.
cap = cv2.VideoCapture(0)                    # Video capture object (cv2.VideoCapture).
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1980)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)  # Aruco dictionary obtained from cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250).
parameters = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
csv_path = r"C:\Users\ankit\Desktop\stage_5\lat_long.csv"               # Path to the CSV file containing AR marker data.
my_file = open("priority_results_with_coordinates.txt", "r")            # File object for reading "priority_results_coordinates.txt".


# reading the file
data = my_file.read()                       # String variable storing the content read from the file.
data_into_list = list(data.split("\n"))     # List containing data parsed from the file.


# print(data_into_list)
my_file.close()
event_coordinates = []                      # List containing coordinates of events.
priority_lst=[]                             # List containing priority markers.
pathx=[]                                    # List containing path coordinates.


# Parsing priority results coordinates from a file
#taking the coordinate,where bot will stop for event
for x in data_into_list:

    lk = ""
    for i in x:
        if i == '0' or i == '1' or i == '2' or i == '3' or i == '4' or i == '5' or i == '6' or i == '7' or i == '8' or i == '9' or i == ',':
            lk += i
    lk += ','
    # print(lk)
    lst = []
    ch = ""
    if lk != ',':
        for p in lk:
            if p != ',':
                ch += p
            else:
                lst.append(int(ch))
                ch = ""

        event_coordinates.append(lst)


# Extracting priority locations
for x in data_into_list:
    for i in x:
        if i=="A" or i=="B" or i=="C" or i=="D" or i=="E":
            priority_lst.append(i)


# Adjusting event coordinates
for i in range(len(event_coordinates)):
    event_coordinates[i][1] -= 98 


# Appending a fixed coordinate as the last event coordinate
event_coordinates.append([550, 994])


# It Contains the pixels point, helping coordinates for bot traversal in the arena.
pathplan2 = {
    'A': [646, 879],
    'B': [1006, 674],
    'C': [1013, 483],
    'D': [912, 482],
    'E': [1320, 202]
}


# It appends the coordinates into pathx list according to priority of events.
for px in priority_lst:
    pathx.append(pathplan2[px])

pathx.append([550, 994])


"""
# Function Name: read_csv
# Input:
#     csv_name (str) - Path to the CSV file containing AR marker data.
# Output:
#     lat_lon (dict) - Dictionary containing AR marker IDs as keys and corresponding latitude and longitude coordinates as values.
# Logic:
#     Reads the CSV file containing AR marker data (ID, latitude, and longitude).
#     Parses the data and stores it in a dictionary.
#     Returns the dictionary.
# Example Call:
      csv_data = read_csv("lat_long.csv")
"""
def read_csv(csv_name):
    lat_lon = {}
    with open(csv_name, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file, fieldnames=['id', 'lat', 'lon'])
        for row in csv_reader:
            if 'lat' in row and 'lon' in row:
                lat = (row['lat'])
                lon = (row['lon'])
                ar_id = (row['id'])
                lat_lon[ar_id] = [lat, lon]
    return lat_lon


"""
# Function Name: write_csv
# Input:
#     lat (float) - Latitude coordinate to be written to the CSV file.
#     lon (float) - Longitude coordinate to be written to the CSV file.
#     csv_name (str) - Path to the CSV file.
# Output:
#     None
# Logic:
#     Writes the provided latitude and longitude coordinates to a CSV file.
# Example Call:
#     write_csv(40.7128, -74.0060, "lat_long.csv")
"""
def write_csv(lat, lon, csv_name):
    with open(csv_name, mode='w', newline='') as csv_file:
        fieldnames = ['lat', 'lon']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({'lat': lat, 'lon': lon})


"""
# Function Name: tracker
# Input:
#     ar_id (int) - AR marker ID for which coordinates are to be tracked.
#     lat_lon (dict) - Dictionary containing AR marker IDs as keys and corresponding latitude and longitude coordinates as values.
# Output:
#     coordinate (list) - List containing latitude and longitude coordinates associated with the provided AR marker ID.
# Logic:
#     Checks if the provided AR marker ID exists in the given dictionary.
#     If found, retrieves the latitude and longitude coordinates associated with the AR marker ID.
#     Writes the coordinates to a CSV file using the write_csv function.
#     Returns the coordinates.
# Example Call:
#    ar_marker_coordinates = tracker(123, {"123": [40.7128, -74.0060]})
"""
def tracker(ar_id, lat_lon):
    coordinate = []
    if str(ar_id) in lat_lon:
        x = float(lat_lon[str(ar_id)][0])
        y = float(lat_lon[str(ar_id)][1])
        coordinate = [x, y]
        write_csv(coordinate[0], coordinate[1], r"C:\Users\ankit\Desktop\stage_5\live_data.csv")

    # Also return coordinate ([lat, lon]) associated with respective ar_id.
    return coordinate


"""
# Function Name: fdirection
# Input:
#     qd (int) - Quadrant direction.
#     path1 (float) - Path 1 value.
#     path2 (float) - Path 2 value.
# Output:
#     direction (str) - Direction value ('F', 'R', 'L', 'U').
# Logic:
#     Determines the direction based on the quadrant direction and path values.
#     Returns the direction.
# Example Call:
#     direction = fdirection(1, 10, 20)
"""
def fdirection(qd, path1, path2):
    if qd == 1:
        if path1 < path2:
            return 'F'
        else:
            return 'R'

    elif qd == 2:
        if path1 < path2:
            return 'F'
        else:
            return 'L'

    elif qd == 3:
        if path1 < path2:
            return 'U'
        else:
            return 'L'

    elif qd == 4:
        if path1 < path2:
            return 'U'
        else:
            return 'R'


"""
# Function Name: cartx
# Input:
#     x1 (int) - X-coordinate of point 1.
#     y1 (int) - Y-coordinate of point 1.
#     x2 (int) - X-coordinate of point 2.
#     y2 (int) - Y-coordinate of point 2.
# Output:
#     distance (float) - Distance between the two points.
# Logic:
#     Calculates the Cartesian distance between two points using their coordinates.
#     Returns the distance.
# Example Call:
#     distance = cartx(0, 0, 3, 4)
"""
def cartx(x1, y1, x2, y2):
    return math.sqrt((math.pow(x1 - x2, 2)) + (math.pow(y1 - y2, 2)))


"""
# Function Name: findqd
# Input:
#     x1 (int) - X-coordinate of point 1.
#     x2 (int) - X-coordinate of point 2.
#     y1 (int) - Y-coordinate of point 1.
#     y2 (int) - Y-coordinate of point 2.
# Output:
#     qd (int) - Quadrant direction.
# Logic:
#     Determines the quadrant direction based on the coordinates of two points.
#     Returns the quadrant direction.
# Example Call:
#     quadrant_direction = findqd(1, 3, 4, 6)
"""
def findqd(x1, x2, y1, y2):
    if y1 < y2 and x1 < x2:
        return 1

    elif y1 < y2 and x1 > x2:
        return 2

    elif y1 > y2 and x1 > x2:
        return 3

    elif y1 > y2 and x1 < x2:
        return 4


"""
# Function Name: eventx
# Input:
#     sendx (str) - Direction string.
# Output:
#     event (str) - Event string ('K' or 'W').
# Logic:
#     Determines the event type based on the direction string.
#     Returns the event type.After visiting even it checks where the next event is and send signal where 'K' means uturn and 'W' means forward
# Example Call:
#     event_type = eventx("U")
"""
def eventx(sendx):
    if sendx == "U":
        return "K"
    else:
        return "W"


"""
# Function Name: calca
# Input:
#     m1 (float) - Slope 1 value.
#     m2 (float) - Slope 2 value.
# Output:
#     angle (float) - Angle value.
# Logic:
#     Calculates the angle between two slopes.
#     Returns the angle.
# Example Call:
#     angle = calca(1, 2)
"""
def calca(m1, m2):
    if (1 + m1 * m2) == 0:
        return 90
    else:
        return np.tanh(abs(m2 - m1) / (1 + m1 * m2))


"""
# Function Name: calkm
# Input:
#     x1 (int) - X-coordinate of point 1.
#     y1 (int) - Y-coordinate of point 1.
#     x2 (int) - X-coordinate of point 2.
#     y2 (int) - Y-coordinate of point 2.
# Output:
#     slope (int) - Slope value.
# Logic:
#     Calculates the slope between two points.
#     Returns the slope.
# Example Call:
#     slope = calkm(0, 0, 3, 4)
"""
def calkm(x1, y1, x2, y2):
    if x2 - x1 == 0:
        return 90
    else:
        return int((y2 - y1) / (x2 - x1))


ip = "192.168.214.4"  #IP address for socket communication.
port = 8002  # Replace with your desired port number


# Server code
arucolst = []       # List containing AR marker data.


"""
this code continuously captures frames from a camera, detects ArUco markers, and stores information about
the markers (excluding a specific marker identified by botid) in a list until it detects a total of 47 markers.
"""
while len(arucolst)<47:
    kssp, image = cap.read()
    corners, ids, _ = detector.detectMarkers(image)
    if ids is not None and botid in ids:
        for cn,id in zip(corners,ids):
            if id!=botid:
                x = int((cn[0][0][0] + cn[0][2][0]) / 2.0)
                y = int((cn[0][1][1] + cn[0][3][1])  / 2.0)
                arucolst.append([id,x,y])


"""
# Function Name: process_aruco_markers
# Input:
#     arucolst (list) - List containing AR marker data.
#     botid (int) - ID of the robot.
#     detector (cv2.aruco_Detector) - Aruco detector object.
#     cap (cv2.VideoCapture) - Video capture object.
#     ip (str) - IP address for socket communication.
#     port (int) - Port number for socket communication.
#     csv_path (str) - Path to the CSV file containing AR marker data.
#     event_coordinates (list) - List containing event coordinates.
#     conn (socket.socket) - Socket connection object.
# Output:
#     None
# Logic:
#     Processes ARUCO marker data, calculates directions, and sends instructions to the robot via socket communication.
"""
def process_aruco_markers(arucolst, botid, detector, cap, ip, port, csv_path, event_coordinates,conn):
            i = 0
            aid = 0
            while True:
                data = conn.recv(1).decode('utf-8')
                ret, frame = cap.read()
                bot_corners = []
                if not ret:
                    break

                corners, ids, _ = detector.detectMarkers(frame)

                # finding the bot position and its corners for crating its xy cartial frame which will tell us the where the bot has to go
                if ids is not None and botid in ids:
                    bot_index = np.where(ids == botid)[0][0]
                    bot_corners = corners[bot_index][0]
                    bot_position = np.mean(bot_corners, axis=0).astype(int)

                    # if the data is recieved from bot is 'N' it means the bot has visited a node and then the path planning algorith will tell the bot hwere to go left right forward or uturn
                    if len(bot_corners) != 0 and data == 'N':
                        #(pathx[i][0],pathx[i][1]) is the road cordinates for better and correct travesing of bot in the arena
                        sendx = ""
                        while sendx == "":
                            cnk = bot_corners
                            fx = int(cnk[0][0])     #x value of bot
                            fy = int(cnk[0][1])     #y value of boot
                            fyx = (2 * int(cnk[0][0]) - int(cnk[3][0])) #+ve y axis x value
                            fyy = (2 * int(cnk[0][1]) - int(cnk[3][1]))  #ve y axis y value
                            fyx_ = int(cnk[3][0])   #-ve y axis x value
                            fyy_ = int(cnk[3][1])   #-ve y axis y value
                            fxx = int(cnk[1][0])     #+ve x axis x value
                            fxy = int(cnk[1][1])     #+ve x axis y value
                            fxx_ = (2 * int(cnk[0][0]) - int(cnk[1][0]))        #-ve x axis x value
                            fxy_ = (2 * int(cnk[0][1]) - int(cnk[1][1]))        #-ve x axis y value
                            y1 = cartx(fyx, fyy, pathx[i][0], pathx[i][1])      #finding cartision distance b/w +ve y axis and the point where the bot has to visit which helps in finding the quadrent where the point lies in respect of bot xy axis
                            y2 = cartx(fyx_, fyy_, pathx[i][0], pathx[i][1])    #finding cartision distance b/w -ve y axis and the point where the bot has to visit which helps in finding the quadrent where the point lies in respect of bot xy axis
                            x1 = cartx(fxx, fxy, pathx[i][0], pathx[i][1])      #finding cartision distance b/w +ve x axis and the point where the bot has to visit which helps in finding the quadrent where the point lies in respect of bot xy axis
                            x2 = cartx(fxx_, fxy_, pathx[i][0], pathx[i][1])    #finding cartision distance b/w -ve x axis and the point where the bot has to visit which helps in finding the quadrent where the point lies in respect of bot xy axis
                            qd = findqd(x1, x2, y1, y2)                         # finding quadrent which decides what are the correct options of bot to move ex:- if the quadrent is 1 then the options are forward and left
                            path1 = calca(calkm(fyx, fyy, fyx_, fyy_), calkm(fx, fy, pathx[i][0], pathx[i][1]))     #finding angle of line wrt y axis which contains orifit of bot frame and the point
                            path2 = calca(calkm(fxx, fxy, fxx_, fxy_), calkm(fx, fy, pathx[i][0], pathx[i][1]))     #finding angle of line wrt x axis which contains orifit of bot frame and the point
                            sendx = fdirection(qd, path1, path2)     # finally finding the correct instruction for bot to follow
                        conn.sendall(sendx.encode('utf-8'))          #sending the data

                    # All logic and variables are same here as above, the only difference is instead of pathx we used event coordinates in path 1 and path 2
                    elif len(bot_corners) != 0 and (cartx(bot_position[0], bot_position[1], event_coordinates[i][0],event_coordinates[i][1]) <= 33):# if distance is less than 33 pixels the bot stps at the event point
                        cnk = bot_corners
                        fx = int(cnk[0][0])
                        fy = int(cnk[0][1])
                        fyx = (2 * int(cnk[0][0]) - int(cnk[3][0]))
                        fyy = (2 * int(cnk[0][1]) - int(cnk[3][1]))
                        fyx_ = int(cnk[3][0])
                        fyy_ = int(cnk[3][1])
                        fxx = int(cnk[1][0])
                        fxy = int(cnk[1][1])
                        fxx_ = (2 * int(cnk[0][0]) - int(cnk[1][0]))
                        fxy_ = (2 * int(cnk[0][1]) - int(cnk[1][1]))
                        y1 = cartx(fyx, fyy, event_coordinates[i][0], event_coordinates[i][1])
                        y2 = cartx(fyx_, fyy_, event_coordinates[i][0], event_coordinates[i][1])
                        x1 = cartx(fxx, fxy, event_coordinates[i][0], event_coordinates[i][1])
                        x2 = cartx(fxx_, fxy_, event_coordinates[i][0], event_coordinates[i][1])
                        qd = findqd(x1, x2, y1, y2)
                        path1 = calca(calkm(fyx, fyy, fyx_, fyy_), calkm(fx, fy, event_coordinates[i][0],
                                                                        event_coordinates[i][1]))
                        path2 = calca(calkm(fxx, fxy, fxx_, fxy_), calkm(fx, fy, event_coordinates[i][0],
                                                                        event_coordinates[i][1]))
                        i += 1
                        # print("Event")
                        if (i == len(event_coordinates)):
                            conn.sendall(str.encode("E"))
                            i = 0
                        else:
                            sendx = eventx(fdirection(qd, path1, path2))
                            conn.sendall(sendx.encode('utf-8'))
                            sleep(5)
                        conn.sendall(str.encode("D"))


"""
# Function Name: show_live_feed
# Input:
#     cap (cv2.VideoCapture) - Video capture object.
# Output:
#     None
# Logic:
#     Displays the live video feed with Aruco marker detection.It detects bot id and anf find the nearest aruco id from it and matches
#     aruco id with lat_long.csv file and update the live data and qgis
# Example Call :
      show_live_feed(cap)
"""
def show_live_feed(cap):

    while True:
        ret, frame = cap.read()                                   # Fram capture throught Camera
        if not ret:
            break
        corners, ids, _ = detector.detectMarkers(frame)           # List Corner and ID's of all aruco's on arena
        i = 0
        aid = 0                                                   # Aruco ID's

        if ids is not None and botid in ids:
            bot_index = np.where(ids == botid)[0][0]              # Bot id
            bot_corners = corners[bot_index][0]                   # Corners of Bot
            bot_position = np.mean(bot_corners, axis=0).astype(int)     # Bots Coordinates

            mx = 10000                                             # High Cap for distance between bot and aruco
            for x in range(len(arucolst)):
                ds = cartx(int(arucolst[x][1]), int(arucolst[x][2]), int(bot_position[0]),      # Calculating Distance between bot and aruco id
                           int(bot_position[1]))
                if ds < mx:                                                                     # if current distance is smaller that previous distance then we append current aruco id to aid and update mx to current distance
                    aid = int(arucolst[x][0])
                    mx = ds
            lat_lon = read_csv(csv_path)
            t_point = tracker(aid, lat_lon)

        frame = cv2.resize(frame, (800, 800))                                                    # Resizing frame
        cv2.imshow('Live Feed', frame)                                                           # Live feed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


# Create threads for both functions
# Create a TCP socket object
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)      # Set socket options to allow reusing the same address
    s.bind((ip, port))                                           # Bind the socket to a specific IP address and port
    s.listen()                                                   # Start listening for incoming connections
    conn, addr = s.accept()                                      # Socket connection object>
    with conn:

        """
        we created global variable of camera frame and sending it to the two different function and using concurrently with the help of threading
        """
        thread_show_live_feed = threading.Thread(target=show_live_feed, args=(cap,))
        thread_process_aruco_markers = threading.Thread(target=process_aruco_markers, args=(arucolst, botid, detector, cap, ip, port, csv_path, event_coordinates,conn))

        # Start the threads
        thread_show_live_feed.start()       # Threads for show_live_feed funtion
        thread_process_aruco_markers.start()   # Threads for process_aruco_markers funtion

        # Join the threads to wait for their completion
        thread_show_live_feed.join()
        thread_process_aruco_markers.join()
