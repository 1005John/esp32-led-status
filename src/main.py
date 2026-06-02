"""Claude Code / Hermes 状态指示器 — WiFi + USB 双通道"""
import sys, select, machine, neopixel, time, network, socket, json

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

# ── WiFi 连接 ──
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
try:
    import wifi_cfg
    wlan.connect(wifi_cfg.SSID, wifi_cfg.PASSWORD)
    for _ in range(30):  # 15 秒超时
        if wlan.isconnected():
            break
        time.sleep_ms(500)
except Exception as e:
    pass

http_ip = ''
if wlan.isconnected():
    http_ip = wlan.ifconfig()[0]
    # LED 短暂闪蓝 3 次表示 WiFi OK
    for _ in range(3):
        np[0] = BLUE; np.write(); time.sleep_ms(200)
        np[0] = BLACK; np.write(); time.sleep_ms(200)
    set_led(GREEN)

# ── HTTP 服务 ──
http_sock = None
try:
    http_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    http_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    http_sock.bind(('0.0.0.0', 80))
    http_sock.listen(2)
    http_sock.settimeout(0.1)  # 阻塞 accept，100ms 超时
except Exception:
    http_sock = None

def handle_http():
    if http_sock is None:
        return
    try:
        conn, addr = http_sock.accept()
    except OSError:
        return  # 超时，无连接
    try:
        conn.settimeout(1.0)
        req = conn.recv(512).decode('utf-8', errors='ignore')
        if '/busy' in req:       set_led(BLUE)
        elif '/waiting' in req:  set_led(RED, do_blink=True)
        elif '/idle' in req:     set_led(GREEN)
        elif '/status' in req:
            data = json.dumps({'color': 'red' if blink_enabled else ('green' if led_color == GREEN else 'blue'), 'blink': blink_enabled})
            conn.send(f'HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n\r\n{data}')
            conn.close()
            return
        conn.send('HTTP/1.0 200 OK\r\n\r\nOK')
    except Exception:
        pass
    try:
        conn.close()
    except Exception:
        pass

# ── USB 串口监听（如果 USB 连接着就用） ──
def handle_usb(buf=''):
    pass  # placeholder — USB listener below

# ── 主循环 ──
poller = select.poll()
poller.register(sys.stdin, select.POLLIN)
buf = ''

while True:
    tick_blink()
    handle_http()

    # USB 串口（非阻塞，USB 不在就跳过）
    try:
        events = poller.poll(20)
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
    except Exception:
        time.sleep_ms(100)  # USB 不可用时降速
