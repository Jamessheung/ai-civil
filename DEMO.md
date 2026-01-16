# 启动浏览器演示 (Visual Demo)

你的代码已就绪，已包含 Next.js 前端页面和 mock 数据填充脚本。请按以下步骤操作以在浏览器中查看效果。

## 1. 启动基础设施
确保 Docker 正在运行：
```bash
docker-compose up -d
```
*等待 5-10 秒确保数据库完全启动。*

## 2. 注入演示数据
运行此脚本，向数据库填充 "美联储报告 (L5)" 和 "推特谣言 (L1)" 两个示例：
```bash
# 确保在项目根目录
/usr/bin/python3 scripts/seed_data.py
```
*成功后应显示 "✅ Seed Complete!"*

## 3. 启动后端 (API)
在一个新终端窗口中：
```bash
cd backend
source venv/bin/activate  # 如果未激活
uvicorn main:app --reload --port 8000
```

## 4. 启动前端 (UI)
在另一个新终端窗口中：
```bash
cd frontend
npm install
npm run dev
```

## 5. 查看效果
打开浏览器访问：
- **主控面板**: [http://localhost:3000](http://localhost:3000)
  - 你将看到 "Active Event Matrix" 网格。
  - "Federal Reserve" (Power) 显示为 Active。
  - "Rumor" (Tech) 显示为 Disputed。
- **详情页**: 点击任意卡片进入。
  - 左侧: Evidence Log (注意 L5 和 L1 的颜色区别)。
  - 中间: Title & Analysis (一致性分数的展示)。
  - 右侧: Timeline。
