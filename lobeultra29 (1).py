#Libraries
import RPi.GPIO as GPIO
import time
#from test_lina import *
#import Pi GPIO library button class
from gpiozero import Button, LED, PWMLED
from picamera import PiCamera
from time import sleep

from enum import Enum

from lobe import ImageModel
import pygame

camera = PiCamera()

# Load Lobe TF model
# --> Change model file path as needed
model = ImageModel.load('/home/g2/Lobe/Sjakt3 TFLite slow')
 
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_TRIGGER1 = 27
GPIO_ECHO1 = 4
GPIO_TRIGGER2 = 23
GPIO_ECHO2 = 24
 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER1, GPIO.OUT)
GPIO.setup(GPIO_ECHO1, GPIO.IN)
GPIO.setup(GPIO_TRIGGER2, GPIO.OUT)
GPIO.setup(GPIO_ECHO2, GPIO.IN)
 

#global variables, KAN HA SET OG GET FUNKSJON MEN OK
antall1 = 0
antall2 = 0
alt = 0
pappkopper = 0
plastkopper = 0

class State(Enum):
    RUNNING = 0
    WAIT = 1
    TRASH = 2
    FULLPLAST = 3
    FULLPAPP = 4
    ERROR = 5

state = State.RUNNING #0 all good, 1 wait, 2 trash thrown, 3 fullt med plast, 4 fullt med papp, 5 error


