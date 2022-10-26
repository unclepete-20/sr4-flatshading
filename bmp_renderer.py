'''
@author Pedro Pablo Arriola Jimenez (20188)
@filename bmp_renderer.py
@description: BMP file renderer that works using concepts related
to framebuffers and low level code such as bytes.
'''

import struct
from Obj import Obj
from Vector import V3


# Functions that will be needed to create low level structures.
def char(c):
    # 1 byte character
    c = struct.pack('=c', c.encode('ascii'))
    return c

def word(w):
    # 2 bytes character
    w = struct.pack('=h', w)   
    return w  


def dword(dw):
    # 4 bytes character
    dw = struct.pack('=l', dw)   
    return dw  

def color_select(r, g, b):
   return bytes([b, g, r])

# Part of SR4: Flat Shading
def cross(v1, v2):
    return (
        v1.y * v2.z - v1.z * v2.y,
        v1.z * v2.x - v1.x * v2.z,
        v1.x * v2.y - v1.y * v2.x
    )

def bounding_box(A, B, C):
    coords = [(A.x, A.y),(B.x, B.y),(C.x, C.y)]

    xmin = 999999
    xmax = -999999
    ymin = 999999
    ymax = -999999

    for (x, y) in coords:
        if x < xmin:
            xmin = x
        if x > xmax:
            xmax = x
        if y < ymin:
            ymin = y
        if y > ymax:
            ymax = y
    return V3(xmin, ymin), V3(xmax, ymax)

def barycentric(A, B, C, P):
    
    cx, cy, cz = cross(
        V3(B.x - A.x, C.x - A.x, A.x - P.x),
        V3(B.y - A.y, C.y - A.y, A.y - P.y)
    )
    if cz == 0:
        return(-1, -1, -1)
    u = cx / cz
    v = cy / cz
    w = 1 - (u + v) 

    return (w, v, u)

# Class of type Render that will nest every function that will create a BMP file from scratch. 

