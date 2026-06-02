# ESP32 LED Status — AI 工具联动指示灯

ESP32-S3 WS2812 LED 实时显示 Claude Code / Hermes 工作状态。USB 串口 + WiFi HTTP 双通道。

## 功能

| 状态 | LED | 含义 |
|------|-----|------|
| 🟢 绿色常亮 | idle | 任务完成，等待输入 |
| 🔵 蓝色常亮 | busy | 工作中 |
| 🔴 红色闪烁 | waiting | 需要用户授权 |

## 通道

| 通道 | 优先级 | 适用场景 |
|------|:---:|------|
| USB 串口 | 1 | 本机连接（零延迟） |
| WiFi HTTP | 2 | 远程 / 无 USB 数据线 |

`esp32-led` CLI 自动选择：USB 可用→走 USB，否则→HTTP。

## 硬件

- **芯片**：ESP32-S3-N16R8
- **LED**：WS2812 GPIO 48
- **固件**：MicroPython v1.28.0 Octal-SPIRAM
- **供电**：推荐 USB 数据 + 外置电源适配器（WiFi 稳定）

## 快速开始

```bash
# 1. 烧录固件
esptool.py --port /dev/cu.usbmodem* --chip esp32s3 write_flash -z 0x0 firmware.bin

# 2. 上传控制脚本
mpremote connect /dev/cu.usbmodem* fs cp src/main.py :main.py
cp src/wifi_cfg.example.py src/wifi_cfg.py  # 编辑填入 WiFi 信息
mpremote connect /dev/cu.usbmodem* fs cp src/wifi_cfg.py :wifi_cfg.py

# 3. CLI 工具
ln -sf $(pwd)/tools/esp32-led ~/bin/esp32-led

# 4. 配置 hooks（见 CLAUDE.md）

# 5. 测试
esp32-led busy     # 🔵 工作中
esp32-led waiting  # 🔴 等授权
esp32-led idle     # 🟢 空闲
```

## 目录

```
esp32-led-status/
├── src/main.py              ← ESP32 固件
├── src/wifi_cfg.example.py  ← WiFi 配置模板
├── tools/esp32-led          ← CLI 控制脚本
├── README.md / DESIGN.md / REQUIREMENTS.md / CHANGELOG.md / CLAUDE.md
└── .gitignore
```

## 支持的工具

| 工具 | busy hook | waiting hook | idle hook |
|------|-----------|--------------|-----------|
| Claude Code | `UserPromptSubmit` + `PostToolUse` | `PermissionRequest` | `Stop` |
| Hermes | `pre_llm_call` + `post_tool_call` | `pre_approval_request` | `post_llm_call` |
