import cv2
# from google.colab.patches import cv2_imshow # the cv2.imshow() function doesn't work properly on Colab, so we use this patch
import numpy as np
import time
import mediapipe as mp
import socket
# from google.colab.output import eval_js
# from base64 import b64decode, b64encode
# from IPython.display import display, Javascript, Image
# import PIL
# import io
# import html
import random
from ECE16Lib.Communication import Communication

comms = Communication("/dev/cu.ECE16",115200)
comms.setup()
comms.clear()
mpDraw = mp.solutions.drawing_utils
mpPose = mp.solutions.pose
pose = mpPose.Pose()
pose_coord = [[None,None],[None,None],[None,None],[None,None],[None,None],[None,None],[None,None],[None,None],[None,None],[None,None],[None,None],[None,None],[None,None],[None,None],[None,None],[None,None],[None,None],[None,None],[None,None],[None,None],[None,None],[None,None],[None,None],[None,None],[None,None],[None,None],[None,None],[None,None],[None,None],[None,None],[None,None],[None,None],[None,None]]
pose_coord = np.array(pose_coord)
vid = cv2.VideoCapture(0)
state = 0
board_coord = [None,None]

required_colors = [None,None,None,None]
current_limb = None
current_color = None
colors_list = ["Red","Blue","Green","Yellow"]
limbs_list = ["Left Hand", "Right Hand", "Left Leg", "Right Leg"]

def spinner():
  color = random.choice(colors_list)
  limb = random.choice(limbs_list)
  current_limb = limbs_list.index(limb)
  current_color = colors_list.index(color)
  return limb,color,current_limb,current_color

def get_num(limb):
  if limb == "Left Hand":
    return 15
  if limb == "Right Hand":
    return 16
  if limb == "Left Leg":
    return 31
  if limb == "Right Leg":
    return 32

"""
Number for each limb:
0 = left hand
1 = right hand
2 = left leg
3 = right leg

States:
-2 == starting the game/loading
0 == initial; board follows player, and player lifts both arms up to place board
1 == board now fixed in position; the first round of the game begins
2+ == different levels of the game; randomly chosen positions for hands and legs on the board
hold position for a certain amount of time to clear each level;
when game paused, store max level in a file outside the program to restore progress later on.
(but we still need state 0 so that the player can correctly position the board)
"""

def position_board(img,coord,h,w):
  hs = int(w/5)
  vs = int(h/5)
  img = cv2.ellipse(img,(coord[0],coord[1]+vs),(10,10),0,0,360,(80,80,240),-1)
  img = cv2.ellipse(img,(coord[0] + hs,coord[1]+vs),(10,10),0,0,360,(80,80,240),-1)
  img = cv2.ellipse(img,(coord[0] -hs ,coord[1]+vs),(10,10),0,0,360,(80,80,240),-1)
  img = cv2.ellipse(img,(coord[0] + 2*hs,coord[1]+vs),(10,10),0,0,360,(80,80,240),-1)

  img = cv2.ellipse(img,(coord[0],coord[1]+ int(0.5*vs)),(10,10),0,0,360,(227,146,41),-1)
  img = cv2.ellipse(img,(coord[0]+hs,coord[1] + int(0.5*vs)),(10,10),0,0,360,(227,146,41),-1)
  img = cv2.ellipse(img,(coord[0]-hs,coord[1] + int(0.5*vs)),(10,10),0,0,360,(227,146,41),-1)
  img = cv2.ellipse(img,(coord[0]+2*hs,coord[1] + int(0.5*vs)),(10,10),0,0,360,(227,146,41),-1)

  img = cv2.ellipse(img,(coord[0],coord[1]),(10,10),0,0,360,(25,189,25),-1)
  img = cv2.ellipse(img,(coord[0]+hs,coord[1]),(10,10),0,0,360,(25,189,25),-1)
  img = cv2.ellipse(img,(coord[0]-hs,coord[1]),(10,10),0,0,360,(25,189,25),-1)
  img = cv2.ellipse(img,(coord[0]+2*hs,coord[1]),(10,10),0,0,360,(25,189,25),-1)

  img = cv2.ellipse(img,(coord[0],coord[1]-int(0.5*vs)),(10,10),0,0,360,(0,230,255),-1)
  img = cv2.ellipse(img,(coord[0]+hs,coord[1]-int(0.5*vs)),(10,10),0,0,360,(0,230,255),-1)
  img = cv2.ellipse(img,(coord[0]-hs,coord[1]-int(0.5*vs)),(10,10),0,0,360,(0,230,255),-1)
  img = cv2.ellipse(img,(coord[0]+2*hs,coord[1]-int(0.5*vs)),(10,10),0,0,360,(0,230,255),-1)

  return img

