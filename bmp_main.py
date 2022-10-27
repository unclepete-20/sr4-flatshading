from bmp_renderer import Render
from Vector import V3

frame = Render()

scale_factor = (50, 50, 100)
translate_factor = (400, 200, 0)

frame.glCreateWindow(800, 800)

frame.lightPosition(0, 0, 1)
    
frame.load_model('dog.obj', scale_factor, translate_factor)

frame.glFinish('dog.bmp')

'''
square = [
    (0.2, 0.2),
    (0.8, 0.2),
    (0.8, 0.8),
    (0.2, 0.8)
]

last_point = square[-1]

for point in square:
    frame.glLine(*last_point, *point)
    last_point = point
'''