class Render(object):
    def __init__(self):
        self.width = 0
        self.height = 0
        self.pixels = 0
        self.clearColor = color_select(0, 0, 0)
        self.viewport_x = 0 
        self.viewport_y = 0
        self.viewport_height = 0
        self.viewport_width = 0
        self.texture = None
        
        # Constants for BMP files
        self.FILE_SIZE = (54)
        self.PIXEL_COUNT = 3
        self.PLANE = 1
        self.BITS_PER_PIXEL = 24
        self.DIB_HEADER = 40
        
    '''
    --- SR1: POINTS
  
    '''      
    def glCreateWindow(self, width, height):
        self.width = width
        self.height = height
        
        self.framebuffer = [[self.clearColor for x in range(self.width)]
                       for y in range(self.height)]
        
        self.zBuffer = [
            [-9999 for x in range(self.width)]
            for y in range(self.height)
        ]
        
    def glViewPort(self, x, y, width, height):
        self.viewport_x = x
        self.viewport_y = y
        self.viewport_width = width
        self.viewport_height = height
    
    def glColor(self, r, g, b):
        self.clearColor = color_select(r, g, b)
    
    def glClearColor(self, r, g, b):
        self.clearColor = color_select(r, g, b)
        for x in range(self.viewport_x, self.viewport_x + self.viewport_width + 1):
            for y in range(self.viewport_y, self.viewport_y + self.viewport_height + 1):
                self.glPoint(x, y)
        
    def glVertex(self, x, y):
        if -1 <= x <= 1:
            if -1 <= y <= 1:
                pass
            else:
                y = 0
        else:
            x = 0
        self.pixel_X = int((x + 1) * self.viewport_width * 1/2 ) + self.viewport_x
        self.pixel_Y = int((y + 1) * self.viewport_height * 1/2) + self.viewport_y
        self.glPoint(self.pixel_X,self.pixel_Y)
        
    def glClear(self):
        for x in range(self.viewport_x, self.viewport_x + self.viewport_width + 1):
            for y in range(self.viewport_y, self.viewport_y + self.viewport_height + 1):
                self.glPoint(x, y)
        
    def glPoint(self, x, y):
        if(0 < x < self.width and 0 < y < self.height):
            self.framebuffer[y][x] = self.clearColor
    
    
    
        
    '''
    --- SR2: LINES
    
    '''
    
    # Line drawing function which implements Bresenham's algorithm
    def glLine(self, v1, v2):
        
        x0 = int((v1.x + 1) * self.viewport_width * 1/2 ) + self.viewport_x
        y0 = int((v1.y + 1) * self.viewport_height * 1/2) + self.viewport_y

        x1 = int((v2.x + 1) * self.viewport_width * 1/2 ) + self.viewport_x
        y1 = int((v2.y + 1) * self.viewport_height * 1/2) + self.viewport_y

        #realizar conversion
        dy = abs(y1 - y0)
        dx = abs(x1 - x0)

        steep = dy > dx

        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1

        if  x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0

        dy = abs(y1 - y0)
        dx = abs(x1 - x0)

        offset = 0
        
        threshold = dx
        
        y = y0

        for x in range(x0, x1 + 1):
            if steep:
                self.glPoint(y, x)
            else:
                self.glPoint(x, y)

            offset += dy * 2
            if offset >= threshold:
                y += 1 if y0 < y1 else -1
                threshold += dx * 2
        
        
    '''
    SR3: MODELS
    
    '''
    
    def transform_vertex(self, vertex, scale_factor, translate_factor):
        return V3(
            (vertex[0] * scale_factor[0]) + translate_factor[0], 
            (vertex[1] * scale_factor[1]) + translate_factor[1],
            (vertex[2] * scale_factor[2]) + translate_factor[2]
        )
    
    
    '''
    SR4: FLAT SHADING
    
    '''
    
    def load_model(self, filename, scale_factor, translate_factor):
        model = Obj(filename)
        
        for face in model.faces:
    
            if len(face) == 4:
                f1 = face[0][0] - 1
                f2 = face[1][0] - 1
                f3 = face[2][0] - 1
                f4 = face[3][0] - 1

                v1 = self.transform_vertex(model.vertex[f1], scale_factor, translate_factor)
                v2 = self.transform_vertex(model.vertex[f2], scale_factor, translate_factor)
                v3 = self.transform_vertex(model.vertex[f3], scale_factor, translate_factor)
                v4 = self.transform_vertex(model.vertex[f4], scale_factor, translate_factor)

                if self.texture:

                    ft1 = face[0][1] - 1
                    ft2 = face[1][1] - 1
                    ft3 = face[2][1] - 1
                    ft4 = face[3][1] - 1

                    vt1 = V3(*model.tvertices[ft1])
                    vt2 = V3(*model.tvertices[ft2])
                    vt3 = V3(*model.tvertices[ft3])
                    vt4 = V3(*model.tvertices[ft4])

                    self.triangle_babycenter((v1, v2, v3), (vt1, vt2, vt3))
                    self.triangle_babycenter((v1, v3, v4), (vt1, vt3, vt4))
                else:
                    self.triangle_babycenter((v1, v2, v3))
                    self.triangle_babycenter((v1, v3, v4))
            
            if len(face) == 3:
                f1 = face[0][0] - 1
                f2 = face[1][0] - 1
                f3 = face[2][0] - 1

                v1 = self.transform_vertex(model.vertex[f1], scale_factor, translate_factor)
                v2 = self.transform_vertex(model.vertex[f2], scale_factor, translate_factor)
                v3 = self.transform_vertex(model.vertex[f3], scale_factor, translate_factor)
                
                if self.texture:

                    ft1 = face[0][1] - 1
                    ft2 = face[1][1] - 1
                    ft3 = face[2][1] - 1

                    vt1 = V3(*model.tvertices[ft1])
                    vt2 = V3(*model.tvertices[ft2])
                    vt3 = V3(*model.tvertices[ft3])

                    self.triangle_babycenter((v1, v2, v3), (vt1, vt2, vt3))
                else:
                    self.triangle_babycenter((v1, v2, v3))
    
    
    #posicion de la luz
    def lightPosition(self, x:int, y:int, z:int):
        self.light = V3(x, y, z)
    
    #con zbuffer
    def triangle_babycenter(self, vertices, tvertices=()):
        A, B, C = vertices
        if self.texture:
            tA, tB, tC = tvertices
        
        Light = self.light
        Normal = (B - A) * (C - A)
        i = Normal.norm() @ Light.norm()
        if i < 0:
            return

        print(i)
        self.clearColor = color_select(
            round(255 * i),
            round(255 * i),
            round(255 * i)
        )

        min,max = bounding_box(A, B, C)
        min.round_coords()
        max.round_coords()
        
        for x in range(min.x, max.x + 1):
            for y in range(min.y, max.y + 1):
                w, v, u = barycentric(A, B, C, V3(x, y))

                if (w < 0 or v < 0 or u < 0):
                    continue

                z = A.z * w + B.z * v + C.z * u
                if (self.zBuffer[x][y] < z):
                    self.zBuffer[x][y] = z

                    if self.texture:
                        tx = tA.x * w + tB.x * u + tC.x * v
                        ty = tA.y * w + tB.y * u + tC.y * v

                        self.current_color = self.texture.get_color_with_intensity(tx, ty, i)
                    
                    self.glPoint(x, y)
    '''
    RENDERS FILE
    
    '''
    
    def glFinish(self, filename):
        with open(filename, 'bw') as file:
            # Header
            file.write(char('B'))
            file.write(char('M'))

            # file size
            file.write(dword(self.FILE_SIZE + self.height * self.width * self.PIXEL_COUNT))
            file.write(word(0))
            file.write(word(0))
            file.write(dword(self.FILE_SIZE))

            # Info Header
            file.write(dword(self.DIB_HEADER))
            file.write(dword(self.width))
            file.write(dword(self.height))
            file.write(word(self.PLANE))
            file.write(word(self.BITS_PER_PIXEL))
            file.write(dword(0))
            file.write(dword(self.width * self.height * self.PIXEL_COUNT))
            file.write(dword(0))
            file.write(dword(0))
            file.write(dword(0))
            file.write(dword(0))
    
            # Color table
            for y in range(self.height):
                for x in range(self.width):
                    file.write(self.framebuffer[y][x])
            file.close()
            
            


    '''
    # Function that will implement an algorithm to draw and fill triangles
    def draw_triangles(self, A, B, C):
        #self.glLine(A, B)
        #self.glLine(B, C)
        #self.glLine(C, A)
        
        A.round()
        B.round()
        C.round()
        
        # Filling triangles
        if (A.y > B.y):
            
            A, B = B, A
            
        if (A.y > C.y):
            
            A, C = C, A
            
        if (B.y > C.y):
            
            B, C = C, B

        
        self.glColor(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1))
        
        dx_ac = (C.x -A.x)
        dy_ac = (C.y - A.y)
        
        if (dy_ac == 0):
            return
        
        invslope_ac = dx_ac / dy_ac
        
        dx_ab = B.x - A.x
        dy_ab = B.y - A.y
        
        if (dy_ab != 0):
        
            invslope_ab = dx_ab / dy_ab
            
            for y in range(A.y, B.y + 1):
                xi = round(A.x - invslope_ac * (A.y - y))
                xf = round(A.x - invslope_ab * (A.y - y))
                
                if (xi > xf):
                    xi, xf = xf, xi

                for x in range(xi, xf + 1):
                    self.glPoint(x, y)
        
        dx_bc = C.x - B.x
        dy_bc = C.y - B.y
        
        if (dy_bc != 0):
            
            invslope_bc = dx_bc / dy_bc
                    
            for y in range(B.y, C.y + 1):
                xi = round(A.x - invslope_ac * (A.y - y))
                xf = round(B.x - invslope_bc * (B.y - y))
                
                if (xi > xf):
                    xi, xf = xf, xi

                for x in range(xi, xf + 1):
                    self.glPoint(x, y)
    
    '''