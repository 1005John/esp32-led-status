# 变更日志

## [v1.0.1] - 2026-06-02

### 新增
- Hermes Agent hooks 支持：`pre_llm_call→busy` / `post_tool_call→busy` / `pre_approval_request→waiting` / `post_llm_call→idle`
- Claude Code `PostToolUse→busy` hook：批准后工具执行完自动切蓝灯
- `esp32-led` CLI 自动检测串口端口（`glob('/dev/cu.usbmodem*')`），适配不同机器

### 修复
- 移除 waiting 模式 5 秒自动超时：未批准时持续红灯闪烁，批准后由 `PostToolUse`/`post_tool_call` hook 主动恢复蓝灯
- Hermes `pre_tool_call` 改为 `pre_llm_call`：解决简单对话（无工具调用）时蓝灯不亮的问题

## [v1.0.0] - 2026-06-02

### 新增
- 初始版本：Claude Code 状态指示器
- ESP32-S3 MicroPython 固件 (main.py)
- 三状态 LED 控制：idle (绿) / busy (蓝) / waiting (红闪)
- CLI 工具 esp32-led
- 串口协议 STATUS:idle|busy|waiting
- 自动启动 (main.py)
