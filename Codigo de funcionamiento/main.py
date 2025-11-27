from machine import Pin, time_pulse_us, PWM, ADC
import time

NAME1 = "SENSOR 1"
TRIG1 = Pin(23, Pin.OUT)   # Pin TRIG1
ECHO1 = Pin(22, Pin.IN)    # Pin ECHO1
MOTOR1 = PWM(Pin(18), freq=1000) #pin Motor1

NAME2 = "SENSOR 2"
TRIG2 = Pin(12, Pin.OUT)   # Pin TRIG2
ECHO2 = Pin(14, Pin.IN)    # Pin ECHO2
MOTOR2 = PWM(Pin(5), freq=1000) #pin Motor2

NAME3 = "SENSOR 3"
TRIG3 = Pin(33, Pin.OUT)   # Pin TRIG3
ECHO3 = Pin(25, Pin.IN)    # Pin ECHO3
MOTOR3 = PWM(Pin(17), freq=1000) #pin

NAME4 = "SENSOR 4"
TRIG4 = Pin(32, Pin.OUT)   # Pin TRIG
ECHO4 = Pin(35, Pin.IN)    # Pin ECHO
MOTOR4 = PWM(Pin(16), freq=1000) #pin Motor4

# Pin ADC donde conectaste el divisor de voltaje
adc = ADC(Pin(34))
adc.atten(ADC.ATTN_11DB)   # Permite leer hasta ~3.3V
adc.width(ADC.WIDTH_12BIT) # Lectura de 0 a 4095

# Valores de tu divisor de voltaje
R1 = 100000   
R2 = 100000   

# --- Configuración del buzzer ---
buzzer = Pin(26, Pin.OUT)   
buzzer.value(0)

buzzer = Pin(27, Pin.OUT)   

# --- Al encender el ESP32, sonar el buzzer ---
buzzer.value(1)     
time.sleep(1)        
buzzer.value(0)

def medir_distancia(TRIG, ECHO):
    # Asegurar TRIG en bajo
    TRIG.value(0)
    time.sleep_us(5)

    # Pulso de 10us al TRIG
    TRIG.value(1)
    time.sleep_us(10)
    TRIG.value(0)

    # Medir duración del pulso en ECHO
    duracion = time_pulse_us(ECHO, 1, 80000)  # timeout 30ms

    if duracion < 0:
        return None  # No hubo lectura

    # Convertir a distancia (cm)
    distancia = (duracion * 0.0343) / 2
    return distancia

def vibrar(motor, distancia, name):
    if distancia is None:
        print(name + " No se detectó objeto.")
        print(name + " Motor apagado")
        motor.duty(0)
    else:
        print(name + " Distancia:", round(distancia, 2), "cm")
        if distancia < 100 and distancia >=50 :
            print(name + " Motor encendido leve")
            motor.duty(200)  # fuerza alta (0–1023)
        elif distancia < 50 and distancia >= 30:
            print(name + " Motor encendido suave")
            motor.duty(400)  # fuerza media
        elif distancia < 30 and distancia > 0:
            print(name + " Motor encendido fuerte")
            motor.duty(800)
        else:
            print(name + " Motor apagado")
            motor.duty(0)
            
def leer_bateria():
    lectura = adc.read()
    volt_esp = (lectura / 4095   ) * 3.3
    volt_bat = volt_esp * ((R1 + R2) / R2)
    print(lectura)
    return volt_bat


def porcentaje_bateria(v):
    if v >= 3.7: return 100
    if v <= 3.30: return 0
    return (v - 3.30) * 100 / (3.7 - 3.30)


def activar_buzzer():
    # Sonido corto
    buzzer.value(1)
    time.sleep(0.2)
    buzzer.value(0)
    time.sleep(0.2)

while True:
    distancia1 = medir_distancia(TRIG1, ECHO1)
    Zumbador1 = vibrar(MOTOR1, distancia1, NAME1)
    
    distancia2 = medir_distancia(TRIG2, ECHO2)
    Zumbador2 = vibrar(MOTOR2, distancia2, NAME2)
    
    distancia3 = medir_distancia(TRIG3, ECHO3)
    Zumbador3 = vibrar(MOTOR3, distancia3, NAME3)
    
    distancia4 = medir_distancia(TRIG4, ECHO4)
    Zumbador4 = vibrar(MOTOR4, distancia4, NAME4)
    
    while True:
        v = leer_bateria()
        p = porcentaje_bateria(v)
        print("Voltaje batería: {:.2f} V   |   Nivel: {:.0f}%".format(v, p))
        # Activar buzzer si batería está baja
        if p < 20:
            activar_buzzer()
        else:
            buzzer.value(0)
        time.sleep(1)
