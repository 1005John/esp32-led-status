"""Claude Code / Hermes 状态指示器 — USB 串口控制"""
import sys, select, machine, neopixel, time

LED_PIN = 48
np = neopixel.NeoPixel(machine.Pin(LED_PIN), 1)

GREEN  = (0, 50, 0)
BLUE   = (0, 0, 50)
RED    = (50, 0, 0)
BLACK  = (0, 0, 0)

blink_enabled = False
blink_color = RED
blink_state = False
last_blink = time.ticks_ms()
led_color = GREEN

def set_led(color, do_blink=False):
    global led_color, blink_enabled, blink_color, blink_state
    led_color = color
    blink_enabled = do_blink
    blink_color = color
    blink_state = True
    _apply()

def _apply():
    if blink_enabled:
        np[0] = blink_color if blink_state else BLACK
    else:
        np[0] = led_color
    np.write()

def tick_blink():
    global blink_state, last_blink
    if not blink_enabled:
        return
    now = time.ticks_ms()
    if time.ticks_diff(now, last_blink) > 400:
        last_blink = now
        blink_state = not blink_state
        _apply()

# ── 启动绿灯 ──
set_led(GREEN)

# ── USB 串口监听 ──
poller = select.poll()
poller.register(sys.stdin, select.POLLIN)
buf = ''

while True:
    tick_blink()
    events = poller.poll(50)
    for fd, flag in events:
        if flag & select.POLLIN:
            ch = sys.stdin.read(1)
            if ch == '\n':
                cmd = buf.strip()
                if cmd == 'STATUS:idle':
                    set_led(GREEN)
                    sys.stdout.write('OK: idle\n')
                elif cmd == 'STATUS:busy':
                    set_led(BLUE)
                    sys.stdout.write('OK: busy\n')
                elif cmd == 'STATUS:waiting':
                    set_led(RED, do_blink=True)
                    sys.stdout.write('OK: waiting\n')
                else:
                    sys.stdout.write('UNKNOWN: ' + cmd + '\n')
                buf = ''
            elif ch not in ('\r', '\x03'):
                buf += ch
