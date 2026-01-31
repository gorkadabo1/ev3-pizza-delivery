#!/usr/bin/env python3
from ev3dev2.sensor import Sensor
from ev3dev2.motor import OUTPUT_A, OUTPUT_D, MoveTank
from ev3dev2.sensor.lego import UltrasonicSensor
from ev3dev2.sensor.lego import ColorSensor
from ev3dev2.led import Leds
from ev3dev2.sensor import INPUT_1, INPUT_3, INPUT_4

from time import sleep
from threading import Thread

#Ultrasonikoaren kontrola kudeatzeko klasea
class ultrasonic(Thread):
    def __init__(self, threadID):
        Thread.__init__(self)
        self.threadID = threadID
        self.running = True
        self.leds = Leds()
        self.us = UltrasonicSensor(INPUT_3)
        self.distantzia = 0
    
    #Haria exekutatzen denean kalkulatuko den logika
    def run(self):
        self.leds.all_off()
        
        while self.running:
            self.distantzia = self.us.distance_centimeters
            sleep (0.01)

#Kolore-sentsorearekin semaforoen egoera detektatzeko klasea
class semaforoa(Thread):
    def __init__(self, threadID, sekuentzia):
        Thread.__init__(self)
        self.threadID = threadID
        self.running = True
        self.eye = ColorSensor(INPUT_4)
        self.sekuentzia = sekuentzia

        #Koloreen balioak definitu RGB eskalan
        self.red = ['red', 84, 28, 14]
        self.green = ['green', 84, 188, 104]
        self.blue = ['blue', 35, 145, 118]

        self.koloreak = [self.red, self.green, self.blue]

        #Lurra detektatzeko aldagaia
        self.ground = 0

        #Bidetik atera behar dela adierazteko flag-a
        self.atera = False

        #Semaforo zerrenda
        self.momentuSemaforoa = []

        #Semaforo indizea
        self.j = 0
    
    def run(self):
        while self.running:
            diferentziaMin = 9999999999999 #Diferentzia minimoa kalkulatzeko aldagai hasieratu
            momentuKolorea = ''

            #Kolore-sentsorearen RGB balioak irakurri
            red = self.eye.rgb[0]
            green = self.eye.rgb[1]
            blue = self.eye.rgb[2]

            #Detektatutako kolorea ea gorria berdea edo urdina den detektatu aurretik egindako definizioak erabiliz
            for kolorea in self.koloreak:
                diferentzia = abs(red - kolorea[1]) + abs(green - kolorea[2]) + abs(blue - kolorea[3])
                if diferentzia < diferentziaMin:
                    diferentziaMin = diferentzia
                    momentuKolorea = kolorea[0]

            #Lurra detektatzeko atalasea ezarri
            if diferentziaMin > 90:
                momentuKolorea = 'ground'
            
            #Uneko kolorea ez bada 'ground', groud aldagaia 0ra berrezarri.
            if momentuKolorea != 'ground':
                #print("Red: {}, Green: {}, Blue: {}, MK: {}".format(red, green, blue, momentuKolorea)) 
                self.ground = 0
                
                #momentuSemaforoa zerrenda hutsik badago, unean detektatutako kolorea gehitu.
                if len(self.momentuSemaforoa) == 0:
                    self.momentuSemaforoa.append(momentuKolorea)

                #momentuSemaforoa azken elementua eta unean detektatutako kolorea desberdinak badira, kolore berria gehitu.
                elif self.momentuSemaforoa[-1] != momentuKolorea:
                    self.momentuSemaforoa.append(momentuKolorea)
            
            else:
                #Uneko kolorea 'ground' bada, eta ground aldagaia ez bada 4 baino handiagoa, gehitu 1.
                if self.ground <= 4:
                    self.ground += 1
                
                #ground 4ra iristen bada, ground eta momentuSemaforoa berrezarri.
                else:
                    self.ground = 0
                    self.momentuSemaforoa = []

            #momentuSemaforoa zerrendak 3 kolore baditu (sekuentzia bat osatu duela adierazten du).
            if len(self.momentuSemaforoa) == 3:

                #momentuSemaforoa-ko azken sekuentzia egokia den egiaztatu (self.sekuentzia erabiliz).
                #Egiaztatzean, sekuentziako kolore posizioa eta kolore zuzena konparatzen dira.
                if (self.momentuSemaforoa[self.sekuentzia[1][self.j] - 1] == self.sekuentzia[0][self.j]) :
                    
                    #Sekuentzia zuzena bada, atera aldagaiari True balioa esleitu (seinale bezala erabiltzeko).
                    self.atera = True
                    self.j += 1

                    #Indizea 3ra iristen bada (sekuentzia osoa osatu delako), 0ra berrezarri.
                    if self.j >= 3:
                        self.j = 0
                else:
                    self.atera = False
                self.momentuSemaforoa = []
            sleep(0.1)

