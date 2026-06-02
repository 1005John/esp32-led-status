# 变更日志

## [v1.0.0] - 2026-06-02

### 新增
- 初始版本：Claude Code 状态指示器
- ESP32-S3 MicroPython 固件 (main.py)
- 三状态 LED 控制：idle (绿) / busy (蓝) / waiting (红闪)
- CLI 工具 esp32-led
- 串口协议 STATUS:idle|busy|waiting
- 自动启动 (boot.py → main.py)
