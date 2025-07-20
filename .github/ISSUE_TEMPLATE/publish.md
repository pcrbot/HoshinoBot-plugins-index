---
name: 发布插件
about: Publish plugin to index
title: '发布插件'
labels: 'publish'
assignees: ''

---

请确保信息填写正确，此拉取请求将被自动合并。

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

# 作者
[[authors]]
name="@pcrbot"
link="https://github.com/pcrbot"

# 如果不止一个作者，请将下面的部分取消注释
#[[authors]]
#name="@pcrbot"
#link="https://github.com/pcrbot"
```
