# auto-load-osz

## 简介

最近在玩 neosu，但是它的 osu!direct 不能用 BID 搜图。

于是，我索性使用网页（如官网/小夜站）下图，然后自动解压到 neosu 的 maps 文件夹。

在退出程序时，可选择重打包为 osz 并移动至 stable 的 Songs 文件夹便于下次游玩时导入数据库。

## 使用方法

1. 安装依赖。如果 Python 版本 >= 3.13，则还需安装 `legacy-cgi` （这个问题以后我更新我的 `clayutil` 应该就能解决了）。
2. 在 [main.py](main.py) 的开头部分修改相关设置。
3. 运行 `main.py`。
