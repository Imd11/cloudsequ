# 协作和发布规则

- 用户要求完成并推送工作时，将经过验证的改动通过 PR 合并到 main；先 fetch，保留他人的改动，不强推，不绕过必需检查。
- 用户说“发布”“部署上线”“更新服务器”时，执行 `python3 scripts/deploy.py`。它发布刚获取的 origin/main 固定提交，不发布未提交文件或仅在分支上的代码。
- 仅修改或推送代码不会触发生产发布。需要发布时先完成 main 合并，再运行脚本。
- SSH 私钥和 known_hosts 位于仓库旁的 server-access 私有目录，也可通过 DEPLOY_SSH_KEY、DEPLOY_KNOWN_HOSTS、DEPLOY_HOST 指定。禁止提交私钥、环境凭据、数据库备份。
- 发布后确认脚本报告的 SHA、HTTPS、业务接口检查。失败时报告失败；不能把 GitHub 推送成功当作部署成功。
- 数据库迁移、Nginx、systemd 配置变更需要单独检查处理；发布脚本只更新应用，不自动应用这些配置。代码回退不恢复或删除数据库数据。
- 不修改参考项目 nutritionlive 的生产环境或凭据。
