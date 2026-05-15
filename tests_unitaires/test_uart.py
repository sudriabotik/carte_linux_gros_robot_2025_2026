import serial
import time

# =========================
# CONFIG
# =========================
DEBUG = True

UART_PORT = "/dev/ttyS6"
BAUDRATE = 1000000
LOG_FILE = "log_uart.txt"

# =========================
# MAIN
# =========================

def main():
    if not DEBUG:
        print("Debug désactivé ? UART non lancé")
        return

    try:
        ser = serial.Serial(
            port=UART_PORT,
            baudrate=BAUDRATE,
            timeout=1
        )
        print(f"[INFO] UART ouvert sur {UART_PORT}")

    except Exception as e:
        print(f"[ERREUR] Impossible d'ouvrir UART : {e}")
        return

    with open(LOG_FILE, "a") as f:
        print("[INFO] Logging en cours... (CTRL+C pour stop)")

        try:
            while True:
                if ser.in_waiting > 0:
                    data = ser.read(ser.in_waiting)

                    try:
                        text = data.decode('utf-8', errors='ignore')
                    except:
                        text = str(data)

                    f.write(text)
                    f.flush()

        except KeyboardInterrupt:
            print("\n[INFO] Arrêt utilisateur")

    ser.close()
    print("[INFO] UART fermé")


if __name__ == "__main__":
    main()