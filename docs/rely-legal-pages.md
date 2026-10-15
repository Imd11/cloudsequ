# Rely 协议页面维护

固定入口为 `/legal/rely/terms/`、`/legal/rely/privacy/`，补充页为 `usage/` 和 `providers/`。页面无需登录，无跟踪脚本，使用首页导航及单栏正文；页脚由生成器复用首页的品牌区、产品与公司导航、版权及备案信息，协议链接位于公司导航中。历史HTML仅同步页脚和样式，正文及协议摘要保持不变。

核心协议版本为 **v1.0**，正文和摘要在 `legal/rely/manifest.json` 登记，与应用 `src/contracts/legal-catalog.json` 一致。已接受版本的 Markdown、摘要及存档不得原地重写；正文实质变化需要新建版本，并在处理前完成告知及必要的重新确认。

第三方服务清单单独在 `legal/rely/supplements.json` 登记，当前来源为 `versions/providers-20261011/providers.md`。它不增加登录勾选项，也不改变核心协议的版本和组合摘要。补充清单事实更新不等于可以改变原隐私政策承诺；重大接收方或处理范围变化仍需更新核心政策及履行必要程序。原 `v0.1-draft` 文件和存档保留。

本次核实清单列出当前接入地址、用途、数据范围、服务方资料和仍未取得的说明，移除填空模板。图片实际处理链路、部分服务留存与禁止训练安排，以及备份清理期限尚未全部核实；不得将本次补充页发布等同于完整合规上线验收。

HTML 由 `scripts/build-rely-legal.py` 生成，不直接编辑正文。生成器检查核心两份及独立补充来源摘要，拒绝正式文本中的填空模板，并核对固定入口和存档页面是否过期。公司名称、地址和客服邮箱在文末集中展示。

维护命令：

```sh
python3 scripts/build-rely-legal.py
python3 scripts/build-rely-legal.py --check
python3 scripts/build-rely-legal.py --check --app-catalog /path/to/nutritionlive/src/contracts/legal-catalog.json
```

核心 bundleHash 为按 documents 顺序排列的 `[id, sha256]` 数组使用紧凑 JSON 序列化后的 SHA-256；每份 sha256 按原 Markdown UTF-8 字节计算。新增补充版本也须登记摘要并保留旧存档。

发布前检查匿名访问、完整文本和所有链接。Markdown、scripts/docs 不进入站点发布包；普通 GitHub 推送不会更新线上官网，需要另运行 `python3 scripts/deploy.py` 并核对发布 SHA、HTTPS 及业务接口。仅显示形式调整不能代替事实核验。
