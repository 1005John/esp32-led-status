# ESP32 LED Status — 系统设计

> 版本：v1.0 | 日期：2026-06-02

## 1. 架构概览

```
┌─────────────┐    串口命令       ┌──────────────────┐
│  Claude Code │  ─────────────→  │  ESP32-S3 (MP)   │
│  (Mac mini)  │  STATUS:idle     │  GPIO 48 WS2812  │
│              │  STATUS:busy     │                  │
│  esp32-led   │  STATUS:waiting  │  🔵🔴🟢 LED      │
└─────────────┘                  └──────────────────┘
```

## 2. 通信协议

| 命令 | 响应 | LED 行为 |
|------|------|----------|
| `STATUS:idle` | `OK: idle` | 绿色常亮 |
| `STATUS:busy` | `OK: busy` | 蓝色常亮 |
| `STATUS:waiting` | `OK: waiting` | 红色闪烁 (400ms 周期) |

- 物理层：USB-Serial/JTAG, 115200 baud
- 格式：文本命令，`\n` 换行
- 容错：未知命令返回 `UNKNOWN: xxx`，LED 保持不变

## 3. 固件设计

### 主循环

```
boot → 初始化 WS2812 → 绿灯
  └→ loop:
       ├ 闪烁逻辑 (400ms 周期，仅在 waiting 状态)
       └ select.poll(50ms) → 读取串口 → 解析命令 → 切换状态
```

### 状态机

```
         ┌──────────┐
         │   IDLE   │ ← 启动默认
         │  绿灯常亮 │
         └────┬─────┘
              │ STATUS:busy
              ▼
         ┌──────────┐
         │   BUSY   │
         │  蓝灯常亮 │
         └────┬─────┘
              │ STATUS:waiting
              ▼
         ┌──────────┐
         │ WAITING  │
         │  红灯闪烁 │
         └────┬─────┘
              │ STATUS:idle
              ▼
         ┌──────────┐
         │   IDLE   │
         └──────────┘
```

## 4. CLI 工具

`tools/esp32-led` — Python 脚本，通过 `os.open(PORT, O_WRONLY)` 直接写串口，无依赖（除 Python 3 标准库），静默失败不影响 Claude Code。

## 5. 关键决策

| 决策 | 原因 |
|------|------|
| MicroPython 而非 C | 快速开发，无需工具链 |
| select.poll 而非 sys.stdin.readline | 非阻塞读取，不影响 LED 闪烁 |
| os.write 而非 pySerial | 零依赖，避免文件锁冲突 |
| 静默失败 | LED 是辅助功能，不应影响主工作流 |
