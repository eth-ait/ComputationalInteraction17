import pyglet
from pyglet.gl import *

from fader import Fader
import numpy as np
import time, os
import spline
import geometry
import colorsys
import itertools

from tracker import Tracker

WIDTH = 800
HEIGHT = 800
SEQUENCES_FILE = 'sequences.dat'

class TriPhaseSequence:
    def __init__(self, tris):
        self.states = tris
        self.state = 0
        self.time_in_state = 0
        self.timeout = 0.5
        self.trigger = 0.0
        self.active = 0.0
        self.color = colorsys.hsv_to_rgb(np.random.random(), 0.9, 0.5)
        self.last = (0,0)
            
    def update_none(self, dt):
        self.time_in_state += dt        
        if self.time_in_state > self.timeout:
            self.state = 0
            self.time_in_state  = 0    

    def reset(self):
        self.state = 0
        self.time_in_state  = 0
        self.trigger = 0.0
        
    def update(self, x, y, dt):
    
        new = (x,y)
        old = self.last
        self.last = new
        if self.state>=len(self.states):
            self.reset()
            self.active = 1.0
            return True
        
        self.trigger = 0.99 * self.trigger
        self.active = 0.995 * self.active
        for i in range(20):
            j = i/20.0
            x = j*new[0]+(1-j)*old[0]
            y = j*new[1]+(1-j)*old[1]
            
            s = self.states[self.state]
                                 
            if geometry.inside_triangle((x,y), s):
                self.state = self.state + 1
                self.time_in_state = 0 
                self.trigger = 1.0
          
            if self.state>=len(self.states):
                self.reset()
                self.active = 1.0          
                return True
                
        self.time_in_state += dt
                
        if self.time_in_state > self.timeout:
            self.reset()           
        return False
        
                            
