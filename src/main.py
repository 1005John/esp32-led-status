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
waiting_start = 0  # 进入 waiting 模式的时间戳
WAITING_TIMEOUT = 5000  # 5 秒后自动恢复 busy

# 串口轮询
poller = select.poll()
poller.register(sys.stdin, select.POLLIN)

buf = ''

while True:
    now = time.ticks_ms()

    # 闪烁逻辑
    if blink_enabled:
        # 超时自动恢复：5 秒无新命令 → busy
        if time.ticks_diff(now, waiting_start) > WAITING_TIMEOUT:
            blink_enabled = False
            np[0] = BLUE
            np.write()
            sys.stdout.write('TIMEOUT: auto-revert to busy\n')
        elif time.ticks_diff(now, last_blink) > 400:
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
                    waiting_start = now
                    sys.stdout.write('OK: waiting\n')
                else:
                    sys.stdout.write('UNKNOWN: ' + cmd + '\n')
                buf = ''
            elif ch not in ('\r', '\x03'):
                buf += ch
