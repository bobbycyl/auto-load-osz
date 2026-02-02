# auto-load-osz

## 简介

最近在玩 neosu，但是它的 osu!direct 不能用 BID 搜图。

于是，我索性使用网页（如官网/小夜站）下图，然后自动解压到 neosu 的 maps 文件夹。

在退出程序时，可选择重新打包为 osz 并移动至 stable 的 Songs 文件夹便于下次游玩时导入数据库。

目前只在 Linux 上测试过，Windows 如果使用混合目录分隔符（“\”与“/”混用）是否会导致 `find_deepest_dirs` 函数出错仍是未知。

## 使用方法

1. 安装依赖。如果 Python 版本 >= 3.13，则需安装 `legacy-cgi` （这个问题以后我更新依赖库应该就能解决了）。
2. 在 [main.py](main.py) 的开头部分修改 `HOME_PATH`、`MONITOR_PATH`、`TARGET_PATH` 和 `REMOVE_SRC`。
3. 运行 `main.py`。