class Phaser(pyglet.window.Window):

    MODE_NORMAL     = 0
    MODE_TRACING    = 1
    MODE_CREATING   = 2

    def __init__(self):
        super(Phaser, self).__init__(WIDTH, HEIGHT) # config=pyglet.gl.Config(sample_buffers=1, samples=2))
        self.xdim = WIDTH
        self.ydim = HEIGHT
        self.load_fonts()
        
        self.gesture_sound = pyglet.media.StaticSource(pyglet.resource.media('gesture.wav'))

        # add the faders
        self.faders = []   
        self.title_fader = Fader(0.1, 0.9)
        self.faders.append(self.title_fader)
                               
        self.mouse = (0, 0)
        self.title_image = pyglet.font.Text(self.fonts[40], 'PhaseSeq')
        self.mode_image = pyglet.font.Text(self.fonts[30], 'Trace mode')
        self.show_saved_image = pyglet.font.Text(self.fonts[20], 'Showing saved traces')
        self.create_image = pyglet.font.Text(self.fonts[30], 'Creating classifier')
        self.showinst_image = pyglet.font.Text(self.fonts[20], 'Press H to toggle instructions')

        instructions =  'To create a classifier:\n'
        instructions += '- Right click to begin\n'
        instructions += '- Left click to place first path segment\n'
        instructions += '- Left click again to extend path\n'
        instructions += '- Optionally use <A> and <D> to change width\n'
        instructions += '- Repeat until path complete\n'
        instructions += '- Right click to save\n'
        instructions += '(Press <U> to undo last point while drawing)\n\n'
        instructions += 'To preserve traces on screen:\n'
        instructions += '- Hold <Shift> and perform a movement\n'
        instructions += '- Release <Shift> to stop recording\n'
        instructions += '- Perform these steps as many times as needed\n'
        instructions += '- Press <T> to toggle showing all stored recordings\n'
        instructions += '- Press <X> to clear all stored recordings\n'
        instructions += '\nOther keybindings:\n'
        instructions += '<C> clears all saved classifiers\n'
        instructions += '<L> loads saved classifiers from file\n'
        instructions += '<S> saves current set of classifiers to file\n'
        self.inst_label = pyglet.text.Label(instructions, font_size=16, x=self.width/2, y=self.height-100, anchor_x='center',  multiline=True, width=self.width*0.75)

        self.phase_trace = []
        self.trace_len = 150
        
        self.sequences = []
        self.active_sequence = None
        self.saved_traces = []
        self.show_saved_traces = False
        
        self.extents = [-0.05,1.1,-0.6,0.6]
        self.thickness = 0.07
        
        self.tracker = Tracker(WIDTH, HEIGHT)     

        self.mode = Phaser.MODE_NORMAL
        self.show_instructions = False

        self.import_sequences()

    def start_sequence(self):
        self.active_sequence = []
        
    def end_sequence(self):
        if len(self.active_sequence)>1:
            self.sequences.append(TriPhaseSequence(self.make_path(self.active_sequence, self.thickness)))
        self.active_sequence = None
        
    def import_sequences(self):
        if not os.path.exists(SEQUENCES_FILE):
            print('No existing sequences file found!')
            return

        self.sequences = []
        self.active_sequence = None

        with open(SEQUENCES_FILE, 'r') as f:
            seq_data = f.readlines()
        
        for sd in seq_data:
            points = []
            sd = sd.split(',')
            for i in range(0, len(sd), 6):
                t = map(float, sd[i:i+6])
                points.append(((t[0], t[1]), (t[2], t[3]), (t[4], t[5])))
            self.sequences.append(TriPhaseSequence(points))

        print('Imported %d sequences' % (len(self.sequences)))

    def export_sequences(self):
        if len(self.sequences) == 0:
            print('No sequences to export')
            return

        print('Exporting %d sequences to %s' % (len(self.sequences), SEQUENCES_FILE))
        with open(SEQUENCES_FILE, 'w') as f:
            for j, s in enumerate(self.sequences):
                points = list(itertools.chain.from_iterable(s.states))
                for i, p in enumerate(points):
                    f.write('%f,%f' % p)
                    if i < len(points) - 1:
                        f.write(',')
                    else:
                        if j < len(self.sequences) - 1:
                            f.write('\n')
                print('Sequence exported (%d points)' % (len(points) / 3))

    def load_fonts(self):
        # load fonts
        self.fonts = {}
        pyglet.font.add_file("rez.ttf")
        for i in range(6,41):
            self.fonts[i] = pyglet.font.load('Rez', i)

    def start(self):
        pyglet.clock.schedule_interval(self.update, 1/60.0)
        pyglet.app.run()
        self.export_sequences()
          
    def update(self, dt):            
        """Frame update"""
        # update the faders, so they fade in and out
        for fader in self.faders:
            fader.update(dt)            
                         
        self.tracker.update(pos=self.mouse)            

        n = len(self.tracker.the_object.d_seq)
        for d in self.tracker.the_object.d_seq:
            state = (d[0,0],-d[0,1]*4)
            self.phase_trace.append(state)

            if self.mode == Phaser.MODE_NORMAL:
                for i,seq in enumerate(self.sequences):
                    seq.update(state[0], state[1], dt/n)
                
                    if seq.active == 1.0:
                        self.gesture_sound.play()
                        self.title_image = pyglet.font.Text(self.fonts[40], 'Gesture %d' % i)
                        self.title_fader.reset()
            
        if self.mode != Phaser.MODE_TRACING and len(self.phase_trace) > self.trace_len:
            self.phase_trace = self.phase_trace[len(self.phase_trace) - self.trace_len:]

        self.draw()

    def draw_axes(self):
        w = 0.8 * self.extents[1]
        y1 = 0.7 * self.extents[2]
        y2 = 0.7 * self.extents[3]

        glLineWidth(3.0)
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        if self.mode == Phaser.MODE_TRACING:
            glColor4f(0.2, 0.9, 0.5 ,0.3)
        else:
            glColor4f(0.2, 0.5, 0.9 ,0.3)

        glBegin(GL_LINES)
        glVertex2f(0,y1)
        glVertex2f(0, y2)
        glVertex2f(0,0)
        glVertex2f(w,0)        
        glEnd()
        
        if self.mode == Phaser.MODE_TRACING:
            glColor4f(0.2, 0.9, 0.6, 0.1)
            glBegin(GL_QUADS)
            glVertex2f(0,0)
            glColor4f(0.2, 0.9, 0.6, 0.0)
            glVertex2f(0, y1)
            glVertex2f(w, y1)
            glColor4f(0.2, 0.9, 0.6, 0.1)
            glVertex2f(w,0)        
        else:
            glColor4f(0.2, 0.6, 0.9, 0.1)
            glBegin(GL_QUADS)
            glVertex2f(0,0)
            glColor4f(0.2, 0.6, 0.9, 0.0)
            glVertex2f(0, y1)
            glVertex2f(w, y1)
            glColor4f(0.2, 0.6, 0.9, 0.1)
            glVertex2f(w,0)        
        glEnd()
        
        if self.mode == Phaser.MODE_TRACING:
            glColor4f(0.2, 0.9, 0.5, 0.4)
        else: 
            glColor4f(0.2, 0.5, 0.9, 0.4)

        n = 10
        for i in range(n):
            x = w * ((i+1)/float(n))
            glBegin(GL_LINES)
            glVertex2f(x, -0.01)
            glVertex2f(x, 0.01)
            glEnd()

        glLineWidth(1.0)
        
    def draw_trace(self):
       glBlendFunc(GL_SRC_ALPHA, GL_ONE)
       k = 1.0
       glLineWidth(3.0)
       glBegin(GL_LINE_STRIP)
       for vertex in reversed(self.phase_trace):
            if vertex:
                glColor4f(0.9,0.7,0.7,k)
                glVertex2f(vertex[0], vertex[1])
                if self.mode != Phaser.MODE_TRACING:
                    k = k * 0.95 #0.9
       glEnd()
       glLineWidth(1.0)

    def draw_tri(self, tri, color, phase=0):
        alpha =  color[3]
        
        glColor4f(color[0], color[1], color[2], alpha)#/2.0)
        glBegin(GL_TRIANGLES)
        glVertex2f(*tri[0])
        glVertex2f(*tri[1])
        glVertex2f(*tri[2])        
        glEnd()
        
        # glBegin(GL_LINE_LOOP)
        
        # glColor4f(color[0], color[1], color[2], alpha)
        # glVertex2f(*tri[0])                
        # glVertex2f(*tri[1])        
        # glVertex2f(*tri[2])        
        # glEnd()

    def draw_saved_traces(self):
        if not self.show_saved_traces:
            return

        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glLineWidth(3.0)
        colours = [ [0.9, 0.2, 0.2, 0.8], [0.2, 0.9, 0.2, 0.8], [0.2, 0.2, 0.9, 0.8] ]
        for i, st in enumerate(self.saved_traces):
            glBegin(GL_LINE_STRIP)
            glColor4f(*colours[i%3])
            for j, vertex in enumerate(st):
                glVertex2f(vertex[0], vertex[1])
            glEnd()
        glLineWidth(1.0)
        
    def draw_sequences(self):
        for sequence in self.sequences:            
            for i,elt in enumerate(sequence.states):
                if sequence.active>0.1:
                    self.draw_tri(elt, (1,1,1, sequence.active))
                else:
                    if i == sequence.state:
                        self.draw_tri(elt, (0.6, 0.9, 0.6, sequence.trigger+0.1))
                    else:
                        self.draw_tri(elt, (0.6, 0.9, 0.6, 0.25), phase=i)
                                            
        if self.active_sequence:
            self.draw_thick_line(self.active_sequence)
             
    def make_path(self, seq, thickness):
        """Convert a linear sequence to a set of triangles"""
        last = None
        last_l = None
        tris = []
        
        #if len(seq)>2:            
        #    spl = spline.CardinalSpline(seq, tension=0.2)
        #    seq = [spl(x/3.0) for x in range(3*(len(seq)-1))]
        
        for pt in seq:
            if last:
                normal = geometry.normal(last, pt)
                strut = geometry.mul(normal, thickness)
                if not last_l:
                    last_r = (geometry.sub(strut, last))
                    last_l = (geometry.add(strut, last))                
                                
                tris.append((geometry.add(strut, pt), last_r, last_l))
                tris.append((geometry.add(strut, pt), geometry.sub(strut, pt), last_r))
                last_l = geometry.add(strut, pt)
                last_r = geometry.sub(strut, pt)
            
            last = pt
        return tris
        
    def draw_thick_line(self, seq):
        glColor4f(0.3,0.8,0.2, 0.5)

        if len(seq) == 1:            
            glPointSize(4.0)
            glBegin(GL_POINTS)
            glVertex2f(*seq[0])
            glEnd()
            return
        
        tris = self.make_path(seq, self.thickness)       
        
        for tri in tris:            
            glBegin(GL_LINE_LOOP)
            for vertex in tri:           
                glVertex2f(*vertex)            
            glEnd()
            
    def draw_tracing_background(self):
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glBegin(GL_QUADS)
        glColor4f(0.33, 0.85, 0.26, 0.3)
        glVertex2f(0,0)
        glColor4f(0.33, 0.85, 0.26, 0.3)
        glVertex2f(self.width, 0)
        glColor4f(0.55, 0.85, 0.46, 0.3)
        glVertex2f(self.width, self.height)
        glColor4f(0.55, 0.85, 0.46, 0.3)
        glVertex2f(0, self.height)        
        glEnd()

    def draw_background(self):
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glBegin(GL_QUADS)
        glColor4f(0.02,0.04,0.12,1)        
        glVertex2f(0,0)
        glColor4f(0.02,0.04,0.12,1)        
        glVertex2f(self.width, 0)
        glColor4f(0.03,0.07,0.22,1)        
        glVertex2f(self.width, self.height)
        glColor4f(0.13,0.07,0.22,1)        
        glVertex2f(0, self.height)        
        glEnd()

    def draw(self):        
        """Draw the entire screen"""   
        glClearColor(0.02,0.04,0.12,1)        
        
        self.last_frame_time = time.clock()
        self.clear()        
        if self.mode == Phaser.MODE_TRACING:
            self.draw_tracing_background()
        else:
            self.draw_background()

        glLoadIdentity()          

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(self.extents[0],self.extents[1],self.extents[2], self.extents[3],-1,1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        self.draw_axes()
        self.draw_trace()
        self.draw_saved_traces()
        self.draw_sequences()
        
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self.draw_title()
        self.draw_mode()
        self.draw_instructions()
        
    def on_key_press(self, symbol, modifiers):
        if self.mode == Phaser.MODE_NORMAL and symbol == pyglet.window.key.LSHIFT or symbol == pyglet.window.key.RSHIFT:
            self.mode = Phaser.MODE_TRACING
            self.phase_trace = []
        pyglet.window.Window.on_key_press(self, symbol, modifiers)

    def on_key_release(self, symbol, modifiers):  
        if symbol == pyglet.window.key.C:
            print('Clearing sequences')
            self.sequences = []
            self.active_sequence = None
            if os.path.exists(SEQUENCES_FILE):
                os.unlink(SEQUENCES_FILE)
        elif symbol == pyglet.window.key.A:
            self.thickness -= 0.01
            print('thickness =', self.thickness)
        elif symbol == pyglet.window.key.D:
            self.thickness += 0.01
            print('thickness =', self.thickness)
        elif self.mode == Phaser.MODE_TRACING and symbol == pyglet.window.key.LSHIFT or symbol == pyglet.window.key.RSHIFT:
            self.mode = Phaser.MODE_NORMAL
            self.saved_traces.append(self.phase_trace)
            self.phase_trace = []
        elif symbol == pyglet.window.key.S:
            self.export_sequences()
        elif symbol == pyglet.window.key.L:
            self.import_sequences()
        elif symbol == pyglet.window.key.H:
            self.show_instructions = not self.show_instructions
        elif symbol == pyglet.window.key.U:
            if self.mode == Phaser.MODE_CREATING:
                if len(self.active_sequence) > 1:
                    self.active_sequence = self.active_sequence[:-1]
                else:
                    self.end_sequence()
                    self.mode = Phaser.MODE_NORMAL

        elif symbol == pyglet.window.key.X:
            self.saved_traces = []
            print('cleared saved traces')
        elif symbol == pyglet.window.key.T:
            self.show_saved_traces = not self.show_saved_traces

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse = (x, y)
    
    def new_state(self,x,y):
        x = x / float(self.width)
        y = y / float(self.height)
        rx = (1-x)*self.extents[0] + (x)*self.extents[1]
        ry = (1-y)*self.extents[2] + (y)*self.extents[3]
        self.active_sequence.append((rx, ry))
        
    def on_mouse_release(self, x, y, button, modifiers):
        self.mouse = (x, y)

        # left mouse click adds new segment to current sequence
        if button == pyglet.window.mouse.LEFT and self.active_sequence != None:
            self.new_state(x,y)
            return

        # right mouse ends an active sequence...
        if (button == pyglet.window.mouse.RIGHT \
                or (button == pyglet.window.mouse.LEFT and modifiers & 2)) \
                and self.active_sequence != None:
            self.end_sequence()
            self.mode = Phaser.MODE_NORMAL
            return

        # ...or starts a new one
        if (button == pyglet.window.mouse.RIGHT \
                or (button == pyglet.window.mouse.LEFT and modifiers & 2)) \
                and self.active_sequence == None:
            self.start_sequence()
            self.mode = Phaser.MODE_CREATING
            self.new_state(x, y)
            return

    def draw_instructions(self):
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)            
        self.showinst_image.x = 10
        self.showinst_image.y = 30
        self.showinst_image.halign = 'left'
        self.showinst_image.valign = 'center'
        self.showinst_image.color = (1,1,1,1)
        self.showinst_image.draw()
        if self.show_instructions:
            self.inst_label.draw()

    def draw_mode(self):
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)            
        if self.mode == Phaser.MODE_TRACING:
            self.mode_image.x = self.width/2
            self.mode_image.y = self.height - 40
            self.mode_image.halign = "center"
            self.mode_image.valign = "center"
            self.mode_image.color = (1,1,1, 1)
            self.mode_image.draw()
        elif self.mode == Phaser.MODE_CREATING:
            self.create_image.x = self.width/2
            self.create_image.y = self.height - 40
            self.create_image.halign = "center"
            self.create_image.valign = "center"
            self.create_image.color = (1,1,1, 1)
            self.create_image.draw()
        
        if self.show_saved_traces:
            self.show_saved_image.x = self.width - 10
            self.show_saved_image.y = 30
            self.show_saved_image.halign = 'right'
            self.show_saved_image.valign = 'center'
            self.show_saved_image.color = (1,1,1,1)
            self.show_saved_image.draw()

    def draw_title(self):
        """Draw the title, fading in and out"""        
        k = self.title_fader.get()                
        if k>1e-3:
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)            
            self.title_image.x = self.width/2 
            self.title_image.y = self.height/2
            self.title_image.halign = "center"
            self.title_image.valign = "center"
            self.title_image.color = (1,1,1, k)
            self.title_image.draw()
    
if __name__ == "__main__":
    sd = Phaser()
    sd.start()


  
         