#Marra beltza detektatzeko funtzioa
def marraDetektatu(lsa):

    balioak = [0, 0, 0, 0, 0, 0, 0, 0]
    marra =  [0, 0, 0, 0, 0, 0, 0, 0, 0]
    batazbestekoa = 0

    for i in range(0,8):
        balioak[i] = lsa.value(i)
        batazbestekoa += lsa.value(i)

    batazbestekoa /= 8

    for i in range(0,8):
        if(balioak[i] < batazbestekoa) :
            marra[i] = 1
        
    return marra


def main():

    robot = MoveTank(OUTPUT_A, OUTPUT_D)
    lsa = Sensor(INPUT_1)
    t_handia = 6 #6
    t_txikia = 1 #1

    #Ultrasoinu sentsorea aktibatu
    u = ultrasonic(1)
    u.setDaemon = True
    u.start()

    #Semaforoaren sekuentzia eta ordena kontrolatu
    parametroKolore = ['blue', 'green', 'green']
    parametroZenbaki = [3, 3, 1]
    c = semaforoa(2, [parametroKolore, parametroZenbaki])
    c.setDaemon = True
    c.start()
    giraDerecha = False

    erdikoIndizea = 3.5
    aurrekoIndizea = 0

    while True:

        #Objektu hurbilegi dagoenean gelditu eta kolorea aldatu
        while u.us.distance_centimeters < 30:
            u.leds.set_color('LEFT', 'RED')
            u.leds.set_color('RIGHT', 'RED')
            robot.on(0, 0)
            sleep(0.025)
        
        u.leds.set_color('LEFT', 'GREEN')
        u.leds.set_color('RIGHT', 'GREEN')

        #Semaforoa detektatu bada, eskuinera biratzeko flag bat akitabtzen dugu aurrerago egiaztatuko dena
        if c.atera:
            giraDerecha = True
            c.atera = False

        v = 20 #25
        k = 1 #1
        marra = marraDetektatu(lsa)
        
        #Marra beltzaren luzera eta posizioa detektatzeko aldagaiak hasieratu
        max_hasiera = -1
        bukaera_max = -1
        luzera_max = 0

        hasiera = -1

        for i, balioa in enumerate(marra):
            if balioa == 1: #Marra beltzaren hasiera detektatu.
                if hasiera == -1: #Oraindik marra baten hasiera ez bada aurkitu, posizioa gordetzen da.
                    hasiera = i
            else:
                if hasiera != -1: #Uneko marra beltzaren amaiera detektatu.
                    luzera = i - hasiera #Uneko marraren luzera kalkulatu.

                    #Marraren luzera maximoa eguneratu, beharrezkoa bada.
                    if luzera > luzera_max:
                        luzera_max = luzera
                        max_hasiera = hasiera
                        bukaera_max = i - 1

                    #Uneko marraren hasiera balioa berrezarri hurrengo detekziorako.
                    hasiera = -1

        #Eskuinera biratzeko egoera aktibo badago eta marraren luzera > 4 bada, robota eskuinera birarazi
        if giraDerecha and luzera_max > 4: #Probar > 4
            robot.on(30, 0)
            sleep(0.5)
            giraDerecha = False
            continue

        #Marraren luzera txikia bada (<= 1), aurreko indizea mantendu.
        elif luzera_max <= 1:
            erdikoIndizea = aurrekoIndizea

        #Bestela, marraren erdiko posizioa kalkulatu.
        else:
            erdikoIndizea = (max_hasiera + bukaera_max) / 2

        diferentzia = 3.5 - erdikoIndizea
        aurrekoIndizea = erdikoIndizea


        if diferentzia > 2:
            ajuste_v = diferentzia * t_handia
            ajuste_k = diferentzia
        elif diferentzia < -2:
            ajuste_v = (-diferentzia) * t_handia
            ajuste_k = (-diferentzia)
        else:
            if diferentzia > 0:
                ajuste_v = diferentzia * t_txikia
                ajuste_k = diferentzia
            else:
                ajuste_v = (-diferentzia) * t_txikia
                ajuste_k = (-diferentzia)

        v -= ajuste_v
        k += ajuste_k

        vl = v - diferentzia * k
        vr = v + diferentzia * k

        robot.on(vl, vr)
        sleep(0.025)



if __name__ == "__main__":

    main()