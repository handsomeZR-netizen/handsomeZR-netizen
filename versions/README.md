# 版本存档 · Versions

| 版本 | 风格 | 位置 | 对应提交 |
| :-- | :-- | :-- | :-- |
| **v3 pixel**（当前） | 像素游戏风：标题画面 · 对话框 · 能力面板 · 任务日志 · 装备栏 · 成就 · 存档 | 仓库根目录 | — |
| **v2 macaron** | 马卡龙柔光风 | [`versions/v2-macaron/`](v2-macaron/) | `7e83b46` |

只想看看旧版：直接打开 [`versions/v2-macaron/`](v2-macaron/)，GitHub 会渲染里面的 README。

## 回滚到 v2（任选一种）

**方式 A：用存档目录（推荐）**

```bash
cp versions/v2-macaron/README.md README.md
cp versions/v2-macaron/assets/*.svg assets/
git add -A && git commit -m "rollback: v2 macaron homepage" && git push
```

**方式 B：用 git 历史**（注意：`7e83b46` 里的旧版还带着真名，用方式 A 更好）

```bash
git checkout 7e83b46 -- README.md assets
git commit -m "rollback: v2 macaron homepage" && git push
```

两种方式都不用动 workflow：`.github/workflows/profile-data.yml` 仍然每天生成 v2 用到的
`github-contribution-grid-snake.svg`，文件名没变。

## 从 v2 回到 v3

```bash
python3 tools/build.py        # 重新生成 README.md 和 assets/
git add -A && git commit -m "restore v3 pixel homepage" && git push
```

## 以后再存一个版本

```bash
mkdir -p versions/v3-pixel/assets
cp README.md versions/v3-pixel/
cp assets/*.svg versions/v3-pixel/assets/
```

README 里的图片都是相对路径 `assets/...`，所以复制过去的存档在 GitHub 上也能直接预览
（贪吃蛇和存档卡片是从 `output` 分支读取的绝对地址，同样有效）。
