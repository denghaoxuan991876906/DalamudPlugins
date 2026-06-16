# DalamudPlugins

自定义 Dalamud 插件仓库。仓库只保存每个插件的**元数据**（JSON），插件二进制 (`latest.zip`) 存放在本仓库的 **GitHub Release** 里，`pluginmaster.json` 由脚本 `generate_pluginmaster.py` 自动生成。

## 安装（最终用户）

游戏内输入 `/xlplugins` → `Settings` → `Experimental` → 在 **Custom Plugin Repositories** 添加：

```
https://raw.githubusercontent.com/denghaoxuan991876906/DalamudPlugins/main/pluginmaster.json
```

## 目录结构

```
plugins/<InternalName>/<InternalName>.json   # 插件基础元数据（进 git）
.github/workflows/
  regenerate.yml     # plugins/** 有改动时重算 pluginmaster.json
  publish.yml        # 各插件发版入口（repository_dispatch / workflow_dispatch）
generate_pluginmaster.py                      # 扫描 plugins/ 生成 pluginmaster.json
pluginmaster.json                             # 生成产物，勿手改
```

插件元数据 JSON 只写基础字段（`Author`/`Name`/`InternalName`/`AssemblyVersion`/`Description`/`Punchline`/`RepoUrl`/`Tags`/`DalamudApiLevel` 等）。`DownloadLinkInstall`/`DownloadLinkUpdate`/`LastUpdate` 由脚本自动补全，指向本仓库 Release：

```
https://github.com/denghaoxuan991876906/DalamudPlugins/releases/download/<InternalName>-v<AssemblyVersion>/latest.zip
```

## 新增插件（维护者）

1. 新建 `plugins/<InternalName>/<InternalName>.json`，填好基础字段（`AssemblyVersion` 先写即将发布的版本）。
2. 提交到 main（`regenerate.yml` 会自动生成 `pluginmaster.json`）。
3. 让该插件触发一次发布（见下），把 `latest.zip` 上传到本仓库的 Release。

## 发布新版本（各插件源仓库）

插件源仓库的 release workflow 里，构建出 `latest.zip` 并发布到自己的 release 后，触发本仓库的 `publish.yml`：

```yaml
- name: Publish to DalamudPlugins
  env:
    GH_TOKEN: ${{ secrets.DALAMUDPLUGINS_PAT }}
  run: |
    gh api -X POST /repos/denghaoxuan991876906/DalamudPlugins/dispatches \
      -f event_type=publish-plugin \
      -f 'client_payload={"internal_name":"MyPlugin","version":"1.0.0.0","zip_url":"https://github.com/ME/MyPlugin/releases/download/v1.0.0.0/latest.zip"}'
```

`publish.yml` 收到后会：下载该 zip → 上传到本仓库 Release（tag `MyPlugin-v1.0.0.0`，asset 名 `latest.zip`）→ 更新 `AssemblyVersion` → 重算 `pluginmaster.json`。

### Token 配置

`repository_dispatch` 跨仓库触发，`GITHUB_TOKEN` 不够用，需新建一个对本仓库有写权限的凭据，加到**各插件源仓库**的 Secret（名为 `DALAMUDPLUGINS_PAT`）：

- **Fine-grained PAT**（推荐）：对本仓库开 `Contents: Read and write` + `Actions: Read and write`。
- 或 **Classic PAT**：勾选 `repo`。

> 也可以在本仓库 Actions 页用 `workflow_dispatch` 手动触发 `Publish Plugin`，填入 `internal_name` / `version` / `zip_url` 来发布或重新发布某个版本。
