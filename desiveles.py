import audio
import time

buf_global = None

def callback(buf):
    global buf_global
    buf_global = buf

audio.init(channels=1, frequency=16000, gain_db=24, highpass=0.9883)
audio.start_streaming(callback)

print("Calibrando... queda en silencio")

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
            if muestras > 0:
                rms = (suma / muestras) ** 0.5
                print(int(rms))
        except Exception as e:
            print("Error:", e)
            buf_global = None
    time.sleep_ms(50)
