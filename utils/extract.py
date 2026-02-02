import os
import shutil
import tempfile
from pathlib import Path


def find_deepest_dirs(root_path: Path) -> list[tuple[int, Path]]:
    """
    找到目录树中最深的目录（叶子目录）
    返回: [(depth, dir_path), ...]
    """
    deepest: list[tuple[int, Path]] = []
    max_depth = -1

    for root, dirs, files in os.walk(root_path):
        current_depth = root.count(os.sep) - str(root_path).count(os.sep)

        # 如果没有子目录，就是叶子目录
        if not dirs:
            if current_depth > max_depth:
                max_depth = current_depth
                deepest = [(current_depth, Path(root))]
            elif current_depth == max_depth:
                deepest.append((current_depth, Path(root)))

    return deepest


def extract_innermost(zip_path: str, output_name: str, exist_ok: bool = False):
    """
    解压 zip，找到最内层文件夹，重命名为指定名称
    """
    _zip_path = Path(zip_path)
    _output_name = Path(output_name).resolve()
    print(f"正在解压 {_zip_path} 到 {_output_name}")

    # 如果目录已存在
    if _output_name.exists():
        if not exist_ok:
            raise FileExistsError(f"'{_output_name}' 已存在，解压已终止")
        print(f"=> '{_output_name}' 已存在，将覆盖")

    # 创建临时目录解压
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_path = Path(tmpdir)

        # 解压到临时目录
        shutil.unpack_archive(_zip_path, temp_path, format="zip")

        # 找到最内层目录
        deepest_dirs = find_deepest_dirs(temp_path)

        if not deepest_dirs:
            raise ValueError("压缩包内没有找到任何目录")

        print(f"=> 找到 {len(deepest_dirs)} 个最深层目录（深度 {deepest_dirs[0][0]}）")

        # 创建输出目录
        _output_name.mkdir(exist_ok=True, parents=True)

        # 处理多个同深度目录的情况
        if len(deepest_dirs) == 1:
            # 只有一个最深层，直接移动
            src = deepest_dirs[0][1]
            # 复制内部所有内容，而不是目录本身
            for item in src.iterdir():
                dest = _output_name / item.name
                print(f"==> {dest.name}")
                if item.is_dir():
                    shutil.copytree(item, dest, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, dest)
        else:
            # 多个同深度：每个最深层的内容分别放入子目录
            for _, src in deepest_dirs:
                # 保持原始目录名作为子文件夹
                subdir_name = src.name
                dest_dir = _output_name / subdir_name

                # 重名则覆盖
                dest_dir.mkdir(exist_ok=True)

                # 复制内部内容
                for item in src.iterdir():
                    dest = dest_dir / item.name
                    print(f"==> {dest.name}")
                    if item.is_dir():
                        shutil.copytree(item, dest, dirs_exist_ok=True)
                    else:
                        shutil.copy2(item, dest)