def check_match(coord,h,w):
  hs = int(w/5)
  vs = int(h/5)
  match = [False,False,False,False]
  red = [[board_coord[0],board_coord[1]+vs],[board_coord[0] + hs,board_coord[1]+vs],[board_coord[0] -hs ,board_coord[1]+vs],[board_coord[0] + 2*hs,board_coord[1]+vs]]
  blue = [[board_coord[0],board_coord[1]+int(0.5*vs)],[board_coord[0] + hs,board_coord[1]+int(0.5*vs)],[board_coord[0] - hs ,board_coord[1]+int(0.5*vs)],[board_coord[0] + 2*hs,board_coord[1]+int(0.5*vs)]]
  green = [[board_coord[0],board_coord[1]],[board_coord[0] + hs,board_coord[1]],[board_coord[0] -hs ,board_coord[1]],[board_coord[0] + 2*hs,board_coord[1]]]
  yellow = [[board_coord[0],board_coord[1]-int(0.5*vs)],[board_coord[0] + hs,board_coord[1]-int(0.5*vs)],[board_coord[0] - hs ,board_coord[1]-int(0.5*vs)],[board_coord[0] + 2*hs,board_coord[1]-int(0.5*vs)]]

  for a in red:
    if np.linalg.norm([a[0] - coord[0],a[1]-coord[1]]) < 50:
      match[0] = True


  for a in blue:
    if np.linalg.norm([a[0] - coord[0],a[1]-coord[1]]) < 50:
      match[1] = True

  for a in green:
    if np.linalg.norm([a[0] - coord[0],a[1]-coord[1]]) < 50:
      match[2] = True

  for a in yellow:
    if np.linalg.norm([a[0] - coord[0],a[1]-coord[1]]) < 50:
      match[3] = True

  return match
  


limb = ''
color = ''
count = 0 
completed_level = False
other_limbs_correct = [False,False,False]
other = 0
current_limb_correct = False
num_prev_correct = 0
num_prev_required = 0
state = -2
count = 10
time_started = 0

