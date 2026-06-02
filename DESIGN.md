# ESP32 LED Status — 系统设计

> 版本：v1.0.1 | 日期：2026-06-02

## 1. 架构概览

```
┌──────────────┐    串口命令       ┌──────────────────┐
│  Claude Code  │  ─────────────→  │  ESP32-S3 (MP)   │
│  + Hermes     │  STATUS:idle     │  GPIO 48 WS2812  │
│              │  STATUS:busy     │                  │
│  esp32-led   │  STATUS:waiting  │  🔵🔴🟢 LED      │
└──────────────┘                  └──────────────────┘
```

### 双工具协作

Claude Code 和 Hermes 共享同一块 ESP32，各自通过 hooks 控制 LED。串口写入极短（微秒级），不会冲突。

## 2. 通信协议

| 命令 | 响应 | LED 行为 |
|------|------|----------|
| `STATUS:idle` | `OK: idle` | 绿色常亮 |
| `STATUS:busy` | `OK: busy` | 蓝色常亮 |
| `STATUS:waiting` | `OK: waiting` | 红色闪烁 (400ms 周期)，持续到收到新命令 |

- 物理层：USB-Serial/JTAG, 115200 baud
- 格式：文本命令，`\n` 换行
- 容错：未知命令返回 `UNKNOWN: xxx`，LED 保持不变

## 3. Hook 设计

### Claude Code

| Hook | 命令 | 时机 |
|------|------|------|
| `UserPromptSubmit` | busy | 用户发送消息时 |
| `PostToolUse` | busy | 任何工具执行完成后（含批准后的工具） |
| `PermissionRequest` | waiting | 需要用户授权时 |
| `Stop` | idle | 轮次结束，等待用户输入 |

**授权后恢复流程**：
```
PermissionRequest → 红灯闪烁
  → 用户批准 → 工具执行 → PostToolUse → busy → 蓝灯
  → 用户拒绝 → 红灯持续闪烁（直到 Stop→idle 或下轮 UserPromptSubmit→busy）
```

### Hermes

| Hook | 命令 | 时机 |
|------|------|------|
| `pre_llm_call` | busy | 任何 LLM 调用前（含简单对话） |
| `post_tool_call` | busy | 工具执行完成后（含批准后的工具） |
| `pre_approval_request` | waiting | 需要用户授权时 |
| `post_llm_call` | idle | LLM 回复完成，等待用户输入 |

**为何用 `pre_llm_call` 而非 `pre_tool_call`**：
简单对话（如"你好"）不触发 `pre_tool_call`，导致蓝灯从未亮起。`pre_llm_call` 在每次 LLM 调用前都触发。

## 4. 固件设计

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
         │ WAITING  │ ← 持续闪烁直到收到 busy/idle
         │  红灯闪烁 │
         └──────────┘
```

### 主循环

```
boot → 初始化 WS2812 → 绿灯
  └→ loop:
       ├ 闪烁逻辑 (400ms 周期，仅在 waiting 状态)
       └ select.poll(50ms) → 读取串口 → 解析命令 → 切换状态
```

### 闪烁可持续性

waiting 模式无自动超时——持续闪烁直到外部发送 `STATUS:busy` 或 `STATUS:idle`。恢复由 hook（`PostToolUse`/`post_tool_call`）负责。

## 5. CLI 工具

`tools/esp32-led` — Python 3 脚本，自动检测 `/dev/cu.usbmodem*` 端口，`os.write` 直写串口。零依赖（标准库），静默失败。

## 6. 关键决策

| 决策 | 原因 |
|------|------|
| MicroPython 而非 C | 快速开发，无需工具链 |
| select.poll 而非 sys.stdin.readline | 非阻塞读取，不影响 LED 闪烁 |
| os.write 而非 pySerial | 零依赖，避免文件锁冲突 |
| waiting 无超时 + hook 恢复 | 未批准一直闪，批准由 hook 切回 busy |
| 串口端口自动检测 | 不同机器/不同 USB 口端口号不同 |
| 双工具共享同一 ESP32 | 串口写入极短，实际不会冲突 |
