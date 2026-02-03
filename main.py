import os
from shutil import ReadError, copytree, rmtree
from time import sleep

from clayutil.futil import FolderMonitor, compress_as_zip

from utils.extract import extract_innermost

HOME_PATH = os.environ["HOME"]
MONITOR_PATH = os.path.join(HOME_PATH, "Downloads")
STABLE_SONGS_PATH = os.path.join(
    HOME_PATH, ".local", "share", "osu!", "Songs"
)  # ~/.local/share/osu!/Songs/
NEOSU_MAPS_PATH = os.path.join(
    HOME_PATH, ".local", "share", "neosu", "maps"
)  # ~/.local/share/neosu/maps/
REMOVE_SRC = True  # 解压后自动删除原始 osz

monitor = FolderMonitor(MONITOR_PATH, False)


@monitor.on_event("created", False)
def _(event):
    main(event["src_path"], REMOVE_SRC)


@monitor.on_event("moved", False)
def _(event):
    main(event["dest_path"], REMOVE_SRC)


def main(src_path, remove_src=False):
    global runtime_downloaded
    try:
        basename = os.path.basename(src_path)
        binfo, ext = os.path.splitext(basename)
        if ext == ".osz":
            # 文件名类似于 1701699 TRUE - Storyteller.osz，提取最开始的数字
            sid = binfo.split()[0]

            # 检查目标路径下的文件夹是否有重复的 SID ，如有，发出警告
            for dirname in os.listdir(STABLE_SONGS_PATH):
                if dirname.split()[0] == sid:
                    # 警告用红色加粗字体
                    print(
                        "\033[1;31m警告：目标路径下已存在同 SID 文件夹：%s\033[0m"
                        % dirname
                    )
                    # 但是警告不影响程序正常执行
                    break
            else:
                # 如果没有检测到重复的，才加入 runtime_downloaded
                # 这样避免清理的时候把现有的谱面删了
                runtime_downloaded.add(binfo)

            # 解压到目标路径
            extract_innermost(src_path, os.path.join(NEOSU_MAPS_PATH, binfo), True)
            # patch: 同时复制一份到 stable Songs，这样可以不操作 neosu 数据库
            if STABLE_SONGS_PATH != "":
                copytree(os.path.join(NEOSU_MAPS_PATH, binfo), os.path.join(STABLE_SONGS_PATH, binfo))
            if remove_src:
                # 删除源文件
                os.remove(src_path)
                print("已解压并删除源文件：%s" % binfo)
    except ReadError:
        print("解压失败：%s" % basename)


monitor.start()
print("监控已启动")
print("监控目录：%s\n目标目录：%s" % (MONITOR_PATH, NEOSU_MAPS_PATH))
runtime_downloaded: set[str] = set()
try:
    while True:
        sleep(3)
        pass
except KeyboardInterrupt:
    monitor.stop()
monitor.shutdown_thread_pool(False)
print("监控已停止")

if STABLE_SONGS_PATH != "":
    # 清理 runtime_downloaded（虽然这么做可能是多余的？）
    for runtime_binfo in runtime_downloaded:
        if os.path.exists(os.path.join(STABLE_SONGS_PATH, runtime_binfo)):
            rmtree(os.path.join(STABLE_SONGS_PATH, runtime_binfo))

    # 询问是否重打包
    repack_after_input = input("重打包谱面至 stable Songs？ (y/[n]) ")
    if repack_after_input.lower() == "y":
        for dirname in os.listdir(NEOSU_MAPS_PATH):
            compress_as_zip(
                os.path.join(NEOSU_MAPS_PATH, dirname),
                os.path.join(STABLE_SONGS_PATH, dirname + ".osz"),
            )
            # 删除源文件夹
            rmtree(os.path.join(NEOSU_MAPS_PATH, dirname))
            print("已重打包：%s" % dirname)
    else:
        print("已放弃重打包")
