#!/usr/bin/env python3
"""
HTTP设备路径发现工具
用于探测HTTP监控设备的可用路径
"""

import requests
import sys
import time
from urllib.parse import urljoin

def test_device_url(ip, port, paths):
    """测试设备的不同路径"""
    base_url = f"http://{ip}:{port}"
    
    print(f"正在测试设备: {base_url}")
    print("=" * 50)
    
    common_paths = [
        "", "/", "/login", "/web", "/doc", "/home", "/index",
        "/ISAPI", "/ISAPI/Streaming/channels/101", "/ISAPI/System/deviceInfo",
        "/cam/realmonitor", "/axis-cgi/mjpg/video.cgi", "/video.mjpg",
        "/cgi-bin/mjpg/video.cgi", "/mjpg/video.mjpg", "/snapshot.cgi",
        "/web/recorder.html", "/view/viewer_index.shtml", "/main.html",
        "/admin", "/admin/index.html", "/user/login", "/auth/login"
    ]
    
    # 合并用户指定的路径
    if paths:
        test_paths = paths + common_paths
    else:
        test_paths = common_paths
    
    # 去重
    test_paths = list(set(test_paths))
    
    results = []
    
    for path in test_paths:
        url = urljoin(base_url, path)
        try:
            print(f"测试: {url}")
            
            # 设置超时和请求头
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=5, allow_redirects=True)
            
            status = response.status_code
            content_type = response.headers.get('content-type', 'unknown')
            content_length = len(response.content)
            
            result = {
                'url': url,
                'status': status,
                'content_type': content_type,
                'content_length': content_length,
                'title': 'N/A'
            }
            
            # 尝试提取页面标题
            if 'text/html' in content_type and status == 200:
                try:
                    import re
                    title_match = re.search(r'<title[^>]*>([^<]+)</title>', response.text, re.IGNORECASE)
                    if title_match:
                        result['title'] = title_match.group(1).strip()
                except:
                    pass
            
            results.append(result)
            
            print(f"  状态: {status} | 类型: {content_type} | 大小: {content_length} bytes")
            if result['title'] != 'N/A':
                print(f"  标题: {result['title']}")
            
            time.sleep(0.5)  # 避免请求过快
            
        except requests.exceptions.Timeout:
            print(f"  超时")
        except requests.exceptions.ConnectionError:
            print(f"  连接失败")
        except Exception as e:
            print(f"  错误: {str(e)}")
    
    return results

def analyze_results(results):
    """分析测试结果"""
    print("\n" + "=" * 50)
    print("测试结果分析:")
    print("=" * 50)
    
    # 按状态码分组
    status_groups = {}
    for result in results:
        status = result['status']
        if status not in status_groups:
            status_groups[status] = []
        status_groups[status].append(result)
    
    # 显示成功响应
    if 200 in status_groups:
        print("\n✅ 成功响应 (200):")
        for result in status_groups[200]:
            print(f"  {result['url']} - {result['title']}")
    
    # 显示重定向
    redirects = [301, 302, 303, 307, 308]
    for code in redirects:
        if code in status_groups:
            print(f"\n🔄 重定向 ({code}):")
            for result in status_groups[code]:
                print(f"  {result['url']}")
    
    # 显示认证要求
    if 401 in status_groups:
        print("\n🔐 需要认证 (401):")
        for result in status_groups[401]:
            print(f"  {result['url']}")
    
    # 显示未找到
    if 404 in status_groups:
        print("\n❌ 未找到 (404):")
        for result in status_groups[404]:
            print(f"  {result['url']}")
    
    # 推荐最佳路径
    successful = [r for r in results if r['status'] == 200]
    if successful:
        print("\n🏆 推荐访问路径:")
        # 优先选择HTML页面
        html_pages = [r for r in successful if 'text/html' in r['content_type']]
        if html_pages:
            for page in html_pages[:3]:  # 显示前3个
                print(f"  {page['url']} ({page['title']})")
        else:
            for page in successful[:3]:
                print(f"  {page['url']}")

def main():
    """主函数"""
    if len(sys.argv) < 3:
        print("用法: python discover_http_paths.py <IP地址> <端口> [路径1] [路径2] ...")
        print("示例: python discover_http_paths.py 192.168.42.86 55501")
        return
    
    ip = sys.argv[1]
    port = int(sys.argv[2])
    custom_paths = sys.argv[3:] if len(sys.argv) > 3 else None
    
    try:
        results = test_device_url(ip, port, custom_paths)
        analyze_results(results)
        
        # 保存结果到文件
        import json
        with open(f'http_paths_{ip}_{port}.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n💾 结果已保存到: http_paths_{ip}_{port}.json")
        
    except KeyboardInterrupt:
        print("\n测试被中断")
    except Exception as e:
        print(f"测试失败: {str(e)}")

if __name__ == "__main__":
    main()