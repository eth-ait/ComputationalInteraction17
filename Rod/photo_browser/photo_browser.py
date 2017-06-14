from __future__ import division
import os, sys, socket, struct
import numpy as np

import sounddevice as sd
import soundfile as sf


import pyglet
from pyglet.gl import *

from PIL import Image

# screen width, pixels
SCREEN_WIDTH = 1200
# screen height, pixels
SCREEN_HEIGHT = 568
# file extensions to load as photos
IMAGE_FILES = [ 'jpg', 'png' ]
# limit on number of photos to load
MAX_IMAGES = 50
# toggle rescaling on/off
RESCALE_IMAGES = True
# rescale images that are taller than this value to fit
MAX_IMAGE_DIM = 450
# framerate for the pyglet window
FPS = 60
# horizontal gap between successive photos, pixels
SPACING = 70
# port to listen for incoming UDP data
LISTEN_PORT = 12333
# default location for photos
DEFAULT_PHOTO_DIR = 'photos'

# control modes
MODE_MOUSE                  = 0
MODE_MOUSE_FLIPPED          = 1
MODE_NETWORK                = 2
MODE_MOUSE_VELOCITY         = 3
MODE_MOUSE_ACC              = 4
MODE_MOUSE_STICKY           = 5
MODE_MIC                    = 6

MODE_NAMES = \
        { 
            MODE_MOUSE: 'Simple mouse', 
            MODE_MOUSE_FLIPPED: 'Simple mouse (flipped)',
            MODE_MOUSE_VELOCITY: 'Mouse velocity',
            MODE_MOUSE_ACC: 'Mouse acceleration',
            MODE_NETWORK: 'Network control',
            MODE_MOUSE_STICKY: 'Control with sticky targets',
            MODE_MIC: 'Control with audio input',
        }

# represents a single photo in the browser
class Photo(object):
    def __init__(self, path):
        self.path = path
        self.name = os.path.split(path)[1]
        self.image = None
        self.x = np.zeros((3,1))
        self.offset = 0

    def load(self):
        self.image = pyglet.image.load(self.path)

    # given the window height, blit the image to the window at the 
    # currently set x-position 
    def blit(self, window_height):
        if self.image:
            self.image.blit(self.x, (window_height - self.image.height) / 2)

    # given the window height, blit the image to the window at the 
    # currently set x-position and offset
    def blit_offset(self, window_height):
        if self.image:
            self.image.blit(self.x + self.offset, (window_height - self.image.height) / 2)

