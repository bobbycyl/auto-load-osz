import os
from queue import Queue
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
KEEP_WITHOUT_ASK = False  # 无需请求用户，自动复制一份 osz 到 stable Songs

monitor = FolderMonitor(MONITOR_PATH, False)
q = Queue()


@monitor.on_event("created", False)
def _(event):
    q.put(event["src_path"])


@monitor.on_event("moved", False)
def _(event):
    q.put(event["dest_path"])


def main(src_path):  # 必须在主线程执行
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
                        "\033[1;33m警告：\033[0m目标路径下已存在同 SID 文件夹：%s"
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
            cp2songs = KEEP_WITHOUT_ASK
            if not KEEP_WITHOUT_ASK:
                keep = input("\033[1m是否保留该谱面？ [%s] (y/[n]) \033[0m" % binfo)
                if keep.lower() == "y":
                    cp2songs = True
            if cp2songs:
                compress_as_zip(
                    os.path.join(NEOSU_MAPS_PATH, binfo),
                    os.path.join(STABLE_SONGS_PATH, binfo + ".osz"),
                )

            rmtree(os.path.join(NEOSU_MAPS_PATH, binfo))
            if REMOVE_SRC:
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
        main(q.get())
except KeyboardInterrupt:
    monitor.stop()
monitor.shutdown_thread_pool(False)
print("监控已停止")

# 询问是否重置 neosu maps 数据
reset_neosu_maps = input(
    "\033[1m是否重置 neosu maps？ (y/[n]) \033[0m"
)
if reset_neosu_maps.lower() == "y":
    if os.path.exists(
        neosu_maps_db := os.path.join(NEOSU_MAPS_PATH, "..", "neosu_maps.db")
    ):
        os.remove(neosu_maps_db)
    clear_folder(NEOSU_MAPS_PATH)
    print("已重置 neosu maps")
else:
    print("已放弃操作")
