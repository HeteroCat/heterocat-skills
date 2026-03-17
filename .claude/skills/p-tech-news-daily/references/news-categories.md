# 科技新闻分类参考

## 概览
本文档提供科技新闻的分类标准和示例，帮助智能体在生成日报时进行合理的分类和筛选。

## 核心分类体系

### 1. 人工智能（AI）
**关键词**：AI、artificial intelligence、machine learning、ML、deep learning、神经网络、LLM、GPT、ChatGPT、自动驾驶、计算机视觉

**判断标准**：
- 涉及机器学习算法、模型、框架
- AI 应用场景和技术突破
- 大语言模型（LLM）相关动态

**示例**：
- "GPT-4 Released: A Multimodal LLM"
- "Tesla's Full Self-Driving Beta Update"
- "New Deep Learning Framework Achieves SOTA"

---

### 2. 云计算与基础设施
**关键词**：cloud、AWS、Azure、GCP、Kubernetes、Docker、serverless、devops、infrastructure、scaling

**判断标准**：
- 云服务提供商的新产品和功能
- 容器化和编排技术
- DevOps 工具和实践

**示例**：
- "AWS Launches New EC2 Instances"
- "Kubernetes 1.28 Released"
- "Google Cloud Announces Serverless Database"

---

### 3. 开发技术
**关键词**：programming、language、framework、library、JavaScript、Python、Rust、Go、web development、mobile、frontend、backend

**判断标准**：
- 编程语言的新版本和特性
- 开发框架和库的更新
- Web 和移动开发技术

**示例**：
- "Python 3.12 Released"
- "React 18 New Features"
- "New JavaScript Framework gaining popularity"

---

### 4. 安全与隐私
**关键词**：security、vulnerability、encryption、privacy、hack、breach、malware、zero-day

**判断标准**：
- 安全漏洞和威胁
- 加密技术和隐私保护
- 安全工具和最佳实践

**示例**：
- "Critical Vulnerability in Popular Library"
- "New Encryption Standard Approved"
- "Major Data Breach Exposes User Data"

---

### 5. 硬件与芯片
**关键词**：chip、semiconductor、processor、GPU、TPU、Apple Silicon、Intel、AMD、NVIDIA、ARM

**判断标准**：
- 芯片和处理器技术
- 硬件产品和发布
- 半导体行业动态

**示例**：
- "NVIDIA Announces New GPU Architecture"
- "Apple M3 Chip Performance Review"
- "Intel Next-Gen Processor Roadmap"

---

### 6. 开源项目
**关键词**：open source、GitHub、repo、release、fork、Linux、kernel

**判断标准**：
- 重要开源项目的更新
- 开源社区动态
- 新兴开源项目

**示例**：
- "Linux Kernel 6.6 Released"
- "Popular Open Source Project Reaches 100k Stars"
- "New Open Source Alternative to Commercial Tool"

---

### 7. 创业与融资
**关键词**：startup、funding、IPO、acquisition、venture capital、Series A、unicorn

**判断标准**：
- 创业公司融资消息
- 并购和 IPO
- 创业生态动态

**示例**：
- "AI Startup Raises $100M in Series B"
- "Tech Giant Acquires Cloud Security Firm"
- "Startup Goes Public with Strong IPO"

---

### 8. 科技公司与产品
**关键词**：Google、Apple、Microsoft、Meta、Tesla、product launch、update、feature

**判断标准**：
- 大型科技公司的产品发布
- 重要产品更新
- 公司战略动态

**示例**：
- "Apple Launches New iPhone Features"
- "Google Announces Pixel 8"
- "Microsoft Updates Office 365"

---

### 9. 数据科学
**关键词**：data、analytics、database、big data、SQL、NoSQL、visualization、BI

**判断标准**：
- 数据库技术和产品
- 数据分析工具和方法
- 大数据处理技术

**示例**：
- "New Database Optimization Technique"
- "Popular Data Visualization Tool Update"
- "Big Data Processing Framework Milestone"

---

### 10. 区块链与加密货币
**关键词**：blockchain、crypto、Bitcoin、Ethereum、Web3、DeFi、NFT、smart contract

**判断标准**：
- 区块链技术发展
- 加密货币市场动态
- Web3 应用和协议

**示例**：
- "Ethereum Upgrade Successfully Deployed"
- "New Blockchain Protocol Gains Traction"
- "NFT Marketplace Volume Reaches All-Time High"

---

## 筛选和排序规则

### 按重要性筛选
- **高优先级**：score > 100 或评论数 > 50
- **中优先级**：50 < score ≤ 100 或 20 < 评论数 ≤ 50
- **低优先级**：score ≤ 50 且评论数 ≤ 20

### 按时间筛选
- 优先显示最近 24 小时内的新闻
- 对于重要新闻（高 score），时间窗口可放宽到 48 小时

### 按相关性筛选
- 根据日报主题选择相关分类
- 例如：AI 专题日报中，优先展示 AI 分类新闻

### 排除规则
- 排除非技术类内容（如纯政治、娱乐新闻）
- 排除明显是广告或营销的内容
- 排除低质量的链接或讨论

## 输出格式建议

### 标准日报结构
```
# {日期} 科技日报

## 📊 概览
- 今日新闻总数：X 条
- 最热门话题：[标题]
- 关键词：AI, 云计算, 开源...

## 🔥 热门话题
按 score 排序的前 3-5 条新闻

## 🤖 人工智能
AI 相关新闻，按重要性排序

## 💻 开发技术
开发技术相关新闻

## ☁️ 云计算与基础设施
云计算相关新闻

## 🔒 安全与隐私
安全相关新闻

## 📈 其他资讯
其他分类新闻
```

### 单条新闻格式
```
- [标题](链接)
  - 来源：Hacker News | 分数：XX | 评论：XX
  - 简要描述或翻译（1-2 句）
```

## 注意事项
1. **翻译准确性**：确保技术术语翻译准确，保持专业性和一致性
2. **时效性**：优先关注最新的技术动态
3. **价值判断**：选择对读者有实际价值的新闻
4. **多样性**：避免单一分类占比过高，保持日报内容的多样性
5. **客观性**：保持客观中立，不添加个人主观评价
