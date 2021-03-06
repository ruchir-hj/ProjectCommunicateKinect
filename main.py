import math
import cv
import freenect
import frame_convert
import pyglet
import pyglet.image
import Image
import speechd
import os
import thread
import threading
import time


count = 0

class Converter(object):
    
    raw_depth_image = cv.CreateImage((640,480), 8, 1)
    thresh_depth_image = cv.CreateImage((640,480), 8, 1)
    contour_depth_image = cv.CreateImage((640,480), 8, 1)
    raw_video_image = cv.CreateImage((640,480), 8, 3)
    raw_masked_image = cv.CreateImage((640,480), 8, 3)

    def __init__(self):
        super(Converter, self).__init__()
        
    def get_data(self):
        self.raw_depth_image = frame_convert.pretty_depth_cv(freenect.sync_get_depth()[0])
        self.raw_video_image = frame_convert.video_cv(freenect.sync_get_video()[0])
        cv.Flip(self.raw_depth_image,None,-1)
        cv.Flip(self.raw_video_image,None,-1)

    def get_depth(self):
        width, height = cv.GetSize(self.raw_depth_image) 
        depth_image = pyglet.image.ImageData(width, height, "L", self.raw_depth_image.tostring())

        return depth_image
    
    def get_contour_image(self):
        cv.Not(self.raw_depth_image,self.raw_depth_image)
        cv.Threshold(self.raw_depth_image, self.thresh_depth_image, 128, 255, cv.CV_THRESH_BINARY)
        
        contour_depth_image = cv.CreateImage((640,480),8,1)

        cv.Dilate(self.thresh_depth_image,contour_depth_image, None, 18)
        cv.Erode(contour_depth_image,contour_depth_image, None, 10)
        return contour_depth_image

    def get_centers(self):        
        contour_depth_image = self.get_contour_image()
        storage = cv.CreateMemStorage(0)
        contour = cv.FindContours(contour_depth_image, storage, cv.CV_RETR_CCOMP, cv.CV_CHAIN_APPROX_SIMPLE)
        
        depth_points = []
        
        while contour:
            bound_rect = cv.BoundingRect(list(contour))
            contour = contour.h_next()

            pt1 = (bound_rect[0], bound_rect[1])
            pt2 = (bound_rect[0] + bound_rect[2], bound_rect[1] + bound_rect[3])
            points = []
            points.append(pt1)
            points.append(pt2)
            if len(points):
                depth_points.extend(reduce(lambda a, b: ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), points))
                
        return depth_points


    def get_video(self):
        width, height = cv.GetSize(self.raw_video_image) 
        video_image = pyglet.image.ImageData(width, height, "BGR", self.raw_video_image.tostring()) 
        return video_image
    
    def get_masked(self):
        contour_depth_image_bgr = cv.CreateImage((640,480), self.raw_video_image.depth, self.raw_video_image.nChannels)
        self.raw_masked_image = cv.CreateImage((640,480), self.raw_video_image.depth, self.raw_video_image.nChannels)
        #cv.Not(self.raw_depth_image,self.raw_depth_image)
        cv.CvtColor(self.raw_depth_image,contour_depth_image_bgr, cv.CV_GRAY2BGR)

        cv.And(self.raw_video_image,contour_depth_image_bgr,self.raw_masked_image)
        masked_image = pyglet.image.ImageData(640,480, "BGR", self.raw_masked_image.tostring()) 

        return masked_image
                

