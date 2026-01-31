# 🔧 端口配置修复总结

## 问题描述
用户报告实时视频查看时出现以下错误：
- `net::ERR_CONNECTION_REFUSED http://localhost:8889/api/stream/start`
- `WebRTC连接失败: TypeError: Failed to fetch`
- `API Error: TypeError: Failed to fetch`
- `视频加载失败: Error: WebRTC连接失败`
- `H.265 (HEVC) 视频无法播放`

## 根本原因
项目中的端口配置混乱，多个配置文件使用了不一致的端口，并且缺乏对H.265 (HEVC)视频的支持。

## 当前环境
目前系统在本地直接运行，没有使用Docker容器化部署。

## 修复内容

### ✅ 已更新的端口配置

当前项目已更新为以下端口配置，所有服务都在本地直接运行，不使用Docker容器：

## 当前端口配置

### 服务端口映射
| 服务名称 | 端口号 | 访问地址 | 用途 |
|----------|---------|----------|------|
| 主后端API | 8004 | http://localhost:8004 | 设备管理、数据接口 |
| WebRTC服务 | 8081 | http://localhost:8081 | 实时视频流处理 |
| HEVC兼容服务 | 8090 | http://localhost:8090 | H.265视频转换与兼容 |
| Vue3前端 | 5173 | http://localhost:5173 | 前端开发服务器 |

### 测试地址
- **Vue3前端**: http://localhost:5173
- **测试工具**: 使用 `tools/check_services.py` 检查所有服务状态

## 验证步骤

### 1. 检查服务状态
```powershell
# Windows PowerShell检查服务状态
# 检查后端服务
Invoke-RestMethod -Uri 'http://localhost:8004/health' -Method GET

# 检查WebRTC服务
Invoke-RestMethod -Uri 'http://localhost:8081/health' -Method GET

# 检查HEVC兼容服务
Invoke-RestMethod -Uri 'http://localhost:8090/health' -Method GET

# 或使用系统状态检查脚本
python tools/check_services.py
```

```bash
# Linux/MacOS检查服务状态
# 检查后端服务
curl http://localhost:8004/health

# 检查WebRTC服务
curl http://localhost:8081/health

# 检查HEVC兼容服务
curl http://localhost:8090/health

# 或使用系统状态检查脚本
python tools/check_services.py
```

### 2. 测试视频流
1. 打开Vue3前端: http://localhost:5173
2. 系统已内置测试设备，无需额外配置
3. 选择设备并尝试播放
4. 验证实时视频显示正常，H.265视频也能正常播放



## 常见问题排查

### 如果仍然连接失败
1. **检查服务是否运行**: 确认后端服务(8004)、WebRTC服务(8081)和HEVC兼容服务(8090)已全部启动
2. **防火墙设置**: 确保端口8004、8081、8090和5173未被防火墙阻止
3. **H.265视频问题**: 确保HEVC兼容服务(8090端口)正在运行，如果H.265视频黑屏，请参考 `docs/HEVC_FIX_GUIDE.md`
4. **浏览器兼容性**: 使用最新版Chrome/Firefox测试

*注意：当前系统已改为本地直接运行，不再支持Docker容器化部署。*

### 调试工具
- 使用 `tools/check_services.py` 检查所有服务状态
- 查看各服务终端输出获取详细错误信息
- 使用浏览器开发者工具查看网络请求
- 运行 `python scripts/webrtc/hevc_compat_server.py --status` 检查HEVC服务状态

## 下一步操作

✅ **所有端口配置已更新为当前实际使用值**  
✅ **支持H.265 (HEVC)视频播放**  
✅ **系统已内置测试设备**  
✅ **本地直接运行模式，无需Docker**  

现在可以正常使用实时视频功能，包括H.265视频！

**建议使用**: http://localhost:5173 进行系统访问。