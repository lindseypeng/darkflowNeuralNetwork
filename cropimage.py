# -*- coding: utf-8 -*-
"""
Created on Sun Feb  3 20:58:05 2019

@author: alinsi
"""


# -*- coding: utf-8 -*-
"""
Created on Sun Feb  3 20:58:05 2019

@author: alinsi
"""


import cv2 
import os
import argparse
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", required=True,help="path to input image")
ap.add_argument("-o", "--output", required=True,help="path to output annotations")
ap.add_argument("-s", "--start", required=True,help="start frame")
ap.add_argument("-e", "--end", required=True,help="end frame")
ap.add_argument("-c", "--crop", required=False,help="path to cropped image")

args = vars(ap.parse_args())
# 
## load the input image from disk
folderread = args["input"]
foldersave = args["output"]
start=int(args["start"])
end=int(args["end"])
crop=(args["crop"])
numoffiles=end-start+1

# initialize the list of reference points and boolean indicating
# whether cropping is being performed or not
refPt = []
cropping = False
########################################################
####MUST CROP FROM TOP LEFT TO BOTTOM RIGHT###
############################################
def click_and_crop(event, x, y, flags, param): 
    global refPt, cropping
    if event == cv2.EVENT_LBUTTONDOWN:
        refPt = [(x, y)]
        cropping = True
    elif event == cv2.EVENT_LBUTTONUP:
        refPt.append((x, y))
        cropping = False
		# draw a rectangle around the region of interest
        cv2.rectangle(image, refPt[0], refPt[1], (0, 255, 0), 2)
        cv2.imshow("image", image)
print("Crop from Top Left to Bottom Right, Press 'r' to refresh image, Press 'c' to crop, Press 'q' to go to next image or end")
rangenum=range(numoffiles)
placeread=folderread+"/{}.jpg"
particle_pose=0
particle_truncated=0
particle_difficult=0
for f in rangenum:
    index=0
    f2="{:01d}".format(f+start)
    filename=(placeread.format((f2)))
    filename2=str(f2)+".jpg"
    print("this is file" + filename)
    if os.path.exists(filename)==False:
        print ("file dosnt exist {}".format(f2))        
        continue##if file dosnt exit 
    else:    
        image = cv2.imread(filename)
        (h, w, d) = image.shape
        my_file=open(foldersave+"/{}.xml".format(f2),"w+")
        my_file.write("<annotation>\n\t<folder>{}</folder>\n\t<filename>{}</filename>\n\t<size>\n\t\t<width>{}</width>\n\t\t<height>{}</height>\n\t\t<depth>{}</depth>\n\t</size>\n\t<segmented>0</segmented>".format(folderread,filename2, w, h, d))
        clone = image.copy()
        cv2.namedWindow("image")
        cv2.setMouseCallback("image", click_and_crop)
        while True:##break loop by control c
            cv2.imshow("image", image)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("r"):
                image = clone.copy()
            elif key == ord("c"):
                if len(refPt) == 2:
                    xmin = refPt[0][0]
                    xmax = refPt[1][0]
                    ymin = refPt[0][1]
                    ymax = refPt[1][1]
                    if (ymax-ymin)>0 and (xmax-xmin)>0:
                        classification = input('Enter your classification name: ')
                        my_file.write("\n\t<object>\n\t\t<name>{}</name>\n\t\t<pose>{}</pose>\n\t\t<truncated>{}</truncated>\n\t\t<difficult>{}</difficult>\n\t\t<bndbox>\n\t\t\t<xmin>{}</xmin>\n\t\t\t<ymin>{}</ymin>\n\t\t\t<xmax>{}</xmax>\n\t\t\t<ymax>{}</ymax>\n\t\t</bndbox>\n\t</object>".format(classification, particle_pose, particle_truncated, particle_difficult, xmin, ymin, xmax, ymax))
                        roi = clone[refPt[0][1]:refPt[1][1], refPt[0][0]:refPt[1][0]]
                        index=index+1
                        cv2.imwrite(crop+'/frame{}index{}class{}.png'.format(f2,index,classification),roi)##optional if you want to save your cropped image
                    else:
                        print("cropping not done properly,press r to refresh")
#        		cv2.imshow("ROI", roi)##optional if you want to see your cropped image
#        		cv2.waitKey(0)
        	## keep looping until the 'q' key is pressed
            elif key == ord("q"):
                break
    my_file.write("\n</annotation>")
    my_file.close()
    

cv2.destroyAllWindows()
