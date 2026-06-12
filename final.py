import audio
import time

SILENCIO = 600
UMBRAL_SONIDO = 1300
VENTANA = 60
TOS_ACTIVOS_MAX = 20
MUGIDO_ACTIVOS_MIN = 45

buf_global = None

def callback(buf):
    global buf_global
    buf_global = buf

audio.init(channels=1, frequency=16000, gain_db=24, highpass=0.9883)
audio.start_streaming(callback)

historial = []
ultimo_estado = "SILENCIO"

print("Sistema iniciado...")

while True:
    if buf_global is not None:
        try:
            buf = buf_global
            buf_global = None
            suma = 0
            muestras = 0
            for i in range(0, len(buf) - 1, 2):
                s = (buf[i+1] << 8) | buf[i]
                if s > 32767:
                    s -= 65536
                suma += s * s
                muestras += 1
            if muestras == 0:
                continue
            rms = (suma / muestras) ** 0.5
            historial.append(rms)
            if len(historial) > VENTANA:
                historial.pop(0)

            if len(historial) < VENTANA:
                continue

            picos = 0
            en_pico = False
            for val in historial:
                if val > UMBRAL_SONIDO and not en_pico:
                    picos += 1
                    en_pico = True
                elif val < SILENCIO:
                    en_pico = False

            activos = sum(1 for v in historial if v > SILENCIO)

            if picos >= 1 and 4 <= activos <= TOS_ACTIVOS_MAX:
                estado = "TOS"
            elif activos >= MUGIDO_ACTIVOS_MIN:
                estado = "MUGIDO"
            elif activos > 2:
                estado = "SONIDO"
            else:
                estado = "SILENCIO"

            if estado != ultimo_estado:
                if estado == "TOS":
                    print("ALERTA TOS DETECTADA")
                elif estado == "MUGIDO":
                    print("MUGIDO NORMAL")
                elif estado == "SONIDO":
                    print("sonido normal")
                else:
                    print("silencio")
                ultimo_estado = estado

        except Exception as e:
            print("Error:", e)
            buf_global = None
    time.sleep_ms(50)
