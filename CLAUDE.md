# ESP32 LED Status — Claude Code 项目指令

## 项目信息

- **名称**：esp32-led-status
- **用途**：通过 ESP32-S3 WS2812 LED 显示 Claude Code 工作状态
- **硬件**：ESP32-S3-N16R8, GPIO 48, WS2812
- **固件**：MicroPython v1.28.0 Octal-SPIRAM

## 文件位置

| 文件 | 说明 |
|------|------|
| `src/main.py` | ESP32 固件，上传后自动运行 |
| `tools/esp32-led` | CLI 控制脚本，链接到 `~/bin/` |

## ⚠️ 文档同步约束

每次代码修改后，检查并同步：
1. `REQUIREMENTS.md` — 功能需求状态
2. `DESIGN.md` — 架构/模块/决策
3. `CHANGELOG.md` — 变更记录

## 开发命令

```bash
# 上传固件
mpremote connect /dev/cu.usbmodem1101 fs cp src/main.py :main.py
mpremote connect /dev/cu.usbmodem1101 reset

# 实时调试
mpremote connect /dev/cu.usbmodem1101 exec "print('test')"

# 测试 LED
~/bin/esp32-led idle|busy|waiting
```

## 烧录新设备

1. 下载 MicroPython 固件（Octal-SPIRAM 版本）
2. `esptool.py --port /dev/cu.usbmodemXXX --chip esp32s3 write-flash -z 0x0 firmware.bin`
3. `mpremote connect /dev/cu.usbmodemXXX fs cp src/main.py :main.py`
4. 按 RST 键重启
