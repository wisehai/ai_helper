# ai_helper
## 功能简介
命令行工具，在终端中使用ai服务

- 支持管道输入
例如：
`grep "important" log.txt | ai chat "分析这些重要日志条目"  `

- 支持自动检测在线离线，使用不同的模型
解决了Clash中TUN Mode假在线的问题

待办：
- 增加备用在线线路
- 手动切换在线离线状态

## 使用方法

### 配置API
```
# 临时设置  
export AI_API_KEY="你的API密钥"  

# 永久设置（添加到~/.bashrc）  
echo 'export AI_API_KEY="你的API密钥"' >> ~/.bashrc  
source ~/.bashrc
```
### 使脚本可执行并安装
```
chmod +x ai.py  
sudo cp ai.py /usr/local/bin/ai
```

### 使用举例
程序名ai,参数有chat和dic（如其他需求，可自行修改源代码）,后面输入提示词
```
# 聊天  
ai chat 今天天气怎么样？  

# 翻译  
ai dic Hello, how are you today?
```

