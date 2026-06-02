# 变更日志

## [v1.1.0] - 2026-06-02

### 新增
- WiFi + HTTP 控制通道：ESP32 连接 WiFi 后在 80 端口提供 HTTP API
- CLI 双通道回退：USB 优先 → HTTP 备选（读取 `~/.esp32-led-ip`）
- 外置供电 + USB 数据双连接方案（解决 WiFi 功耗导致 USB 掉线）
- 启动时 LED 闪蓝 3 次表示 WiFi 连接成功
- `src/wifi_cfg.example.py` 配置模板
- `/status` HTTP 端点返回 JSON 状态

### 修复
- WiFi 初始化延迟到启动 5 秒后（避免 USB 枚举期间掉线）
- 移除 `_thread`，HTTP 用阻塞 socket + 100ms 超时集成到主循环
- USB 不可用时主循环自动降速不崩溃

## [v1.0.1] - 2026-06-02

### 新增
- Hermes Agent hooks 支持
- Claude Code `PostToolUse→busy` hook
- `esp32-led` CLI 自动检测串口端口

### 修复
- 移除 waiting 模式 5 秒自动超时
- Hermes `pre_tool_call` 改为 `pre_llm_call`

## [v1.0.0] - 2026-06-02

### 新增
- 初始版本：Claude Code 状态指示器
- ESP32-S3 MicroPython 固件 (main.py)
- 三状态 LED 控制：idle / busy / waiting
- CLI 工具 esp32-led
- 串口协议 STATUS:idle|busy|waiting
