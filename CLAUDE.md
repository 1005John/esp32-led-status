# ESP32 LED Status — Claude Code 项目指令

## 项目信息

- **版本**：v1.1.0
- **用途**：ESP32-S3 WS2812 LED 显示 AI 工具工作状态
- **硬件**：ESP32-S3-N16R8, GPIO 48, WS2812
- **固件**：MicroPython v1.28.0 Octal-SPIRAM
- **通道**：USB 串口（主） + WiFi HTTP（备）
- **支持工具**：Claude Code + Hermes

## 文件位置

| 文件 | 说明 |
|------|------|
| `src/main.py` | ESP32 固件，上传后自动运行 |
| `src/wifi_cfg.example.py` | WiFi 配置模板（复制为 wifi_cfg.py，已 gitignore） |
| `tools/esp32-led` | CLI 控制脚本 → `~/bin/esp32-led` |

## ⚠️ 文档同步约束

每次代码修改后检查并同步：
1. `REQUIREMENTS.md` — 功能需求状态
2. `DESIGN.md` — 架构/Hook 表
3. `CHANGELOG.md` — 变更记录

## 开发命令

```bash
# 上传固件
mpremote connect /dev/cu.usbmodem* fs cp src/main.py :main.py
mpremote connect /dev/cu.usbmodem* fs cp src/wifi_cfg.py :wifi_cfg.py
mpremote connect /dev/cu.usbmodem* reset  # 外置供电时可用

# 测试 LED
~/bin/esp32-led idle|busy|waiting

# 测试 HTTP（需要 WiFi 连上 + IP 可达）
curl http://192.168.3.229/status
curl http://192.168.3.229/busy
```

## Hook 配置

### Claude Code (`~/.claude/settings.json`)
```json
"hooks": {
  "UserPromptSubmit":    [{"hooks": [{"type": "command", "command": "esp32-led busy"}]}],
  "ElicitationResult":   [{"hooks": [{"type": "command", "command": "esp32-led busy"}]}],
  "PostToolUse":         [{"hooks": [{"type": "command", "command": "esp32-led busy"}]}],
  "PermissionRequest":   [{"hooks": [{"type": "command", "command": "esp32-led waiting"}]}],
  "Stop":                [{"hooks": [{"type": "command", "command": "esp32-led idle"}]}]
}
```

### Hermes (`~/.hermes/config.yaml`)
```yaml
hooks:
  pre_llm_call:         [command: esp32-led busy]
  post_tool_call:       [command: esp32-led busy]
  pre_approval_request: [command: esp32-led waiting]
  post_llm_call:        [command: esp32-led idle]
hooks_auto_accept: true
```

## 烧录新设备

1. 按住 BOOT → 按 RST → 松开 BOOT（下载模式）
2. `esptool.py --port /dev/cu.usbmodem* --chip esp32s3 write_flash -z 0x0 firmware.bin`
3. 按 RST 正常启动
4. `mpremote connect /dev/cu.usbmodem* fs cp src/main.py :main.py`
5. 复制 `wifi_cfg.example.py` → `wifi_cfg.py`，填入 WiFi SSID/密码
6. `mpremote connect /dev/cu.usbmodem* fs cp src/wifi_cfg.py :wifi_cfg.py`
7. 按 RST 重启
8. 扫描 GPIO：`mpremote exec "import neopixel,machine;..."` 确认 LED 引脚
9. 获取 WiFi IP：启动后 LED 蓝闪 3 次 = WiFi 已连，通过串口读 IP
10. `echo "IP地址" > ~/.esp32-led-ip`
