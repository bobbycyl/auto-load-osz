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

            # 解压到目标路径
            extract_innermost(src_path, os.path.join(NEOSU_MAPS_PATH, binfo), True)

            # 重打包 2 份（新版的 neosu 在这种情况下行为更正常）
            compress_as_zip(
                os.path.join(NEOSU_MAPS_PATH, binfo),
                os.path.join(NEOSU_MAPS_PATH, binfo + ".osz"),
            )
            compress_as_zip(
                os.path.join(NEOSU_MAPS_PATH, binfo),
                os.path.join(STABLE_SONGS_PATH, binfo + ".osz"),
            )

            rmtree(os.path.join(NEOSU_MAPS_PATH, binfo))
            if remove_src:
                # 删除源文件
                os.remove(src_path)
                print("已解压并删除源文件：%s" % binfo)
    except ReadError:
        print("解压失败：%s" % basename)


def clear_folder(folder_path):
    """清空文件夹，保留空文件夹"""
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isfile(item_path):
            os.remove(item_path)  # 删除文件
        elif os.path.isdir(item_path):
            rmtree(item_path)  # 递归删除子文件夹


monitor.start()
print("监控已启动")
print("监控目录：%s\n目标目录：%s" % (MONITOR_PATH, NEOSU_MAPS_PATH))
try:
    while True:
        sleep(3)
        pass
except KeyboardInterrupt:
    monitor.stop()
monitor.shutdown_thread_pool(False)
print("监控已停止")

# 询问是否重置 neosu maps 数据
reset_neosu_maps = input(
    "谱面已重打包至 stable Songs，是否重置 neosu maps 以节约空间？ (y/[n]) "
)
if reset_neosu_maps.lower() == "y":
    os.remove(os.path.join(NEOSU_MAPS_PATH, "..", "neosu_maps.db"))
    clear_folder(NEOSU_MAPS_PATH)
    print("已重置 neosu maps")
else:
    print("已放弃重打包")
