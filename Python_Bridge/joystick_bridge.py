import serial
import pyvjoy
import time

"""
STM32 to vJoy Bridge Script
Author: Enver Yaşar
Assisted by: Gemini (Architecture, signal scaling & debugging)
Description: Maps raw serial UART stream to Windows virtual joystick axes.
"""
COM_PORT = 'COM4'  # Kendi portun
BAUD_RATE = 115200

try:
    j = pyvjoy.VJoyDevice(1)
    print("vJoy cihazı başarıyla bağlandı.")
except Exception as e:
    print(f"vJoy başlatılamadı: {e}")
    exit()

try:
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
    print(f"{COM_PORT} dinleniyor...")
except Exception as e:
    print(f"Seri port açılamadı: {e}")
    exit()

# Her ekseni kendi fiziksel min-max sınırına göre vJoy (0-32768) aralığına genişletir
# invert=True yapıldığında ekseni tersine çevirir (32768 - değer)
def scale_axis(val, in_min, in_max, invert=False):
    val = max(in_min, min(in_max, val))
    scaled = int(((val - in_min) / (in_max - in_min)) * 32768)
    return (32768 - scaled) if invert else scaled

while True:
    try:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        if line:
            parts = line.split(',')
            if len(parts) == 3:
                raw_roll     = int(parts[0])
                raw_pitch    = int(parts[1])
                raw_throttle = int(parts[2])

                # Roll: 1500-2400 aralığını tam 0-32768'e açıyoruz
                roll = scale_axis(raw_roll, in_min=1500, in_max=2400, invert=True)

                # Pitch ve Throttle: Zaten 0-4000 arası tam çalışıyor
                pitch = scale_axis(raw_pitch, in_min=50, in_max=4000, invert=False)
                throttle = scale_axis(raw_throttle, in_min=50, in_max=4000, invert=True)

                # vJoy Eksenlerine gönder
                j.set_axis(pyvjoy.HID_USAGE_X, roll)        # X: Roll
                j.set_axis(pyvjoy.HID_USAGE_Y, pitch)       # Y: Pitch
                j.set_axis(pyvjoy.HID_USAGE_SL0, throttle)  # Slider: Throttle
    except KeyboardInterrupt:
        ser.close()
        break
    except Exception:
        pass