def distance(trigger, echo):
    # set Trigger to HIGH
    GPIO.output(trigger, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(trigger, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(echo) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(echo) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance
    
def take_photo():
    print("Take photo")
    # Optional image rotation for camera
    # --> Change or comment out as needed
    camera.rotation = 0
    #Input image file path here
    # --> Change image path as needed
    camera.capture('/home/g2/Pictures/image.jpg')


def scan():
    take_photo()
    # Run photo through Lobe TF model
    result = model.predict_from_file('/home/g2/Pictures/image.jpg')
    # --> Change image path
    return(result.prediction)


def sendTo(trashType): #skeleton 
    global state
    global pappkopper
    global plastkopper
    global antall1
    global antall2

    print(trashType)
    if trashType == "Pappkopp":
        #sender til den for pappkopp
        pappkopper += 1
        pass
    elif trashType == "Plastkopp":
        #sender til den for plastkopp
        plastkopper += 1
        pass
    else:
        print("Dette er bare tull!")


def verify(option):
    global state
    global pappkopper
    global plastkopper
    global antall1
    global antall2
    global alt

    state = State.WAIT #wait
    #writeToFile() #update file with state/endre til updateScreen()

    trashType = scan()
    sendTo(trashType)
    if(not(trashType == "Søppel" or trashType == "PappkoppR" or trashType == "Blank")):
        #oppdater telling for option
        if option == 1:
            antall1 += 1
        elif option == 2: 
            antall2 += 1
        print(str(option) + " Økes med 1")
        
    else:
        state = State.TRASH #wrong trash
        ikke_kopp()
        pygame.display.flip()
        return False
    
    state = State.RUNNING #ready
    if(pappkopper >= 10):
        state = State.FULLPAPP #plast container full
        full()
        pygame.display.flip()
        return False
    if(plastkopper >= 10):
        state = State.FULLPLAST #papp full
        full()
        pygame.display.flip()
        return False
        
    return True



pygame.init()
pygame.font.init()




question="Hvem synes du hadde best antrekk under MGP?"

cube_w=30
cube_h=30

X = 1200
Y = 600

clock = pygame.time.Clock()
fps = 20
v = 200
x1 = int(X*1/12)
x2 = int(X*10.5/12)
y1 = 0
y2 = 0

 
white = (255, 255, 255)
pink= (255,106,106)
black=(64,64,64)



display_surface = pygame.display.set_mode((0, 0),pygame.FULLSCREEN)

def alt1_text(): 
    font = pygame.font.Font('freesansbold.ttf', 18)
    text = font.render("Alternativ 1", True, pink)
    text_rect = text.get_rect(center=(int(X/4), int(Y/2)))
    display_surface.blit(text, text_rect)

def alt2_text(): 
    font = pygame.font.Font('freesansbold.ttf', 18)
    text = font.render("Alternativ 2", True, pink)
    text_rect = text.get_rect(center=(int(X*3/4), int(Y/2)))
    display_surface.blit(text, text_rect)

def question_text():
    font = pygame.font.Font('freesansbold.ttf', 32)
    text = font.render(question, True, pink)
    text_rect = text.get_rect(center=(int(X/2), int(Y/8)))
    display_surface.blit(text, text_rect)

def bilde1():
    image = pygame.image.load("/home/g2/GUI/p1.PNG").convert_alpha()
    width = image.get_rect().width
    height = image.get_rect().height
    image = pygame.transform.scale(image, (int(width/1.4), int(height/1.4)))
    text_rect = image.get_rect(center=(int(X/4), int(Y*7.5/10)))
    display_surface.blit(image, text_rect)
 
def bilde2():
    image = pygame.image.load("/home/g2/GUI/p2.PNG").convert_alpha()
    width = image.get_rect().width
    height = image.get_rect().height
    image = pygame.transform.scale(image, (int(width/5), int(height/5)))
    text_rect = image.get_rect(center=(int(X*4.9/6), int(Y*7.9/10)))
    display_surface.blit(image, text_rect)

def poeng_alt1(i):
        for j in range(0,i):
            #print("jonasalt1")
            rec1= pygame.Rect(int(x1), Y-(cube_h*j)-3*j, cube_h, cube_w)
            pygame.draw.rect(display_surface, pink, rec1)
        #if(i > 0):
         #   rec1= pygame.Rect(int(x1), Y-(cube_h*(i))-3*i, cube_h, cube_w)
          #  pygame.draw.rect(display_surface, pink, rec1)

def poeng_alt2(i):
        for j in range(0,i):
            #print("jonasalt2")
            rec2= pygame.Rect(int(x2), Y-(cube_h*j)-3*j, cube_h, cube_w)
            pygame.draw.rect(display_surface, pink, rec2)
        #if(i > 0):
         #   rec2= pygame.Rect(int(x2), Y-(cube_h*(i))-3*i, cube_h, cube_w)
          #  pygame.draw.rect(display_surface, pink, rec2)
        
def ny_alt1():
    global y1
    if(antall2 > 0):   #først så tegner vi øverste blokk på andre siden (de vanlige blokkene tegnes egt bare opp til nest øverste)
        rec2= pygame.Rect(int(x2), Y-(cube_h*(antall2))-3*antall2, cube_h, cube_w)
        pygame.draw.rect(display_surface, pink, rec2)
    while(not(int(y1)+antall1*cube_h + 3*antall1) >= Y): #så "dropper" vi blokkene
        pygame.draw.rect(display_surface, (0,0,0), pygame.Rect(int(x1), int(y1- 5), cube_h, cube_w))
        pygame.draw.rect(display_surface, (255,0,0), pygame.Rect(int(x1), int(y1), cube_h, cube_w))
        y1 += 5
        pygame.display.flip()
    #til slutt må vi "rette" på blokken, fordi den ender som regel opp litt for høyt, eller for lavt
    if(antall1%5==0): #for poengsum som går opp i 5 gangen så treffer de perfekt, så de trenger ikke justeres
        pygame.draw.rect(display_surface, (0,0,0), pygame.Rect(int(x1), int(y1- 5), cube_h, cube_w))
        pygame.draw.rect(display_surface, (255,0,0), pygame.Rect(int(x1), int(y1), cube_h, cube_w))
    
    if(y1+antall1*cube_h + 3*antall1 > Y): # her justeres posisjon
        pygame.draw.rect(display_surface, (0,0,0), pygame.Rect(int(x1), int(y1), cube_h, cube_w))
        while(y1+antall1*cube_h + 3*antall1 > Y):
            y1-= 1
        pygame.draw.rect(display_surface, (255,0,0), pygame.Rect(int(x1), int(y1), cube_h, cube_w)) #swag
        pygame.display.flip()
    y1=0
    
def ny_alt2():
    global y2
    if(antall1 > 0):
        rec2= pygame.Rect(int(x1), Y-(cube_h*(antall1))-3*antall1, cube_h, cube_w)
        pygame.draw.rect(display_surface, pink, rec2)
    
    while(not(int(y2)+antall2*cube_h + 3*antall2) >= Y):
        pygame.draw.rect(display_surface, (0,0,0), pygame.Rect(int(x2), int(y2- 5), cube_h, cube_w))
        pygame.draw.rect(display_surface, (255,0,0), pygame.Rect(int(x2), int(y2), cube_h, cube_w))
        y2 += 5
        pygame.display.flip()
        
    if(antall2%5==0): #for poengsum som går opp i 5 gangen så treffer de perfekt, så de trenger ikke justeres
        pygame.draw.rect(display_surface, (0,0,0), pygame.Rect(int(x2), int(y2- 5), cube_h, cube_w))
        pygame.draw.rect(display_surface, (255,0,0), pygame.Rect(int(x2), int(y2), cube_h, cube_w))
    
    if(y2+antall2*cube_h + 3*antall2 > Y): # her justeres posisjon
        pygame.draw.rect(display_surface, (0,0,0), pygame.Rect(int(x2), int(y2), cube_h, cube_w))
        while(y2+antall2*cube_h + 3*antall2 > Y):
            y2-= 1
        pygame.draw.rect(display_surface, (255,0,0), pygame.Rect(int(x2), int(y2), cube_h, cube_w)) #swag
        pygame.display.flip()


    y2=0



def full():
    display_surface.fill(pink)
    font = pygame.font.SysFont('couriernew', 50, bold=True)
    text = font.render("Søppelet er fullt!", True, black)
    text_rect = text.get_rect(center=(X/2, Y/2))
    display_surface.blit(text, text_rect)

def ikke_kopp():
    font = pygame.font.SysFont('couriernew', 50, bold=True)
    text = font.render("Kun kopper skal kastes her!", True, pink)
    text2=font.render("Din stemme telles ikke", True, pink)
    text_rect = text.get_rect(center=(X/2, Y/2))
    text_rect2 = text.get_rect(center=(X/2+30, Y/2+40))
    display_surface.blit(text, text_rect)
    display_surface.blit(text2, text_rect2)
    
def lys1():
    surface = pygame.Surface((X,Y), pygame.SRCALPHA)
    pygame.draw.polygon(surface, (255,255,255,50), ((X/2, -50), (1*X/9, Y), ((3*X)/9, Y)))
    display_surface.blit(surface,(0,0))

def lys2():
    surface = pygame.Surface((X,Y), pygame.SRCALPHA)
    pygame.draw.polygon(surface, (255,255,255,50), ((X/2, -50), (5.8*X/9, Y), ((7.8*X)/9, Y)))
    display_surface.blit(surface,(0,0))
    
        
def draw(alt):
    display_surface.fill((0, 0, 0))   
    alt1_text()
    alt2_text()
    question_text()
    bilde1()
    bilde2()
 
    poeng_alt1(antall1)
    poeng_alt2(antall2)
    #clock.tick(fps)
    if(alt == 1):
        lys1()
        ny_alt1()
    elif (alt==2):
        lys2()
        ny_alt2()

    pygame.display.flip()


if __name__ == '__main__':
    try:
        display_surface = pygame.display.set_mode((X, Y))
        draw(0)
        count = 0

        while True:
            dist1 = distance(GPIO_TRIGGER1, GPIO_ECHO1)
            dist2 = distance(GPIO_TRIGGER2, GPIO_ECHO2)
            
            '''
            if dist1 < 10:
                print("wtf1", dist1)
            if dist2 < 10:
                print("wtf2", dist2)
            sleep(0.5)
            '''
            
            if dist1 < 8:
                dist1 = distance(GPIO_TRIGGER1, GPIO_ECHO1)
                if dist1 < 8:
                    sleep(1)
                    if(verify(1)):
                        draw(1)
            if dist2 < 8:
                dist2 = distance(GPIO_TRIGGER2, GPIO_ECHO2)
                if dist2 < 8:
                    sleep(1)
                    if(verify(2)):
                        draw(2)
            sleep(0.12)
            
            '''
            if count > 1:
                #full()
                ikke_kopp()
                pygame.display.flip()
            '''
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        
 
    # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Jonas elsker boller<3")
        
        GPIO.cleanup()