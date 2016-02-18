from time import sleep
from turtle import Turtle
x , y = 80 , 80
x_top, y_top = -x//2, y//2
moteur = Turtle()
moteur.setposition(x_top, y_top)
for y0 in range(y_top, -y_top, -1):
    if((-1)*((-1)**(y0%2)) == 1):
        for x0 in range(x_top, -x_top, 1):
            moteur.setposition(x0, y0)
    else:
        for x0 in range(-x_top, x_top, -1):
            moteur.setposition(x0, y0)
sleep(20)
