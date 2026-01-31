# HTTP设备路径发现工具使用指南

## 文件位置变更说明

为了提高项目结构的整洁性，我们将HTTP设备相关文件移动到了专门的目录：

### 新文件位置

1. **路径发现脚本**
   - 原位置：`discover_http_paths.py`
   - 新位置：`scripts/device_management/discover_http_paths.py`

2. **测试页面**
   - 原位置：`test_http_iframe.html`
   - 新位置：`tests/test_http_iframe.html`

3. **设备路径数据**
   - 原位置：`http_paths_[IP]_[PORT].json`
   - 新位置：`data/http_device_paths/[IP]_[PORT].json`

## 使用方式

### 路径发现工具
```bash
# 在Monitor根目录下执行
python scripts/device_management/discover_http_paths.py 192.168.42.86 55501
```

### 测试HTTP iframe
访问：http://127.0.0.1:8081/tests/test_http_iframe.html

### 查看路径数据
路径数据保存在：`data/http_device_paths/`目录下，按IP和端口分类存储

## 目录结构

```
Monitor/
├── scripts/device_management/
│   └── discover_http_paths.py    # HTTP设备路径发现脚本
├── tests/
│   └── test_http_iframe.html     # HTTP设备iframe测试页面
├── data/http_device_paths/        # 设备路径数据存储
│   └── 192.168.42.86_55501.json   # 示例设备路径数据
└── docs/
    └── HTTP_DEVICE_PATHS_GUIDE.md  # 本指南
```

## 更新后的访问链接

- **前端页面**：http://127.0.0.1:5173
- **HTTP测试页面**：http://127.0.0.1:8081/tests/test_http_iframe.html
- **设备路径数据**：`data/http_device_paths/`目录下

这样组织后，根目录更加整洁，相关文件按功能分类存放，便于维护和管理。