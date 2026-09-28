# Beijing server deployment

This static site is served by Nginx from `/srv/cloudsequ/current`.
Internal preview listener: `127.0.0.1:8080`; access through the authorized SSH tunnel
at `http://localhost:18080`. Public domain target: `https://cloudsequ.com`.

Navigation and canonical URLs now use the independent domain root instead of the
original GitHub Pages `/miraphant/` prefix. Existing branding/content is retained.

The FDE repository contains the Nginx preview configuration and Node/PostgreSQL setup.
Public DNS and HTTPS were enabled on 2026-09-28. ICP filing remains outstanding; current reachability is not a guarantee of continued provider access. Existing email DNS records were preserved.

## AI 指令发布（已配置）

对 AI 说“把这个项目最新 main 部署上线”，AI 按 AGENTS.md 执行：

```sh
python3 scripts/deploy.py
```

脚本获取 origin/main 并固定 SHA，上传该版本源码，在北京服务器构建，保留旧版本，然后切换 current 并检查 HTTPS。FDE 会先校验 TypeScript，发布前备份 PostgreSQL 并验证备份目录可读；切换后失败会恢复上一个应用版本。官网按静态资源白名单发布。备份和旧版本留在服务器，不包含在 Git 中；还需另行配置异地备份。

这属于 AI 执行的脚本化发布，不是每次 git push 触发上线。两个项目独立发布、独立回退；“发布两个项目”时依次执行两个仓库的脚本并分别报告结果。

需要 Python 3、Git、SSH/scp、curl 和已授权的 SSH 密钥。服务器需要现有 Node 24、PostgreSQL、Nginx 和 sudo 权限。脚本不创建云资源、不改变 DNS、不执行数据库迁移。首次将原 current 目录转换为版本软链接时存在极短切换窗口，FDE 重启也会短暂中断请求。

手工回退：从发布输出中的 PREVIOUS 获取旧目录，用临时软链接加 `mv -Tf` 替换 `/srv/项目/current`；FDE 再执行 `sudo systemctl restart fde`。核对 HTTPS 后结束。不要为代码回退覆盖数据库。
