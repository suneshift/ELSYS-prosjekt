#Libraries
import RPi.GPIO as GPIO
import time

#import Pi GPIO library button class
from gpiozero import Button, LED, PWMLED
from picamera import PiCamera
from time import sleep


from lobe import ImageModel
import pygame

camera = PiCamera()

# Load Lobe TF model
# --> Change model file path as needed
#model = ImageModel.load('/home/g2/Lobe/Sjakt3 TFLite slow')
model = ImageModel.load('/home/g2/Lobe/Fast')
 
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_TRIGGER1 = 23
GPIO_ECHO1 = 24
GPIO_TRIGGER2 = 27
GPIO_ECHO2 = 4
BIT0 = 25 
BIT1 = 26

GPIO.setwarnings(False)
 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER1, GPIO.OUT)
GPIO.setup(GPIO_ECHO1, GPIO.IN)
GPIO.setup(GPIO_TRIGGER2, GPIO.OUT)
GPIO.setup(GPIO_ECHO2, GPIO.IN)
GPIO.setup(BIT0, GPIO.OUT)
GPIO.setup(BIT1, GPIO.OUT)
 

#global variables, KAN HA SET OG GET FUNKSJON MEN OK
antall1 = 0
antall2 = 0
alt = 0
pappkopper = 0
plastkopper = 0


def distance(trigger, echo):
    # set Trigger to HIGH
    GPIO.output(trigger, True)
    
    # set Trigger after 0.01ms to LOW
    # ENDRE DENNE HER
    sleep(0.00001)
    #pygame.time.delay(1)
    GPIO.output(trigger, False)
 
    myStartingTime = StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(echo) == 0:
        StartTime = time.time()
        #Hopp ut hvis noe feiler
        calculation_starting_time = time.time()
        if calculation_starting_time - myStartingTime > 1:
            break
 
    # save time of arrival
    while GPIO.input(echo) == 1:
        StopTime = time.time()
        #Hopp ut hvis noe feiler
        calculation_starting_time = time.time()
        if calculation_starting_time - myStartingTime > 1:
            break
 
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


def sendTo(trashType):
    global state
    global pappkopper
    global plastkopper
    global antall1
    global antall2

    print(trashType)
    if trashType == "Pappkopp":
        #sender til den for pappkopp
        pappkopper += 1
        #PAPP
        GPIO.output(BIT0, 1)
        GPIO.output(BIT1, 0)
    elif trashType == "Plastkopp":
        #sender til den for plastkopp
        plastkopper += 1
        #PLAST
        GPIO.output(BIT0, 0)
        GPIO.output(BIT1, 1)
    else:
        print("Dette er bare tull!")
        #ANNET
        GPIO.output(BIT0, 1)
        GPIO.output(BIT1, 1)

def verify(option):
    global state
    global pappkopper
    global plastkopper
    global antall1
    global antall2
    global alt
    #startT = time.time()
    trashType = scan()
    #stopT = time.time()
    #print("Tid for klassifisering: " + str(stopT-startT))
    sendTo(trashType)
    if(trashType != "Annet"):
        #oppdater telling for option
        if option == 1:
            antall1 += 1
        elif option == 2: 
            antall2 += 1
        print(str(option) + " Økes med 1")
        
    else:
        #Feil objekt
        ikke_kopp()
        pygame.display.flip()
        return False
    
    if(pappkopper >= 10):
        #plast container full
        full()
        pygame.display.flip()
        return False
    if(plastkopper >= 10):
        #papp full
        full()
        pygame.display.flip()
        return False
        
    return True



pygame.init()
pygame.font.init()

question="Hvem synes du hadde best antrekk under MGP?"

cube_w=60
cube_h=60

#X=2400
#Y=900
#display_surface = pygame.display.set_mode((X,Y))
display_surface = pygame.display.set_mode((0, 0),pygame.FULLSCREEN)
X, Y = pygame.display.get_surface().get_size()


clock = pygame.time.Clock()
fps = 20
v = 200
x1 = int(X*1/12)
x2 = int(X*10.5/12)
y1 = 0
y2 = 0

 
white = (255, 255, 255)
pink= (255,153,204)
blue = (153, 204, 255)
gold = (255, 215, 0)
black=(64,64,64)