class PhotoBrowser(pyglet.window.Window):
    def __init__(self, photo_dir):

        # create the pyglet window
        super(PhotoBrowser, self).__init__(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.set_caption('PhotoBrowser window')
        self.mode_label = pyglet.text.Label('Mode: ', font_name='Lucida Sans Mono', font_size=16, x=10, y=self.height-10, anchor_x='left', anchor_y='top')

        self.photo_path = photo_dir
        self.photo_list = []
        self.total_photo_width = 0
        self.x = np.transpose(np.array([[0, 0, 0.5]])) # state vector [a, v, x]
        self.input_pos = 0.5
        self.mode = MODE_MOUSE_VELOCITY
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.bind(('', LISTEN_PORT))
        self.sock.setblocking(0)
        self.lastSound = 0.5
        
        
    def audio_callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""       
        if status:
            print(status)
        if any(indata) and self.mode == MODE_MIC:
            magnitude = np.abs(np.fft.rfft(indata[:, 0], n=fftsize))
            magnitude *= audiogain / fftsize
            self.lastSound = np.mean(magnitude*range(1,len(magnitude)+1))
            print(self.lastSound)
        else:
            print('no input')
            
        # Fancy indexing with mapping creates a (necessary!) copy:
        #queue.put(indata[::downsample, mapping])


    def run(self):
        self.photo_list = self.load_photos(self.photo_path)
        if len(self.photo_list) == 0:
            print('Failed to load any photos!')
            sys.exit(-1)

        pos = -self.total_photo_width / 2
        for i, photo in enumerate(self.photo_list):
            pos += photo.image.width + 50
            photo.x = pos
        
        pyglet.clock.schedule_interval(self.update, 1.0/FPS)
        pyglet.app.run()
        self.sock.close()

    def update(self, dt):

        # update view position (view_pos) based on selected control method.
        # dt is elapsed time since last call to update()
        # view_pos should be set to a value between 0 (far left) and 1 (far right)
        if self.mode == MODE_MOUSE:
            self.x[2,0] = self.input_pos
        elif self.mode == MODE_MOUSE_FLIPPED:
            self.x[2,0] = 1.0 - self.input_pos
        elif self.mode == MODE_MOUSE_VELOCITY:
            gain = 2/FPS
            A = np.array([[0, 0, 0], [0, 1-0.97/FPS, 0], [0, 1/FPS, 1]])   # state transition matrix
            B = np.transpose(np.array([[0, gain, 0]]))  # control input matrix
            u = np.array([[0.5-self.input_pos]])
            
            # create a dead zone around the centre
            dead_zone = 0.05;
            if abs(u[0][0]) < dead_zone:
                u = 0.0
        
            self.x = np.dot(A,self.x) + np.dot(B,u)
            
            # limit position if at edge
            if self.x[2,0] > 1.0 or self.x[2,0] < 0.0:
               self.x[2,0] = max(min(self.x[2,0],1.0),0.0)
               self.x[1,0] = 0.0;
        elif self.mode == MODE_MOUSE_ACC:
            gain = 0.5/FPS
            A = np.array([[1, 0, 0], [1/FPS, 1-0.97/FPS, 0], [0, 1/FPS, 1]])   # state transition matrix
            B = np.transpose(np.array([[gain, 0, 0]]))  # control input matrix
            u = np.array([[0.5-self.input_pos]])
            
            # create a dead zone around the centre
            dead_zone = 0.05;
            if abs(u[0][0]) < dead_zone:
                u = 0.0
            else:
                u = u-np.copysign(dead_zone,u)
        
            self.x = np.dot(A,self.x) + np.dot(B,u)
            
            # limit position if at edge
            if self.x[2,0] > 1.0 or self.x[2,0] < 0.0:
               self.x[2,0] = max(min(self.x[2,0],1.0),0.0)
               self.x[1,0] = 0.0;
        elif self.mode ==  MODE_MOUSE_STICKY:
            gain = 2/FPS
            A = np.array([[0, 0, 0], [0, 1-0.97/FPS, 0], [0, 1/FPS, 1]])   # state transition matrix
            B = np.transpose(np.array([[0, 0, gain]]))  # control input matrix
            u = np.array([[0.5-self.input_pos]])
            
            # create a dead zone around the centre
            dead_zone = 0.05;
            if abs(u[0][0]) < dead_zone:
                u = 0.0
            else:
                u = u-np.copysign(dead_zone,u)
    
            thisu = u
            L=1.0
            for i, photo in enumerate(self.photo_list):
                thisPhotoPos = (self.total_photo_width / 2 +50+photo.x+photo.image.width/2)/self.total_photo_width
                
                if np.abs(thisPhotoPos-self.x[2,0]) < (photo.image.width/2)/self.total_photo_width:
                #Ax +B(u+L(r-x))
                   thisu = u+L*(thisPhotoPos-self.x[2,0])
                   #print(thisu, u)
        
            self.x = np.dot(A,self.x) + np.dot(B,thisu)
            
            # limit position if at edge
            if self.x[2,0] > 1.0 or self.x[2,0] < 0.0:
               self.x[2,0] = max(min(self.x[2,0],1.0),0.0)
               self.x[1,0] = 0.0;

               
        elif self.mode == MODE_NETWORK:
            try:
                netdata, addr = self.sock.recvfrom(10)
                self.x[2,0] = struct.unpack('f', netdata)[0]
                print('Net data: %f' % self.x[2,0])
            except socket.error:
                pass
        elif self.mode == MODE_MIC:
            gain = 0.5/FPS
            A = np.array([[0, 0, 0], [0,1-0.97/FPS, 0], [0, 1/FPS, 1]])   # state transition matrix
            B = np.transpose(np.array([[0, gain, 0]]))  # control input matrix
            u = np.array([[self.lastSound]])
    
            
            # create a dead zone around the centre
            dead_zone = 0.05;
            if abs(u[0][0]) < dead_zone:
                u = 0.0
            else:
                u = u-np.copysign(dead_zone,u)-0.2
        
            self.x = np.dot(A,self.x) + np.dot(B,u)
            
            # limit position if at edge
            if self.x[2,0] > 1.0 or self.x[2,0] < 0.0:
               self.x[2,0] = max(min(self.x[2,0],1.0),0.0)
               self.x[1,0] = 0.0;
        self.mode_label.text = 'Mode: %s (Enter to change)' % MODE_NAMES[self.mode]

        # update the offsets on each photo to simulate scrolling
        for i, photo in enumerate(self.photo_list):
            photo.offset = (self.total_photo_width * (0.5 - self.x[2,0]))

        self.on_draw()

    def load_photos(self, path):
        results = []

        # scan the selected directory for 
        for root, dirs, files in os.walk(path):
            for file in files:
                for imgtype in IMAGE_FILES:
                    if file.lower().endswith(imgtype):
                        results.append(Photo(os.path.join(root, file)))
                        break

        if len(results) > MAX_IMAGES:
            print('WARNING: too many images found, truncating list')
            results = results[:MAX_IMAGES]

        for i, photo in enumerate(results):
            print('> Loading: %s' % photo.path)
            photo.load()
            # check if image needs rescaled
            if RESCALE_IMAGES and photo.image.height > MAX_IMAGE_DIM:
                print('    Rescaling this image (%d > %d)' % (photo.image.height, MAX_IMAGE_DIM))
                # load with PIL, resize and save again
                im = Image.open(photo.path)
                ar = MAX_IMAGE_DIM / im.size[1]
                new_size = map(lambda x: int(x * ar), im.size)
                im = im.resize(new_size, Image.BILINEAR)
                im.save(photo.path)

                # reload the resized version
                photo.load()

            self.total_photo_width += photo.image.width + SPACING
        return results

    def on_draw(self):
        self.clear()
        self.mode_label.draw()

        # draw each photo at an offset depending on the current view_pos value
        for i, photo in enumerate(self.photo_list):
            photo.blit_offset(self.height)

        # draw a basic scroll bar below the photos 
        glColor4f(0.7, 0.7, 0.7, 1)
        glLineWidth(3)
        pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ('v2i', (100, 50, self.width - 100, 50)))
        glLineWidth(5)
        glColor4f(1.0, 1.0, 1.0, 1)
        pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ('v2f', (100 + (self.width - 200) * self.x[2,0], 40, 100 + (self.width - 200) * self.x[2,0], 60)))
        #glColor4f(1.0, 0.0, 0.0, 1) 
        pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ('v2f', (100 + (self.width - 200) * (0.5+self.x[1,0]), 40, 100 + (self.width - 200) * (0.5+self.x[1,0]), 60)))
 
    def on_mouse_motion(self, x, y, dx, dy):
        # coords relative to bottom left of window
        self.input_pos = (self.width - x) / self.width

    def on_key_release(self, symbol, modifiers):
        if symbol == pyglet.window.key.ENTER:
            self.mode += 1
            if self.mode >= len(MODE_NAMES):
                self.mode = 0




