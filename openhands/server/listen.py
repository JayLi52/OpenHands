import os
import debugpy  # 导入 debugpy

import socketio

from openhands.server.app import app as base_app
from openhands.server.listen_socket import sio
from openhands.server.middleware import (
    AttachConversationMiddleware,
    CacheControlMiddleware,
    InMemoryRateLimiter,
    LocalhostCORSMiddleware,
    RateLimitMiddleware,
)
from openhands.server.static import SPAStaticFiles

# 检查环境变量，判断是否以调试模式启动
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
DEBUG_PORT = int(os.getenv("DEBUG_PORT", 5678))

if DEBUG_MODE:
    print(f"Debugger: Waiting for client to attach on port {DEBUG_PORT}...")
    # 监听所有网络接口 (0.0.0.0) 和指定的端口
    debugpy.listen(("0.0.0.0", DEBUG_PORT))
    # 暂停程序执行，直到调试器连接
    debugpy.wait_for_client()
    print("Debugger: Client attached!")

if os.getenv('SERVE_FRONTEND', 'true').lower() == 'true':
    base_app.mount(
        '/', SPAStaticFiles(directory='./frontend/build', html=True), name='dist'
    )

base_app.add_middleware(LocalhostCORSMiddleware)
base_app.add_middleware(CacheControlMiddleware)
base_app.add_middleware(
    RateLimitMiddleware,
    rate_limiter=InMemoryRateLimiter(requests=10, seconds=1),
)
base_app.middleware('http')(AttachConversationMiddleware(base_app))

app = socketio.ASGIApp(sio, other_asgi_app=base_app)