def alt1_text():
    font = pygame.font.SysFont('couriernew', 30, bold=True)
    #font = pygame.font.Font('freesansbold.ttf', 18)
    text = font.render("Alessandra Mele", True, pink)
    text_rect = text.get_rect(center=(int(3*X/10), int(17*Y/32)))
    display_surface.blit(text, text_rect)

def alt2_text(): 
    font = pygame.font.SysFont('couriernew', 30, bold=True)
    #font = pygame.font.Font('freesansbold.ttf', 18)
    text = font.render("Ulrikke Brandstorp", True, blue)
    text_rect = text.get_rect(center=(int(X*7/10), int(17*Y/32)))
    display_surface.blit(text, text_rect)

def question_text():
    font = pygame.font.SysFont('couriernew', 45, bold=True)
    #font = pygame.font.Font('freesansbold.ttf', 32)
    text = font.render(question, True, white)
    text_rect = text.get_rect(center=(int(X/2), int(3*Y/14)))
    display_surface.blit(text, text_rect)

def bilde1():
    image = pygame.image.load("/home/g2/GUI/p1.PNG").convert_alpha()
    width = image.get_rect().width
    height = image.get_rect().height
    image = pygame.transform.scale(image, (int(width/0.75), int(height/0.75)))
    text_rect = image.get_rect(center=(int(X*(0.28)), int(Y*7.4/10)))
    display_surface.blit(image, text_rect)
 
def bilde2():
    image = pygame.image.load("/home/g2/GUI/p2.PNG").convert_alpha()
    width = image.get_rect().width
    height = image.get_rect().height
    image = pygame.transform.scale(image, (int(width/2.5), int(height/2.5)))
    text_rect = image.get_rect(center=(int(X*0.78), int(Y*7.6/10)))
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
            pygame.draw.rect(display_surface, blue, rec2)
        #if(i > 0):
         #   rec2= pygame.Rect(int(x2), Y-(cube_h*(i))-3*i, cube_h, cube_w)
          #  pygame.draw.rect(display_surface, pink, rec2)
        
def ny_alt1():
    global y1
    if(antall2 > 0):   #først så tegner vi øverste blokk på andre siden (de vanlige blokkene tegnes egt bare opp til nest øverste)
        rec2= pygame.Rect(int(x2), Y-(cube_h*(antall2))-3*antall2, cube_h, cube_w)
        pygame.draw.rect(display_surface, blue, rec2)
    while(not(int(y1)+antall1*cube_h + 3*antall1) >= Y): #så "dropper" vi blokkene
        pygame.draw.rect(display_surface, (0,0,0), pygame.Rect(int(x1), int(y1- 10), cube_h, cube_w))
        pygame.draw.rect(display_surface, pink, pygame.Rect(int(x1), int(y1), cube_h, cube_w))
        y1 += 10
        pygame.display.flip()
    #til slutt må vi "rette" på blokken, fordi den ender som regel opp litt for høyt, eller for lavt
    if(antall1%5==0): #for poengsum som går opp i 5 gangen så treffer de perfekt, så de trenger ikke justeres
        pygame.draw.rect(display_surface, (0,0,0), pygame.Rect(int(x1), int(y1- 10), cube_h, cube_w))
        pygame.draw.rect(display_surface, pink, pygame.Rect(int(x1), int(y1), cube_h, cube_w))
    
    if(y1+antall1*cube_h + 3*antall1 > Y): # her justeres posisjon
        pygame.draw.rect(display_surface, (0,0,0), pygame.Rect(int(x1), int(y1), cube_h, cube_w))
        while(y1+antall1*cube_h + 3*antall1 > Y):
            y1-= 1
        pygame.draw.rect(display_surface, pink, pygame.Rect(int(x1), int(y1), cube_h, cube_w)) #swag
        pygame.display.flip()
    y1=0
    
