# ESP32 LED Status — Claude Code 项目指令

## 项目信息

- **名称**：esp32-led-status
- **用途**：通过 ESP32-S3 WS2812 LED 显示 Claude Code / Hermes 工作状态
- **硬件**：ESP32-S3-N16R8, GPIO 48, WS2812
- **固件**：MicroPython v1.28.0 Octal-SPIRAM
- **支持工具**：Claude Code + Hermes Agent

## 文件位置

| 文件 | 说明 |
|------|------|
| `src/main.py` | ESP32 固件，上传后自动运行 |
| `tools/esp32-led` | CLI 控制脚本，链接到 `~/bin/` |

## ⚠️ 文档同步约束

每次代码修改后，检查并同步：
1. `REQUIREMENTS.md` — 功能需求状态
2. `DESIGN.md` — 架构/模块/决策、Hook 表
3. `CHANGELOG.md` — 变更记录

## Hook 配置

### Claude Code (`~/.claude/settings.json`)
```json
"hooks": {
  "UserPromptSubmit": [{"hooks": [{"type": "command", "command": "...esp32-led busy"}]}],
  "PostToolUse":      [{"hooks": [{"type": "command", "command": "...esp32-led busy"}]}],
  "PermissionRequest": [{"hooks": [{"type": "command", "command": "...esp32-led waiting"}]}],
  "Stop":             [{"hooks": [{"type": "command", "command": "...esp32-led idle"}]}]
}
```

### Hermes (`~/.hermes/config.yaml`)
```yaml
hooks:
  pre_llm_call:
  - command: /Users/john/bin/esp32-led busy
  post_tool_call:
  - command: /Users/john/bin/esp32-led busy
  pre_approval_request:
  - command: /Users/john/bin/esp32-led waiting
  post_llm_call:
  - command: /Users/john/bin/esp32-led idle
hooks_auto_accept: true
```

## 开发命令

```bash
# 上传固件
mpremote connect /dev/cu.usbmodem* fs cp src/main.py :main.py
mpremote connect /dev/cu.usbmodem* reset

# 实时调试
mpremote connect /dev/cu.usbmodem* exec "print('test')"

# 测试 LED
~/bin/esp32-led idle|busy|waiting
```

## 烧录新设备

1. 下载 MicroPython 固件（Octal-SPIRAM 版本）
2. 按住 BOOT → 按 RST → 松开 BOOT（进入下载模式）
3. `esptool.py --port /dev/cu.usbmodemXXX --chip esp32s3 write_flash -z 0x0 firmware.bin`
4. 按 RST 正常启动
5. `mpremote connect /dev/cu.usbmodemXXX fs cp src/main.py :main.py`
6. 按 RST 重启
7. 扫描 GPIO 确认 LED 引脚：`mpremote exec "..."` 测试
