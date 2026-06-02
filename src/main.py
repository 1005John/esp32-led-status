import sys, select, machine, neopixel, time, network, socket, json

LED_PIN = 48
np = neopixel.NeoPixel(machine.Pin(LED_PIN), 1)
GREEN=(0,50,0); BLUE=(0,0,50); RED=(50,0,0); BLACK=(0,0,0)
blink_enabled=False; blink_color=RED; blink_state=False
last_blink=time.ticks_ms(); led_color=GREEN

def set_led(c, b=False):
    global led_color, blink_enabled, blink_color, blink_state
    led_color=c; blink_enabled=b; blink_color=c; blink_state=True
    np[0]=blink_color if b and blink_state else (BLACK if b else c); np.write()

def tick_blink():
    global blink_state, last_blink
    if not blink_enabled: return
    n=time.ticks_ms()
    if time.ticks_diff(n,last_blink)>400: last_blink=n; blink_state=not blink_state
    np[0]=blink_color if blink_state else BLACK; np.write()

set_led(GREEN)

# WiFi
wlan=network.WLAN(network.STA_IF); wlan.active(True)
try:
    import wifi_cfg
    wlan.connect(wifi_cfg.SSID,wifi_cfg.PASSWORD)
    for _ in range(30):
        if wlan.isconnected(): break
        time.sleep_ms(500)
except: pass

if wlan.isconnected():
    for _ in range(3): np[0]=BLUE; np.write(); time.sleep_ms(200); np[0]=BLACK; np.write(); time.sleep_ms(200)
    set_led(GREEN)

# HTTP — 用 settimeout 不用 setblocking
http_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
http_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
http_sock.bind(('0.0.0.0', 80))
http_sock.listen(2)
http_sock.settimeout(0.1)

def handle_http():
    global http_sock
    try:
        conn, addr = http_sock.accept()
    except OSError:
        return
    # 收到连接，读数据
    req = b''
    for _ in range(10):
        try:
            chunk = conn.recv(512)
            if chunk: req += chunk; break
        except: pass
        time.sleep_ms(100)
    if req:
        t = req.decode('utf-8','ignore')
        if '/busy' in t: set_led(BLUE)
        elif '/waiting' in t: set_led(RED,do_blink=True)
        elif '/idle' in t: set_led(GREEN)
        elif '/status' in t:
            d=json.dumps({'color':'red' if blink_enabled else ('green' if led_color==GREEN else 'blue'),'blink':blink_enabled})
            conn.send(b'HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n\r\n'+d.encode())
            conn.close(); return
        conn.send(b'HTTP/1.0 200 OK\r\n\r\nOK')
    conn.close()

# USB
poller=select.poll(); poller.register(sys.stdin,select.POLLIN); buf=''

while True:
    tick_blink()
    handle_http()
    try:
        ev=poller.poll(20)
        for fd,f in ev:
            if f&select.POLLIN:
                ch=sys.stdin.read(1)
                if ch=='\n':
                    c=buf.strip()
                    if c=='STATUS:idle': set_led(GREEN); sys.stdout.write('OK: idle\n')
                    elif c=='STATUS:busy': set_led(BLUE); sys.stdout.write('OK: busy\n')
                    elif c=='STATUS:waiting': set_led(RED,do_blink=True); sys.stdout.write('OK: waiting\n')
                    else: sys.stdout.write('UNKNOWN: '+c+'\n')
                    buf=''
                elif ch not in('\r','\x03'): buf+=ch
    except: time.sleep_ms(100)
