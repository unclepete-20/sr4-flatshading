from bmp_renderer import Render
from Vector import V3

frame = Render()

scale_factor = (20, 20, 50)
translate_factor = (350, 250, 0)

frame.glCreateWindow(700, 700)

frame.lightPosition(0, 0, 1)
    
frame.load_model('koenigsegg.obj', scale_factor, translate_factor)

frame.glFinish('car.bmp')

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