# 天眼系统

这是一个视音频流监控系统，支持RTSP、HTTP等多种协议的设备接入和实时监控。

## 安全配置说明

为了保护敏感信息，本项目使用环境变量管理敏感配置。请不要直接修改配置文件中的占位符。

### 环境变量配置

复制 `.env.example` 文件为 `.env`，并填入实际的敏感信息：

```bash
cp .env.example .env
```

需要配置的环境变量包括：

- `DB_USER`: 数据库用户名
- `DB_PASSWORD`: 数据库密码
- `PG_USER`: PostgreSQL用户名（如适用）
- `PG_PASSWORD`: PostgreSQL密码（如适用）
- `JWT_SECRET`: JWT加密密钥（强烈建议使用安全的随机字符串）
- `DEVICE_PASSWORD`: 设备访问密码（如适用）
- `DEVICE_USERNAME`: 设备访问用户名（如适用）

### 生成安全的JWT密钥

```bash
# 使用Python生成
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 或使用openssl生成
openssl rand -base64 32
```

## 部署前注意事项

1. 确保所有敏感信息都通过环境变量配置
2. 将 `.env` 添加到 `.gitignore`，不要提交到版本控制
3. 在生产环境中使用强密码和安全的JWT密钥
4. 定期轮换敏感凭证

## 运行项目

按照原有说明运行项目，系统会自动从环境变量读取配置。