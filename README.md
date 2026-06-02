# ESP32 LED Status — AI 工具联动指示灯

通过 ESP32-S3 板载 WS2812 LED 实时显示 Claude Code / Hermes 工作状态。

## 功能

| 状态 | LED 表现 | 含义 |
|------|----------|------|
| 🟢 绿色常亮 | idle | 任务完成，等待输入 |
| 🔵 蓝色常亮 | busy | 工作中（读文件/写代码/执行命令） |
| 🔴 红色闪烁 | waiting | 需要用户确认或授权 |

## 支持的工具

| 工具 | busy hook | waiting hook | idle hook |
|------|-----------|--------------|-----------|
| Claude Code | `UserPromptSubmit` + `PostToolUse` | `PermissionRequest` | `Stop` |
| Hermes | `pre_llm_call` + `post_tool_call` | `pre_approval_request` | `post_llm_call` |

## 硬件

- **芯片**：ESP32-S3-N16R8 (QFN56, 16MB Flash, 8MB Octal PSRAM)
- **LED**：板载 WS2812 可寻址 RGB，GPIO 48
- **通信**：USB-Serial/JTAG，端口 `/dev/cu.usbmodem*`
- **固件**：MicroPython v1.28.0 (Octal-SPIRAM)

## 快速开始

```bash
# 1. 烧录 MicroPython 固件
#    按住 BOOT → 按 RST → 松开 BOOT → 进入下载模式
esptool.py --port /dev/cu.usbmodem* --chip esp32s3 write_flash -z 0x0 \
  ESP32_GENERIC_S3-SPIRAM_OCT-20260406-v1.28.0.bin
#    按 RST 正常启动

# 2. 上传控制脚本
mpremote connect /dev/cu.usbmodem* fs cp src/main.py :main.py
mpremote connect /dev/cu.usbmodem* reset

# 3. 安装 CLI 工具
ln -sf $(pwd)/tools/esp32-led ~/bin/esp32-led

# 4. 配置 hooks（见 CLAUDE.md）
#    Claude Code: ~/.claude/settings.json
#    Hermes:      ~/.hermes/config.yaml

# 5. 测试
esp32-led busy     # 工作中
esp32-led waiting  # 等授权
esp32-led idle     # 空闲

# 6. 重启 AI 工具，hooks 生效
```

## 目录结构

```
esp32-led-status/
├── src/main.py           ← ESP32 固件（MicroPython）
├── tools/esp32-led       ← CLI 控制脚本（自动检测端口）
├── README.md
├── DESIGN.md
├── REQUIREMENTS.md
├── CHANGELOG.md
└── CLAUDE.md
```

## 技术栈

| 层级 | 技术 |
|------|------|
| MCU 固件 | MicroPython v1.28.0 |
| LED 驱动 | neopixel (MicroPython 内置) |
| 通信协议 | USB-Serial (115200 baud) |
| CLI 控制 | Python 3 + os.write |
| AI 集成 | Claude Code hooks + Hermes hooks |
