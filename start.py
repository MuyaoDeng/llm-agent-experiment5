"""
统一启动脚本 - 同时启动前后端服务
"""
import subprocess
import sys
import time
import os
from threading import Thread

def start_backend():
    """启动后端服务"""
    print("[Backend] Starting backend service...")
    try:
        # 在Windows上使用python，在Unix上使用python3
        python_cmd = "python" if sys.platform == "win32" else "python3"
        subprocess.run([python_cmd, "backend/main.py"], check=True)
    except KeyboardInterrupt:
        print("\n[Backend] Backend service stopped")
    except Exception as e:
        print(f"[Backend] Error: {e}")

def start_frontend():
    """启动前端服务"""
    print("[Frontend] Waiting for backend to start...")
    time.sleep(5)  # 等待后端完全启动
    
    # 检查后端是否就绪
    import requests
    max_retries = 10
    for i in range(max_retries):
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                print("[Frontend] Backend is ready!")
                break
        except:
            if i < max_retries - 1:
                print(f"[Frontend] Waiting for backend... ({i+1}/{max_retries})")
                time.sleep(2)
            else:
                print("[Frontend] Warning: Backend may not be ready, starting frontend anyway...")
    
    print("[Frontend] Starting frontend service...")
    try:
        # 设置环境变量跳过Streamlit的邮箱输入
        env = os.environ.copy()
        
        subprocess.run(
            ["streamlit", "run", "frontend/app.py", 
             "--browser.gatherUsageStats", "false"],
            env=env,
            check=True
        )
    except KeyboardInterrupt:
        print("\n[Frontend] Frontend service stopped")
    except Exception as e:
        print(f"[Frontend] Error: {e}")

def main():
    """主函数"""
    print("=" * 60)
    print("研究智能体系统 - 统一启动")
    print("=" * 60)
    print()
    
    # 检查依赖
    try:
        import streamlit
        import fastapi
        import uvicorn
    except ImportError as e:
        print(f"[错误] 缺少依赖: {e}")
        print("请先运行: pip install -r requirements.txt")
        sys.exit(1)
    
    print("[成功] 依赖检查通过")
    print()
    print("[后端] 服务将在: http://localhost:8000")
    print("[前端] 界面将在: http://localhost:8501")
    print()
    print("按 Ctrl+C 停止所有服务")
    print("=" * 60)
    print()
    
    # 创建线程启动后端
    backend_thread = Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # 在主线程启动前端（这样Ctrl+C可以正常工作）
    try:
        start_frontend()
    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print("🛑 正在停止所有服务...")
        print("=" * 60)
        sys.exit(0)

if __name__ == "__main__":
    main()
