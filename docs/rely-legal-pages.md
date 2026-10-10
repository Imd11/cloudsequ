# Rely 协议页面维护

固定入口为 `/legal/rely/terms/`、`/legal/rely/privacy/`，补充页为 `usage/` 和 `providers/`。页面无需登录，无跟踪脚本；草稿标明未生效。版本全文保存在 `/legal/rely/versions/<版本>/`。

当前版本 **v0.1-draft**。正文源文件在该版本目录的四份 Markdown 中，HTML 由 `scripts/build-rely-legal.py` 生成，不直接修改生成的正文。知识库原始协议未被改写。

维护命令：

```sh
python3 scripts/build-rely-legal.py
python3 scripts/build-rely-legal.py --check
python3 scripts/build-rely-legal.py --check --app-catalog /path/to/nutritionlive/src/contracts/legal-catalog.json
```

定稿时新建版本目录，核实正文中的运营与供应商信息，移除待填写项，填写 ISO 生效时间。manifest 中的逐份 SHA-256 按 Markdown 原始 UTF-8 字节计算；bundleHash 为按 documents 顺序排列的 `[id, sha256]` 数组使用紧凑 JSON 序列化后的 SHA-256。应用仓库 catalog 与 manifest 内容必须一致。生成器会拒绝摘要不匹配或残留待填写内容的正式版本。

已正式使用的版本正文和摘要保持不变，更新时保留原存档。先发布官网并检查匿名访问及所有链接，再在 Rely 启用对应版本。现有发布脚本包含这些 HTML/CSS/JSON；Markdown 和 scripts/docs 不进入站点发布包。普通 GitHub 推送不会发布生产官网。