def ny_alt2():
    global y2
    if(antall1 > 0):
        rec2= pygame.Rect(int(x1), Y-(cube_h*(antall1))-3*antall1, cube_h, cube_w)
        pygame.draw.rect(display_surface, pink, rec2)
    
    while(not(int(y2)+antall2*cube_h + 3*antall2) >= Y):
        pygame.draw.rect(display_surface, (0,0,0), pygame.Rect(int(x2), int(y2- 10), cube_h, cube_w))
        pygame.draw.rect(display_surface, blue, pygame.Rect(int(x2), int(y2), cube_h, cube_w))
        y2 += 10
        pygame.display.flip()
        
    if(antall2%5==0): #for poengsum som går opp i 5 gangen så treffer de perfekt, så de trenger ikke justeres
        pygame.draw.rect(display_surface, (0,0,0), pygame.Rect(int(x2), int(y2- 10), cube_h, cube_w))
        pygame.draw.rect(display_surface, blue, pygame.Rect(int(x2), int(y2), cube_h, cube_w))
    
    if(y2+antall2*cube_h + 3*antall2 > Y): # her justeres posisjon
        pygame.draw.rect(display_surface, (0,0,0), pygame.Rect(int(x2), int(y2), cube_h, cube_w))
        while(y2+antall2*cube_h + 3*antall2 > Y):
            y2-= 1
        pygame.draw.rect(display_surface, blue, pygame.Rect(int(x2), int(y2), cube_h, cube_w)) #swag
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
    text_rect = text.get_rect(center=(int(X/2), int(Y/2)))
    text_rect2 = text.get_rect(center=(int(X/2+30), int(Y/2+40)))
    display_surface.blit(text, text_rect)
    display_surface.blit(text2, text_rect2)
    
def lys1():
    surface = pygame.Surface((X,Y), pygame.SRCALPHA)
    pygame.draw.polygon(surface, (255,255,255,50), ((int(X/2), -50), (int(1*X/9), Y), (int((3*X)/9), Y)))
    display_surface.blit(surface,(0,0))

def lys2():
    surface = pygame.Surface((X,Y), pygame.SRCALPHA)
    pygame.draw.polygon(surface, (255,255,255,50), ((int(X/2), -50), (int(5.8*X/9), Y), (int((7.8*X)/9), Y)))
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
    running = True
    #display_surface = pygame.display.set_mode((X, Y))
    #display_surface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    draw(0)
    count = 0
    GPIO.output(BIT0, 0)
    GPIO.output(BIT1, 0)

    while running:
        #print("Running")
        dist1 = distance(GPIO_TRIGGER1, GPIO_ECHO1)
        #print("Dist1")
        dist2 = distance(GPIO_TRIGGER2, GPIO_ECHO2)
        #print("Dist2")
        
        
        if dist1 < 7:
            dist1 = distance(GPIO_TRIGGER1, GPIO_ECHO1)
            if dist1 < 7:
                print("Distance 1 triggered")
                #sleep(1)
                pygame.time.delay(1000)
                if(verify(1)):
                    draw(1)
                    #print("finished drawing")
                    #Default
                    GPIO.output(BIT0, 0)
                    GPIO.output(BIT1, 0)
                else:
                    pygame.time.delay(2)
                    GPIO.output(BIT0, 0)
                    GPIO.output(BIT1, 0)
        if dist2 < 7:
            dist2 = distance(GPIO_TRIGGER2, GPIO_ECHO2)
            if dist2 < 7:
                print("Distance 2 triggered")
                #sleep(1)
                pygame.time.delay(1000)
                if(verify(2)):
                    draw(2)
                    #print("finished drawing")
                    #Default
                    GPIO.output(BIT0, 0)
                    GPIO.output(BIT1, 0)
                else:
                    pygame.time.delay(2)
                    GPIO.output(BIT0, 0)
                    GPIO.output(BIT1, 0)
        #print("sleeping")
        #sleep(0.2)
        pygame.time.delay(20)
        #print("Done sleeping")
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Quitting")
                running = False
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                print("Keydown")
                if event.key == pygame.K_s:
                    running = False
                    #GPIO.cleanup()
                    pygame.quit()
                #reset
                if event.key == pygame.K_r:
                    antall1 = 0
                    antall2 = 0
                    pappkopper = 0
                    plastkopper = 0
                    draw(0)
                #exit fullscreen
                if event.key == pygame.K_d:
                    display_surface = pygame.display.set_mode((1200,600))
                    draw(0)
                #enter fullscreen
                if event.key == pygame.K_f:
                    display_surface = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
                    draw(0)
        
                
 
        
        