if __name__ == '__main__':
    cv.NamedWindow("Depth")

    converter = Converter()
    #os.system('espeak -v en "this is convertor" ')

    
    window = pyglet.window.Window()

    def speak_message():
        global count
        if (count == 200):
            os.system('espeak -v en+f4 "today we will play with apple" ')
           # count = count + 1
            time.sleep(1)
        elif (count == 510):
            os.system('espeak -v en+f4 "a for apple" ')
           # count = count + 1
            time.sleep(1)
        elif (count == 830):
            os.system('espeak -v en+f4 "apple is a fruit" ')
           # count = count + 1
            time.sleep(1)
        elif (count == 940):
            os.system('espeak -v en+f4 "Here comes the red apple" ')
           # count = count + 1
            time.sleep(1)
        elif (count == 1400):
            os.system('espeak -v en+f4 "Here comes the green apple" ')
           # count = count + 1
            time.sleep(1)
   
    
    def update_images(dt):
        global converter, depth, video, masked, centers
        converter.get_data()
        depth = converter.get_depth()
        centers = converter.get_centers()
        video = converter.get_video()
        masked = converter.get_masked()
        #os.system('espeak -v en "a for apple" ')

    pyglet.clock.schedule_interval(update_images, 1/30.0)
        
    update_images(0.0)
    ## os.system('espeak -v en "a for apple" ')
    ## time.sleep(1)
    ## os.system('espeak -v en "apple is a fruit" ')
    ## time.sleep(1)
    ## os.system('espeak -v en "a is first alphabet" ')
    ## time.sleep(1)
    ## os.system('espeak -v en "Now lets play with apple" ')
    ## time.sleep(1)
    
    #speech_output = speechd.Speaker('apple')
    #speech_output.speak('a for apple') 
    
    
#    if depth is not None:
#        depth_sprite = pyglet.sprite.Sprite(depth)

    if video is not None:
        video_sprite = pyglet.sprite.Sprite(video)

#    masked_sprite = pyglet.sprite.Sprite(masked)
    mike = pyglet.image.load("mike.jpg")
    mike.anchor_x = mike.width // 2
    mike.anchor_y = mike.height // 2

    mike_sprite = pyglet.sprite.Sprite(mike)

    mike1 = pyglet.image.load("apple.jpg")
    mike1.anchor_x = mike.width // 2
    mike1.anchor_y = mike.height // 2

    mike1_sprite = pyglet.sprite.Sprite(mike1)

    
    mike2 = pyglet.image.load("green_apple.jpg")
    mike2.anchor_x = mike.width // 2
    mike2.anchor_y = mike.height // 2

    mike2_sprite = pyglet.sprite.Sprite(mike2)


    start = True
    #os.system('espeak -v en "a for apple" ')
    @window.event
    #os.system('espeak -v en "a for apple" ')
    def on_draw():
        global depth, video, masked, centers, start, x, y, angle, dist
        global px, py, pa, ps
        global count
        
        window.width = 1280
        window.height = 960

        window.clear()
            
        video_sprite.image = video
        video_sprite.scale = 2
        video_sprite.draw()
        sx = sy = 0
        ease = 0.35
        if start:
            x = y = angle = dist = 0
            px = py = pa = ps = 0
            #os.system('espeak -v en "a for apple" ')
            start = False
        if len(centers) == 4:
            px = mike_sprite.x
            py = mike_sprite.y
            pa = mike_sprite.rotation
            ps = mike_sprite.scale
            for c in range(len(centers)):
                if c % 2 == 0:
		    sx += centers[c]
                else:
                    sy += centers[c]
            x = (sx/(len(centers)/2) * 2 - px) * ease + px
            y = (sy/(len(centers)/2) * 2 - py) * ease + py
            dx = centers[2] - centers[0]
            dy = centers[3] - centers[1]
            #os.system('espeak -v en "a for apple" ')
            if dx != 0:
                angle = math.atan((dy*1.0)/dx) / math.pi * -180
                #os.system('espeak -v en "a for apple" ')
            dist = math.sqrt(dx*dx+dy*dy)
        mike_sprite.x = x
        mike_sprite.y = y
        mike_sprite.rotation = (angle - pa) * ease + pa
        mike_sprite.scale = (dist/320*2 - ps) * ease + ps
        mike1_sprite.x = x-300
        mike1_sprite.y = y-300
        mike2_sprite.x = x + 300
        mike2_sprite.y = y + 300
        mike_sprite.draw()
        if (count > 950):
            mike1_sprite.draw()
        if (count > 1420):
            mike2_sprite.draw()
        #os.system('espeak -v en "a for apple" ')
        if (count < 1500):
            speak_message()
            count = count + 1
            
        
    pyglet.app.run()
    #thread.start_new_thread(os.system('espeak -v en "a for apple" '))
    #thread.start_new_thread(pyglet.app.run())
    
        
