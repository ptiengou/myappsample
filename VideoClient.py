import socket
import sys 
import struct 
import time
import json

####################################################
### creating socket and connecting to UE4 server ###
####################################################

# create socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print ("Socket successfully created")
except socket.error as err:
    print ("socket creation failed with error %s" %(err))
 
# define port
port = 12345

# define IP 
try:
    host_ip = socket.gethostbyname('localhost')
except socket.gaierror:
    # this means could not resolve the host, shouldn't happen with localhost though
    print ("there was an error resolving the host")
    sys.exit()
 
# connecting to the server
s.connect((host_ip, port))
print ("the socket has successfully connected to localhost \
on port == %s" %(host_ip))

##########################
### defining functions ###
##########################

#takes time and returns a list of 3 floats --> to generate postion for UE4 (testing without DJI data)
def newPosition(time) :
	p=[0.0, 0.0, 0.0]
	p[0]= 0.0+ 5 * time
	p[1]= 0.0 + 5 * time
	p[2]= 400.0 + 5 * time 
	return p
	
#takes time and returns a list of 3 floats --> to generate rotations for UE4 (testing without DJI data)
def newRotation(time) :
	p=[0.0, 0.0, 0.0]
	p[0]= 0.0
	p[1]= -90.0
	p[2]= time * 3
	return p

#returns distance betweeen two points (3D) in cm
def calculateDistance(x0,y0,z0,x1,y1,z1) :
	dx=x1-x0
	dy=y1-y0
	dz=z1-z0
	d=(dx*dx + dy*dy + dz*dz)**(1/2)
	return(d)

#move from a to b, with a speed in m/s
def moveOnPath(x0,y0,z0,x1,y1,z1,speed,camera_data,s) :
	d=calculateDistance(x0,y0,z0,x1,y1,z1)
	t=d/(speed*100) #seconds
	n=int(t*50) #sending new pos at 50Hz
	dx=(x1-x0)/n
	dy=(y1-y0)/n
	dz=(z1-z0)/n
	x,y,z=x0,y0,z0

	for k in range (n) :
		time.sleep(1/50)
		x+=dx
		y+=dy
		z+=dz
		camera_data['position']['x']= x
		camera_data['position']['y']= y
		camera_data['position']['z']= z
		#redump object to json valid string
		dataString=json.dumps(camera_data)
	    #send string and print time
		s.send(dataString.encode())
		print('new transmission sent : %s' % dataString)

	#to make sure we arrived precisely at the right point
	time.sleep(1/40)
	camera_data['position']['x']= x1
	camera_data['position']['y']= y1
	camera_data['position']['z']= z1
	#redump object to json valid string
	dataString=json.dumps(camera_data)
    #send string and print time
	s.send(dataString.encode())
	print('new transmission sent : %s' % dataString)

#modify Yaw to rotate, in t seconds
def rotateYaw(yaw0,yaw1,t,camera_data, s) :
	n=int(t*50)
	dyaw=(yaw1-yaw0)/n
	yaw=0

	for k in range(n) :
		time.sleep(1/50)
		yaw+=dyaw
		camera_data['rotation']['yaw']=yaw
		#redump object to json valid string
		dataString=json.dumps(camera_data)
	    #send string and print time
		s.send(dataString.encode())
		print('new transmission sent : %s' % dataString)

	#to make sure we arrive precisely to the right yaw
	time.sleep(1/40)
	camera_data['rotation']['yaw']=yaw1
	#redump object to json valid string
	dataString=json.dumps(camera_data)
    #send string and print time
	s.send(dataString.encode())
	print('new transmission sent : %s' % dataString)


################
###waypoints####			
################
speed0=5

x0=0
y0=0
z0=0

x1=2000
y1=5000
z1=1000


############################
###loading data from json###
############################

json_file = open("camera.json" , "r")
#create a json object from template
camera_data = json.load(json_file)

#######################################################################
### while loop to keep generating positions and sending them to UE4 ###
#######################################################################

while (True) :


 #    #declare time
	# current_time = time.clock()
	#modify ID
	camera_data['ID']=0

	#start moving
	rotateYaw(0,90,5,camera_data, s)
	time.sleep(10)
	moveOnPath(x0,y0,z0,x1,y1,z1,speed0,camera_data,s)
	time.sleep(5)




 #    #generate new position
	# p = newPosition(current_time)
	# r = newRotation(current_time)

	# #modify pose in json object (actually a directory) 
	# camera_data['position']['x']= p[0]
	# camera_data['position']['y']= p[1]
	# camera_data['position']['z']= p[2]
	
	# camera_data['rotation']['yaw']= r[0]
	# camera_data['rotation']['pitch']= r[1]
	# camera_data['rotation']['roll']= r[2]
	
	# #redump object to json valid string
	# dataString=json.dumps(camera_data)
 #    #send string and print time
	# s.send(dataString.encode())
	# print('new transmission sent : %s' % dataString)
	# print('time : ' + str(current_time))
