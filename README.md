# WeChat 4.x Auto Reply

基于本地 DeepSeek 模型的微信自动回复机器人，支持 WeChat 4.x 新版客户端。

## 原理

微信 4.x 使用 Chromium 渲染，pywinauto 无法直接读取消息控件。本方案通过 UIA 文本扫描检测新消息，剪贴板粘贴发送回复，DeepSeek R1 本地推理生成内容。

## 安装

`ash
pip install requests pyperclip pywinauto pywin32
## 使用

1.启动 LM Studio，加载 DeepSeek-R1-14B，开启 Server（127.0.0.1:1234）
2.打开微信并登录
3.运行 python auto_reply.py
4.作者GPU为RTX 5070ti laptop，12GB显存，使用deepseek-r1 14B Q4模型时显存占用为11GB，因此建议在LM stdio中使用适合自己的模型，自行在代码中更改模型名称即可。

## 配置

编辑 auto_reply.py 顶部修改模型地址、回复风格等。


## 已知限制

微信 4.x 不暴露消息控件，通过文本变化检测，可能误触发
需要保持微信窗口可访问（不必前台，但不能最小化到托盘）
仅支持文本消息

## 已知bug
启动时会回复该聊天最后一句话，无论是哪一方发的

## Acknowledgments

回复风格基于 
https://github.com/titanwings/colleague-skill

