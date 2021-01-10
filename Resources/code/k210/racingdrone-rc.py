"""rc a b c d
a left/right
b forward/backward
c up/down
d yaw """


import sensor, image, time
from machine import UART
from fpioa_manager import fm
from board import board_info


fm.register (15, fm.fpioa.UART1_TX)
fm.register (17, fm.fpioa.UART1_RX)
uart_A = UART (UART.UART1, 9600, 8, None, 1, timeout = 1000, read_buf_len = 4096)

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_hmirror(0)
sensor.skip_frames(time = 2000)


gatethreshold = (0, 100, -128, -19, -20, 46)
destination = [160,120]


def process_tags():
    img = sensor.snapshot()
    img = img.gaussian(3)
    img = img.binary([(0, 100, -128, -19, -20, 46)])
    img = img.erode(1)
    img = img.dilate(1)
    img = img.dilate(1)
    img = img.dilate(1)

    re= img.find_rects()

    if re:
        #print(re)
        for r in re:
            print("outer rectangle : "+str(r))

            re2= img.find_rects(r.rect())
            if re2:
                #print("inner rectangle : "+str(re2))
                for r2 in re2:
                    print("inner rectangle : "+str(r2))
                    cordr = r2
            else:
                cordr = r

            if (cordr.w()*0.8 < cordr.h()/0.85 and cordr.w()*1.2 > cordr.h()/0.85 and cordr.magnitude() > 150000):
                print("chosen rectangle : "+str(cordr))
                img = img.draw_rectangle(cordr.rect())
                current = [(cordr.x()+int((cordr.w()/2))),(cordr.y()+int((cordr.h()/2)))]
                img = img.draw_cross(current)
                zip_object = zip(destination, current)
                difference = []
                for list1_i, list2_i in zip_object:
                    difference.append(list1_i-list2_i)
                print("Diff:",difference)
                distance = int(3.9*390*240/(cordr.w()*26.84))
                viewdistance = distance - 90
                left = int((-1*distance*difference[0]*2.684/(3.9*240))-15)
                up = int((distance*difference[1]*3.590/(3.9*320))-6)
                xyz = [distance,left,up]
                print("xyz : "+str(xyz))
                factor = 15
                constant = 12
                if left < 0:
                    factor = -15
                rcleft = int(factor*(abs(left)/(abs(left)+constant)))
                factor = 15
                if up < 0:
                    factor = -15
                rcup = int(factor*(abs(up)/(abs(up)+constant)))
                factor = 15
                if viewdistance < 0:
                    factor = -15
                rcviewdistance = int(factor*(abs(viewdistance)/(abs(viewdistance)+constant)))
                if abs(rcleft) < 7 and abs(rcup) < 7 and abs(rcviewdistance) < 13 :
                    print("1:forward "+str(105+rcviewdistance))
                    return "1:forward "+str(105+rcviewdistance)
                else:
                    print("0:rc "+str(rcleft)+" "+str(rcviewdistance)+" "+str(rcup)+" 0")
                    return "0:rc "+str(rcleft)+" "+str(rcviewdistance)+" "+str(rcup)+" 0"

            else:
                print("false postive")
                return("0:rc 0 0 0 0")

    else:
        print("no rectangles found!")
        return("0:rc 0 0 0 0")

def run_algo():

    print("replying :)")
    rccommand = process_tags()
    print(rccommand)
    uart_A.write(rccommand)



while(1):
    #uncomment to run this code with esp32
    #if uart_A.any():
        #try:

            #read_data = uart_A.read()
            #read_str = read_data.decode('utf-8')
            #if (read_str == "1"):
                #print("string = ", read_str)
                #run_algo()
        #except  (UnicodeError):
            #pass
    #uncomment to debugging this code while connected to PC       
    run_algo()

uart_A.deinit ()
del uart_A
