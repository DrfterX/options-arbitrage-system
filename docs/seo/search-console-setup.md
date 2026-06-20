# Google Search Console 配置指南

## 前提条件（系统已自动完成）

- ✅ **robots.txt** — 已配置，允许所有爬虫抓取
- ✅ **Sitemap** — 自动化生成，包含主页 + 定价 + API 文档 + Blog（2 篇文章）+ 所有品种着陆页
- ✅ **Google 验证文件路由** — Flask 已添加 catch-all 路由，支持 HTML 文件验证方法
- ✅ **OG Meta Tags** — 所有页面已配置 og:image/og:title/og:description
- ✅ **Mobile-friendly** — 响应式设计

## 添加站点到 Google Search Console

### 方法一：DNS 验证（推荐，一次配置永久有效）

1. 打开 https://search.google.com/search-console
2. 点击「Add property」
3. 选择 **Domain**（域名），输入 `indevs.in`
4. 复制 Google 提供的 **TXT record** 值
5. 在域名注册商（如 Namecheap/GoDaddy/Cloudflare）的 DNS 设置中添加：
   - 类型：`TXT`
   - 名称：`@`（或留空）
   - 值：Google 提供的 TXT 记录值
6. 回到 Search Console 点击「Verify」
7. 添加成功后，**添加第二个 Property**（URL prefix）：
   - 选择 **URL prefix**
   - 输入 `https://signals.drifter.indevs.in`
   - 三种方法任选：

### 方法二：HTML 文件验证（无需 DNS 访问）

1. 打开 https://search.google.com/search-console
2. 点击「Add property」→ **URL prefix**
3. 输入 `https://signals.drifter.indevs.in`
4. 选择「HTML file」验证方法
5. 下载 Google 提供的 `googleXXXXX.html` 文件
6. 将文件放入 `web/verification/` 目录
7. 在 Railway 重新部署：

```bash
git add projects/options_arbitrage_system/web/verification/google*.html
git commit -m "feat: add Google Search Console verification file"
git push
```

8. Railway 自动部署完成后，点击「Verify」

> 💡 **验证文件路由已配置**：Flask 应用会自动将 `https://signals.drifter.indevs.in/googleXXXXX.html` 的请求映射到 `web/verification/` 目录下的对应文件。

### 方法三：HTML Meta Tag 验证

1. 打开 https://search.google.com/search-console
2. 点击「Add property」→ **URL prefix**
3. 输入 `https://signals.drifter.indevs.in`
4. 选择「HTML tag」验证方法
5. 复制 `<meta name="google-site-verification" content="..." />` 标签
6. 联系项目维护者将 meta 标签添加到所有页面的 `<head>` 中
7. 部署后点击「Verify」

## 提交 Sitemap

验证完成后（任意方法）：

1. 在 Search Console 中选择 `https://signals.drifter.indevs.in` property
2. 左侧导航 → **Sitemaps**
3. 在「Add a new sitemap」中输入：

```
sitemap.xml
```

4. 点击「Submit」

## 验证配置完成后的任务

- [ ] Google Search Console 站点验证完成
- [ ] Sitemap 已提交
- [ ] 等待 Google 抓取（24-48 小时）
- [ ] 在 Search Console 中查看抓取统计和索引覆盖
- [ ] 后续可通过「Performance」报表追踪搜索流量

## 当前 SEO 状态

| 项目 | 状态 | 说明 |
|------|------|------|
| robots.txt | ✅ | 允许所有，正确指向 sitemap |
| Sitemap | ✅ | 自动生成，含 60+ 品种页面 + Blog 文章 |
| OG Tags | ✅ | og:image/og:title/og:description 全覆盖 |
| 响应式设计 | ✅ | 移动端友好 |
| Google Search Console | ⬜ 待配置 | 需人类操作完成验证 |
| 结构化数据 | ⬜ | 暂未实现（后续可添加 BlogPosting Schema） |
