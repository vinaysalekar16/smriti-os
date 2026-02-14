from evdev import InputDevice, categorize, ecodes
import subprocess, time, signal, sys, os

DEVICE = "/dev/input/event4"
# --- CURSOR SPEED TUNING ---
TAP_STEP = 18        # small move for single press (precision)
HOLD_STEP = 70       # fast move when holding button
HOLD_THRESHOLD = 0.35   # seconds before hold mode activates
REPEAT_RATE = 0.01      # repeat speed while holding

# --- KEYBOARD NAVIGATION SPEED ---
KEY_TAP_DELAY = 0.25     # delay before repeat starts
KEY_REPEAT_RATE = 0.06   # repeat speed while holding
key_hold_start = {}
key_last_repeat = {}


DEBOUNCE = 0.35

os.environ["YDOTOOL_SOCKET"] = "/tmp/ydotool.socket"

dev = InputDevice(DEVICE)
dev.grab()   # IMPORTANT: block keys from reaching Chromium

last_time = {}
last_mouse_time = 0
hold_start_time = 0

def ykey(code):
    subprocess.run(["ydotool", "key"] + code.split(), stdout=subprocess.DEVNULL)

def ymouse(x, y):
    subprocess.run(["ydotool", "mousemove", "--", str(x), str(y)], stdout=subprocess.DEVNULL)

def yclick():
    # 0xC0 is Left Click Down+Up
    subprocess.run(["ydotool", "click", "0xC0"], stdout=subprocess.DEVNULL)

def allowed(key):
    now = time.time()
    if now - last_time.get(key, 0) > DEBOUNCE:
        last_time[key] = now
        return True
    return False

def handle_key_repeat(key_name, keycode):
    now = time.time()

    if key_name not in key_hold_start:
        key_hold_start[key_name] = now
        ykey(keycode)
        return

    # wait before starting repeat
    if now - key_hold_start[key_name] < KEY_TAP_DELAY:
        return

    # repeat while holding
    if now - key_last_repeat.get(key_name, 0) > KEY_REPEAT_RATE:
        key_last_repeat[key_name] = now
        ykey(keycode)


print("SMRITI Remote Engine Running (TOML Listener)")

for event in dev.read_loop():
    # Listen for Key events (value 1=press, 2=hold)
    if event.type != ecodes.EV_KEY:
        continue

    key = categorize(event).keycode
    print("KEY PRESSED:", key)

    # Reset hold when button released
    if event.value == 0:
        key_hold_start.pop(key, None)
        key_last_repeat.pop(key, None)
        hold_start_time = 0
        continue

    # --- MOUSE (ARROWS) ---
    if key in ["KEY_UP", "KEY_DOWN", "KEY_LEFT", "KEY_RIGHT"]:
        now = time.time()

        # First press → start hold timer
        if hold_start_time == 0:
            hold_start_time = now
            step = TAP_STEP   # precision movement

        else:
            # After threshold → switch to hold speed
            if now - hold_start_time > HOLD_THRESHOLD:
                if now - last_mouse_time < REPEAT_RATE:
                    continue
                last_mouse_time = now
                step = HOLD_STEP
            else:
                step = TAP_STEP

        if key == "KEY_UP":    ymouse(0, -step)
        elif key == "KEY_DOWN":  ymouse(0, step)
        elif key == "KEY_LEFT":  ymouse(-step, 0)
        elif key == "KEY_RIGHT": ymouse(step, 0)

        continue

    hold_start_time = 0
    if not allowed(key): continue

    # --- OK (CLICK + ENTER) ---
    if key == "KEY_ENTER":
        yclick()
        ykey("28:1 28:0")

    # --- UI NAVIGATION ---
    elif key == "KEY_VOLUMEUP":
        handle_key_repeat("UP", "103:1 103:0")

    elif key == "KEY_VOLUMEDOWN":
        handle_key_repeat("DOWN", "108:1 108:0")

    elif key == "KEY_PAGEUP":
        handle_key_repeat("RIGHT", "106:1 106:0")

    elif key == "KEY_PAGEDOWN":
        handle_key_repeat("LEFT", "105:1 105:0")

    # --- SYSTEM ---
    elif key == "KEY_BACKSPACE":  ykey("56:1 105:1 105:0 56:0")     # Esc
    elif key == "KEY_HOME":       ykey("56:1 2:1 2:0 56:0") # Alt+1
    elif key == "KEY_POWER":      subprocess.run(["sudo", "shutdown", "-h", "now"])
    elif key == "KEY_PROG1":      subprocess.run(["sudo", "reboot"])



def cleanup(sig, frame):
    try:
        dev.ungrab()
    except:
        pass
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)
