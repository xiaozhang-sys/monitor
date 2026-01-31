import requests
import time

# 等待一段时间确保服务完全启动
time.sleep(2)

print("测试后端服务连接...")

try:
    # 先测试基本连接
    response = requests.get("http://localhost:8004/", timeout=5)
    print(f"根路径响应: {response.status_code}")
except:
    print("无法连接到后端服务")

try:
    # 测试登录
    login_data = {"username": "admin", "password": "admin123"}
    response = requests.post("http://localhost:8004/token", data=login_data, timeout=5)
    print(f"登录响应: {response.status_code}")
    if response.status_code == 200:
        print("登录成功!")
        print(response.json())
    else:
        print(f"登录失败: {response.status_code}")
except Exception as e:
    print(f"请求错误: {e}")