while True:
    ret, img = vid.read()
    img = cv2.resize(img,None,fx=1.5,fy=1.5,interpolation=cv2.INTER_AREA)
    h,w,c = img.shape

    results = pose.process(img)
    mpDraw.draw_landmarks(img,results.pose_landmarks,mpPose.POSE_CONNECTIONS)
    if results.pose_landmarks is not None:    
        for id, lm in enumerate(results.pose_landmarks.landmark):
            h, w,c = img.shape
            cx, cy = int(lm.x*w), int(lm.y*h)
            pose_coord[id] = [cx,cy]
            #img = cv2.circle(img,(cx,cy),radius = 2,color = (0,255,0), thickness = -1)
    
    if(state == -2):
      img = cv2.putText(img,"Welcome to TwistAR!",(10,150), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),2,cv2.LINE_AA)
      img = cv2.putText(img,"Game Begins in...",(10,250), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),2,cv2.LINE_AA)
      img = cv2.putText(img,str(count),(10,350), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),2,cv2.LINE_AA)
      if(time.time() - time_started >= 1):
        count-=1
        time_started = time.time()
      
      if count == 0:
        state = 0
      
    
    elif (pose_coord[32][0] is not None) and (pose_coord[32][1] is not None):
       if(state == 0):
          img = position_board(img,pose_coord[32],h,w)
          img = cv2.putText(img,"MOVE AROUND",(10,50), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),2,cv2.LINE_AA)
          img = cv2.putText(img,"to position the board",(10,110), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),2,cv2.LINE_AA)
          img = cv2.putText(img,"and LIFT YOUR HANDS UP",(10,180), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),2,cv2.LINE_AA)
          img = cv2.putText(img,"to place the board",(10,250), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),2,cv2.LINE_AA)
          if((pose_coord[20][1] < pose_coord[4][1])and (pose_coord[19][1] < pose_coord[4][1])):
            state = 1
            board_coord = [pose_coord[32][0],pose_coord[32][1]]
            completed_level = True
       elif(state == -1):
         img = position_board(img,board_coord,h,w)
         img = cv2.putText(img,"GAME OVER!",(10,50), cv2.FONT_HERSHEY_SIMPLEX, 2,(255,255,255),2,cv2.LINE_AA)
         if((pose_coord[20][1] < pose_coord[4][1])and (pose_coord[19][1] < pose_coord[4][1])):
            time.sleep(5)
            state = 0
            board_coord = [pose_coord[32][0],pose_coord[32][1]]
            completed_level = True

       else:
         img = position_board(img,board_coord,h,w)
         if (completed_level):
          limb, color, current_limb, current_color = spinner()
          code = "!"
          if (limb == "Right Hand"):
              code += "RH"
          if (limb == "Left Hand"):
              code += "LH"
          if (limb == "Left Leg"):
              code += "LL"
          if (limb == "Right Leg"):
              code += "RL"
          code += color[0] + str(state)
          comms.send_message(code)
          required_colors[current_limb] = color
          completed_level = False
         img = cv2.rectangle(img,(10,10),(110,100),(190,190,190),thickness=cv2.FILLED)
         img = cv2.rectangle(img,(110,10),(220,100),(130,130,130),thickness=cv2.FILLED)
         img = cv2.rectangle(img,(220,10),(330,100),(100,100,100),thickness=cv2.FILLED)
         img = cv2.rectangle(img,(330,10),(440,100),(70,70,70),thickness=cv2.FILLED)
         if(limb == "Left Hand"):
          img = cv2.putText(img,"LH",(10,50), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),1,cv2.LINE_AA)
          if(color == "Red"):
            img = cv2.putText(img,color,(10,80), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,255),1,cv2.LINE_AA)
          elif(color == "Blue"):
            img = cv2.putText(img,color,(10,80), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,0,0),1,cv2.LINE_AA)
          elif(color == "Green"):
            img = cv2.putText(img,color,(10,80), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,255,0),1,cv2.LINE_AA)
          elif(color == "Yellow"):
            img = cv2.putText(img,color,(10,80), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,255,255),1,cv2.LINE_AA)
         if(limb == "Right Hand"):
          img = cv2.putText(img,"RH",(110,50), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),1,cv2.LINE_AA)
          if(color == "Red"):
            img = cv2.putText(img,color,(110,80), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,255),1,cv2.LINE_AA)
          elif(color == "Blue"):
            img = cv2.putText(img,color,(110,80), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,0,0),1,cv2.LINE_AA)
          elif(color == "Green"):
            img = cv2.putText(img,color,(110,80), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,255,0),1,cv2.LINE_AA)
          elif(color == "Yellow"):
            img = cv2.putText(img,color,(110,80), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,255,255),1,cv2.LINE_AA)
         if(limb == "Left Leg"):
          img = cv2.putText(img,"LL",(220,50), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),1,cv2.LINE_AA)
          if(color == "Red"):
            img = cv2.putText(img,color,(220,80), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,255),1,cv2.LINE_AA)
          elif(color == "Blue"):
            img = cv2.putText(img,color,(220,80), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,0,0),1,cv2.LINE_AA)
          elif(color == "Green"):
            img = cv2.putText(img,color,(220,80), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,255,0),1,cv2.LINE_AA)
          elif(color == "Yellow"):
            img = cv2.putText(img,color,(220,80), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,255,255),1,cv2.LINE_AA)
         if(limb == "Right Leg"):
          img = cv2.putText(img,"RL",(330,50), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),1,cv2.LINE_AA)
          if(color == "Red"):
            img = cv2.putText(img,color,(330,80), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,255),1,cv2.LINE_AA)
          elif(color == "Blue"):
            img = cv2.putText(img,color,(330,80), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,0,0),1,cv2.LINE_AA)
          elif(color == "Green"):
            img = cv2.putText(img,color,(330,80), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,255,0),1,cv2.LINE_AA)
          elif(color == "Yellow"):
            img = cv2.putText(img,color,(330,80), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,255,255),1,cv2.LINE_AA)
        
         img = cv2.putText(img,"Level " + str(state),(250,250), cv2.FONT_HERSHEY_SIMPLEX, 2,(255,255,255),2,cv2.LINE_AA)
         num_prev_correct = 0
         for i in range(0,4):
           
           if i == current_limb:
             pos = get_num(limb)
             matches_found = check_match([pose_coord[pos][0],pose_coord[pos][1]],h,w)
             if (matches_found[current_color] == True):
               current_limb_correct = True
          
           else:
             pos = get_num(limbs_list[i])
             matches_found = check_match([pose_coord[pos][0],pose_coord[pos][1]],h,w)
             if ((required_colors[i] is None) or (matches_found[colors_list.index(required_colors[i])] == True)):
               other_limbs_correct[other] = True
               num_prev_correct +=1
             else:
               other_limbs_correct[other] = False  

             other = (other + 1)%3
           
           limb1 = limbs_list[i]
           color1 = required_colors[i]
           if(color1 is not None):
             if(limb1 == "Left Hand"):
              img = cv2.putText(img,"LH",(10,50), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),1,cv2.LINE_AA)
              if(color1 == "Red"):
                img = cv2.putText(img,color1,(10,80), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,255),1,cv2.LINE_AA)
              elif(color1 == "Blue"):
                img = cv2.putText(img,color1,(10,80), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,0,0),1,cv2.LINE_AA)
              elif(color1 == "Green"):
                img = cv2.putText(img,color1,(10,80), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,255,0),1,cv2.LINE_AA)
              elif(color1 == "Yellow"):
                img = cv2.putText(img,color1,(10,80), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,255,255),1,cv2.LINE_AA)
             if(limb1 == "Right Hand"):
              img = cv2.putText(img,"RH",(110,50), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),1,cv2.LINE_AA)
              if(color1 == "Red"):
                img = cv2.putText(img,color1,(110,80), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,255),1,cv2.LINE_AA)
              elif(color1 == "Blue"):
                img = cv2.putText(img,color1,(110,80), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,0,0),1,cv2.LINE_AA)
              elif(color1 == "Green"):
                img = cv2.putText(img,color1,(110,80), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,255,0),1,cv2.LINE_AA)
              elif(color1 == "Yellow"):
                img = cv2.putText(img,color1,(110,80), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,255,255),1,cv2.LINE_AA)
             if(limb1 == "Left Leg"):
              img = cv2.putText(img,"LL",(220,50), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),1,cv2.LINE_AA)
              if(color1 == "Red"):
                img = cv2.putText(img,color1,(220,80), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,255),1,cv2.LINE_AA)
              elif(color1 == "Blue"):
                img = cv2.putText(img,color1,(220,80), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,0,0),1,cv2.LINE_AA)
              elif(color1 == "Green"):
                img = cv2.putText(img,color1,(220,80), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,255,0),1,cv2.LINE_AA)
              elif(color1 == "Yellow"):
                img = cv2.putText(img,color1,(220,80), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,255,255),1,cv2.LINE_AA)
             if(limb1 == "Right Leg"):
              img = cv2.putText(img,"RL",(330,50), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),1,cv2.LINE_AA)
              if(color1 == "Red"):
                img = cv2.putText(img,color1,(330,80), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,255),1,cv2.LINE_AA)
              elif(color1 == "Blue"):
                img = cv2.putText(img,color1,(330,80), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,0,0),1,cv2.LINE_AA)
              elif(color1 == "Green"):
                img = cv2.putText(img,color1,(330,80), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,255,0),1,cv2.LINE_AA)
              elif(color1 == "Yellow"):
                img = cv2.putText(img,color1,(330,80), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,255,255),1,cv2.LINE_AA)



         #if num_prev_correct < num_prev_required:
          # state = -1

          
         if ((other_limbs_correct == [True,True,True]) and (current_limb_correct == True)):
            completed_level = True
            current_limb_correct = False
            #required_colors[current_color] = color
            state+=1
            num_prev_required = 0
            for k in other_limbs_correct:
              if k == True:
                num_prev_required+=1


    else:
      img = cv2.putText(img,"STAND UP AND FACE THE CAMERA",(10,150), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),2,cv2.LINE_AA)
      img = cv2.putText(img,"SO THAT YOUR HANDS AND FEET",(10,250), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),2,cv2.LINE_AA)
      img = cv2.putText(img,"ARE CLEARLY VISIBLE",(10,350), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),2,cv2.LINE_AA)

    cv2.imshow("TwistAR",img)
    c = cv2.waitKey(1)
    if(c == 27):
        break

vid.release()
cv2.destroyAllWindows()
comms.close()