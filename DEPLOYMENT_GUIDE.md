# 🚀 Streamlit Cloud 部署指南

本项目使用 **GitHub Gist** 提供在线预览功能，配置简单且完全免费。

---

## ✅ 已完成的配置

- ✅ GitHub Token 已配置（本地）
- ✅ 测试成功，可以正常上传和预览
- ✅ YouTube 视频嵌入正常工作
- ✅ 文件永久有效，无需清理机制

---

## 📋 部署到 Streamlit Cloud

### 第一步：准备 GitHub 仓库

1. 将项目推送到 GitHub：
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/你的用户名/仓库名.git
git push -u origin main
```

2. **重要**：确保 `.streamlit/secrets.toml` **没有**被提交到 Git
   - 已在 `.gitignore` 中配置，提交前再次检查

---

### 第二步：在 Streamlit Cloud 创建应用

1. 访问 [share.streamlit.io](https://share.streamlit.io/)
2. 使用 GitHub 账号登录
3. 点击 **New app**
4. 选择你的仓库和分支
5. Main file path: `app.py`
6. 点击 **Deploy**

---

### 第三步：配置 GitHub Token（关键）

在应用创建后：

1. 点击应用右下角的 **Settings** ⚙️
2. 选择 **Secrets** 标签
3. 粘贴以下内容：

```toml
GITHUB_TOKEN = "你的GitHub Personal Access Token"
```

**注意**：请将 `"你的GitHub Personal Access Token"` 替换为你的真实 Token

4. 点击 **Save**
5. 应用会自动重启

---

## 🎉 完成！

现在你的应用已经部署完成：
- ✅ 用户无需任何配置
- ✅ 所有生成的报告自动上传到你的 GitHub Gist
- ✅ 在线预览永久有效
- ✅ YouTube 视频可以正常播放

---

## 🔧 管理你的 Gist

### 查看所有 Gist

访问：https://gist.github.com/17857001531

### 删除旧的 Gist（可选）

如果 Gist 太多，可以手动删除：
1. 访问上述链接
2. 点击要删除的 Gist
3. 点击右上角 **Delete** 按钮

### API 限额监控

GitHub API 限额：每小时 5000 次请求

查看当前用量：
```bash
curl -H "Authorization: token ghp_your_token" \
  https://api.github.com/rate_limit
```

---

## 🔒 安全建议

1. **Token 管理**
   - ✅ 本地配置在 `.streamlit/secrets.toml`（已在 `.gitignore`）
   - ✅ 云端配置在 Streamlit Cloud Secrets
   - ❌ 永远不要提交到公开仓库

2. **定期检查**
   - 访问 https://github.com/settings/tokens
   - 查看 Token 是否被异常使用

3. **Token 泄露处理**
   - 立即删除（revoke）Token
   - 生成新 Token
   - 更新 Streamlit Cloud Secrets

---

## 📊 使用统计

使用 GitHub Gist 方案后：
- ✅ 稳定性：99.9%+（GitHub 服务）
- ✅ 费用：完全免费
- ✅ 存储：理论上无限（单个 Gist 最大 1GB）
- ✅ 流量：完全免费无限制
- ✅ 维护：几乎为零

---

## ❓ 常见问题

### Q: 为什么选择 GitHub Gist？
A: 
- 稳定可靠（GitHub 的服务）
- 完全免费
- 无需额外配置账户
- 支持 HTML 直接预览
- 支持 YouTube 视频嵌入

### Q: 用户上传的文件会占用我的空间吗？
A: 
- 文件存储在你的 GitHub Gist 中
- 单个 HTML 文件通常只有几百 KB
- 即使有 1000 个文件，也只有几百 MB
- GitHub Gist 理论上无限制

### Q: API 限额 5000 次够用吗？
A: 
- 每次处理视频只调用 1 次 API
- 5000 次/小时 = 83 次/分钟
- 对个人使用绰绰有余
- 即使是小型团队也完全够用

### Q: 如果想改用其他服务怎么办？
A: 
- 代码结构已经设计好
- 只需修改 `file_share.py` 中的 `create_shareable_link` 函数
- 可以轻松切换到 Cloudflare R2、AWS S3 等

---

## 🎯 下一步

1. ✅ 测试应用功能是否正常
2. ✅ 处理一个真实的 YouTube 视频
3. ✅ 确认在线预览链接可以正常访问
4. ✅ 确认嵌入的 YouTube 视频可以播放
5. 🚀 部署到 Streamlit Cloud

祝你部署顺利！🎉

