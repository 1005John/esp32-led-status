# ESP32 LED Status — 系统设计

> 版本：v1.1.0 | 日期：2026-06-02

## 1. 架构概览

```
                ┌─ USB 串口：STATUS:xxx  ─┐
Claude Code ───┤                          ├──→ ESP32-S3 ──→ WS2812 GPIO 48
/ Hermes       └─ HTTP API：GET /xxx    ─┘        │
                                                  │ WiFi STA
                                                  │ STA_IF
                                           ┌──────┴──────┐
                                           │ 路由器 / AP  │
                                           └─────────────┘
```

### 通道优先级

| 优先级 | 通道 | 触发条件 |
|:---:|------|------|
| 1 | USB 串口 | `/dev/cu.usbmodem*` 存在 |
| 2 | HTTP (WiFi) | USB 不可用 + `~/.esp32-led-ip` 存在 |

双重供电（USB 数据 + 外部电源适配器）解决 WiFi 功耗导致 USB 掉线问题。

## 2. 通信协议

### USB 串口

| 命令 | 响应 | LED 行为 |
|------|------|----------|
| `STATUS:idle` | `OK: idle` | 绿色常亮 |
| `STATUS:busy` | `OK: busy` | 蓝色常亮 |
| `STATUS:waiting` | `OK: waiting` | 红色闪烁 |

### HTTP API

| 端点 | 方法 | 响应 |
|------|------|------|
| `/busy` | GET | `OK` (蓝灯) |
| `/waiting` | GET | `OK` (红闪) |
| `/idle` | GET | `OK` (绿灯) |
| `/status` | GET | `{"color":"green/blue/red","blink":false/true}` |

## 3. 固件设计

### 启动流程

```
boot → GPIO 48 WS2812 init → 绿灯
  ↓
  ├─ USB 串口监听（立即可用，select.poll）
  ├─ WiFi 连接（启动后立即连接）
  │   └─ 成功 → 蓝闪 3 次 → HTTP 服务器（socket 80 端口，100ms 超时）
  └─ 主循环（20ms 周期）
       ├ tick_blink()     — 闪烁逻辑
       ├ handle_http()    — HTTP accept + recv + 响应
       └ select.poll(20)  — USB 串口（try-except 容错）
```

### WiFi 失败容错

WiFi 连接失败或 HTTP socket 绑定失败时，USB 串口正常工作。主循环中轮询 socket 的错误被静默捕获。

## 4. Hook 设计

### Claude Code

| Hook | 命令 | 时机 |
|------|------|------|
| `UserPromptSubmit` | busy | 用户发送消息 |
| `PostToolUse` | busy | 工具执行完成（含批准后恢复） |
| `PermissionRequest` | waiting | 需要用户授权 |
| `Stop` | idle | 轮次结束 |

### Hermes

| Hook | 命令 | 时机 |
|------|------|------|
| `pre_llm_call` | busy | LLM 调用前 |
| `post_tool_call` | busy | 工具执行完成 |
| `pre_approval_request` | waiting | 需要用户授权 |
| `post_llm_call` | idle | LLM 回复完成 |

## 5. CLI 工具

`tools/esp32-led` — 双通道自动回退：

```
1. glob('/dev/cu.usbmodem*') → os.write(STATUS:xxx)   [USB]
2. ~/.esp32-led-ip 存在 → urllib GET /xxx              [HTTP]
3. 都失败 → stderr 报错，exit 1
```

## 6. 关键决策

| 决策 | 原因 |
|------|------|
| USB 优先，HTTP 备选 | USB 零延迟零配置，HTTP 用于远程 |
| 阻塞 socket + 100ms 超时 | 比 setblocking(False) + try-except 更可靠 |
| 不用 `_thread` | ESP32-S3 MicroPython 的线程 + WiFi 导致启动崩溃 |
| 外置供电 + USB 数据 | WiFi TX 功耗大时 USB 不掉线 |
| wifi_cfg.py 不入库 | WiFi 密码不应提交到 Git |
| 串口端口自动检测 | 不同 Mac / USB 口端口号不同 |
