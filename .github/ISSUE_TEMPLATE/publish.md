---
name: 发布插件
about: Publish plugin to index
title: '发布插件'
labels: 'publish'
assignees: ''

---

<!-- 请确保信息填写正确，GitHub Actions 会自动创建拉取请求 -->

```toml
# 基本信息
name="插件名称"
description="一个很棒的插件，可以做很棒的事情"
link="https://github.com/pcrbot/HoshinoBot-plugins-index"

# 如果 description 需要换行，请用以下格式
#description = """
#插件介绍长
#一行里面写不下
#必须要分行"""

# 如果 description 需要包含链接，请用以下格式
#description="这个插件来自 [pcrbot](https://github.com/pcrbot/HoshinoBot-plugins-index) 仓库"


# 作者
[[authors]]
name="@pcrbot"
link="https://github.com/pcrbot"

# 如果不止一个作者，请重复这个部分
#[[authors]]
#name="@another-pcrbot"
#link="https://github.com/pcrbot-bot"
```