if __name__ == "__main__":
    photo_path = DEFAULT_PHOTO_DIR

    if len(sys.argv) != 2 and not os.path.exists(DEFAULT_PHOTO_DIR):
        print('Usage: simple_photo_browser.py <photo directory>')
        sys.exit(-1)
    
    if len(sys.argv) == 2:
        if not os.path.exists(sys.argv[1]):
            print('Invalid path: "%s"' % sys.argv[1])
            sys.exit(-1)
        
        photo_path = sys.argv[1]
        
        
       
    device = sd.default.device
    device_info = sd.query_devices(device, 'input')
    samplerate = device_info['default_samplerate']
    downsample = 10
    channels = [1] 
    mapping = [c - 1 for c in channels]  # Channel numbers start with 1
    window = 200
    interval = 30
    
    
    (low, high) = (100, 2000)
    columns = 5
    audiogain = 100.0
    delta_f = (high - low) / (columns - 1)
    fftsize = np.ceil(samplerate / delta_f).astype(int)
    low_bin = np.floor(low / delta_f)
    
    browser = PhotoBrowser(photo_path)
    stream = sd.InputStream(
        device=device, channels=max(channels),
        samplerate=samplerate, callback=browser.audio_callback)
        

    print('Will search for images in: "%s"' % photo_path)
    with stream:
       browser.run()
