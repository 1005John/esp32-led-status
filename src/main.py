"""Claude Code / Hermes 状态指示器 — ESP32-S3 GPIO 48 WS2812"""
import sys
import select
import machine
import neopixel
import time

LED_PIN = 48
np = neopixel.NeoPixel(machine.Pin(LED_PIN), 1)

# 颜色定义
GREEN  = (0, 50, 0)
BLUE   = (0, 0, 50)
RED    = (50, 0, 0)
BLACK  = (0, 0, 0)

# 启动：绿色
np[0] = GREEN
np.write()

blink_enabled = False
blink_color = RED
blink_state = False
last_blink = time.ticks_ms()

# 串口轮询
poller = select.poll()
poller.register(sys.stdin, select.POLLIN)

buf = ''

while True:
    now = time.ticks_ms()

    # 闪烁逻辑（持续闪烁直到收到新命令）
    if blink_enabled:
        if time.ticks_diff(now, last_blink) > 400:
            last_blink = now
            blink_state = not blink_state
            np[0] = blink_color if blink_state else BLACK
            np.write()

    # 非阻塞读取串口
    events = poller.poll(50)
    for fd, flag in events:
        if flag & select.POLLIN:
            ch = sys.stdin.read(1)
            if ch == '\n':
                cmd = buf.strip()
                if cmd == 'STATUS:idle':
                    blink_enabled = False
                    np[0] = GREEN
                    np.write()
                    sys.stdout.write('OK: idle\n')
                elif cmd == 'STATUS:busy':
                    blink_enabled = False
                    np[0] = BLUE
                    np.write()
                    sys.stdout.write('OK: busy\n')
                elif cmd == 'STATUS:waiting':
                    blink_enabled = True
                    blink_color = RED
                    sys.stdout.write('OK: waiting\n')
                else:
                    sys.stdout.write('UNKNOWN: ' + cmd + '\n')
                buf = ''
            elif ch not in ('\r', '\x03'):
                buf += ch
