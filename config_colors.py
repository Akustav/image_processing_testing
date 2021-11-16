import cv2
import numpy as np
import _pickle as pickle
import camera

def nothing(x):
	pass

cap = camera.RealsenseCamera()

cv2.namedWindow('image')
cv2.namedWindow('tava')
cv2.namedWindow('mask')
cv2.moveWindow('mask', 400, 0)
try:
	with open('colors/colors.pkl', 'rb') as fh:
		colors_lookup = pickle.load(fh)
except:
	colors_lookup	= np.zeros(0x1000000, dtype=np.uint8)


cv2.createTrackbar('brush_size','image',3,10, nothing)
cv2.createTrackbar('noise','image',1,5, nothing)

mouse_x	= 0
mouse_y	= 0
brush_size	= 1
noise	= 1
p = 0
update_i	= 0

def change_color():
	global update_i, noise, brush_size, mouse_x, mouse_y
	update_i	-= 1
	ob			= yuv[max(0, mouse_y-brush_size):min(cap.height, mouse_y+brush_size+1),
					max(0, mouse_x-brush_size):min(cap.width, mouse_x+brush_size+1),:].reshape((-1,3)).astype('int32')
	noises		= range(-noise, noise+1)
	for y in noises:
		for u in noises:
			for v in noises:
				colors_lookup[((ob[:,0]+y) + (ob[:,1]+u) * 0x100 + (ob[:,2]+v) * 0x10000).clip(0,0xffffff)]	= p

# mouse callback function
def choose_color(event,x,y,flags,param):
	global update_i, noise, brush_size, mouse_x, mouse_y
	if event == cv2.EVENT_LBUTTONDOWN:
		print("click...")
		mouse_x	= x
		mouse_y	= y
		brush_size	= cv2.getTrackbarPos('brush_size','image')
		noise		= cv2.getTrackbarPos('noise','image')
		update_i	= 60
		change_color()

cv2.namedWindow('tava')
cv2.setMouseCallback('tava', choose_color)
cv2.setMouseCallback('mask', choose_color)

print("V2ljumiseks vajutada t2hte 'q', v22rtuste salvestamiseks 's', v22rtuste kustutamiseks 'e'")
print("Palli confimiseks 'r', kollane='y', sinine='b', roheline='g', valge='w', tumeroheline='d', muu='o'")

i 	= 0

cap.open()
while(True):
	
	# Capture frame-by-frame
	#_, yuv = cap.read()
	# 
	yuv, depth_frame = cap.get_frames()
	
	if update_i > 0:
		change_color()

	i	+= 1
	if i % 5 == 0:# Display the resulting frame
		i	= 0

		#bgr = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_I420)

		cv2.imshow('tava', yuv)
		
		fragmented	= colors_lookup[yuv[:,:,0] + yuv[:,:,1] * 0x100 + yuv[:,:,2] * 0x10000]
		frame = np.zeros((cap.height, cap.width, 3), dtype=np.uint8)
		frame[fragmented == 1] = np.array([0, 255, 0], dtype=np.uint8)#balls - green
		frame[fragmented == 2] = np.array([255, 0, 255], dtype=np.uint8)#magenta basket
		frame[fragmented == 3] = np.array([255, 0, 0], dtype=np.uint8)#blue basket
		frame[fragmented == 4] = np.array([0, 69, 255], dtype=np.uint8)#field
		frame[fragmented == 5] = np.array([255, 255, 255], dtype=np.uint8)#white
		frame[fragmented == 6] = np.array([255, 255, 0], dtype=np.uint8)#dark green
		cv2.imshow('mask', frame)
	
	k = cv2.waitKey(1) & 0xff

	if k == ord('q'):
		break
	elif k == ord('g'):
		print('green balls')
		p = 1
	elif k == ord('m'):
		print('magenta gate')
		p = 2
	elif k == ord('b'):
		print('blue gate')
		p = 3
	elif k == ord('o'):
		print('orange')
		p = 4
	elif k == ord('w'):
		print('white')
		p = 5
	elif k == ord('d'):
		print('dark green')
		p = 6
	elif k == ord('b'):
		print('everything else')
		p = 0
	elif k == ord('s'):
		with open('colors/colors.pkl', 'wb') as fh:
			pickle.dump(colors_lookup, fh, -1)
		print('saved')
	elif k == ord('e'):
		print('erased')
		colors_lookup[colors_lookup == p]	= 0
# When everything done, release the capture

cap.close()

cv2.destroyAllWindows()
