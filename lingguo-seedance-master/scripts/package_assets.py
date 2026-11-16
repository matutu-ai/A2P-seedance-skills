#!/usr/bin/env python3
"""Package numbered Seedance references from an explicit case manifest."""

import argparse
import hashlib
import json
import os
import re
import tempfile
import zipfile
from pathlib import Path


TOKEN = re.compile(r"@(图片|视频|音频)([1-9]\d*)")


def local_file(folder: Path, name: str) -> Path:
    if not isinstance(name, str) or not name or Path(name).name != name:
        raise ValueError(f"文件名必须是当前案例目录中的单个文件名：{name!r}")
    path = folder / name
    if not path.is_file() or path.is_symlink() or path.stat().st_size == 0:
        raise ValueError(f"素材不存在、为空或是符号链接：{name}")
    return path


def read_manifest(path: Path):
    folder = path.parent.resolve()
    data = json.loads(path.read_text(encoding="utf-8"))
    prompt = local_file(folder, data["prompt_file"])
    assets_dir = data.get("assets_dir", ".")
    if assets_dir != "." and (
        not isinstance(assets_dir, str)
        or assets_dir == ".."
        or Path(assets_dir).name != assets_dir
    ):
        raise ValueError("assets_dir 必须是当前案例目录中的单层子目录")
    asset_folder = folder / assets_dir
    if not asset_folder.is_dir() or asset_folder.is_symlink():
        raise ValueError(f"素材目录不存在或是符号链接：{assets_dir}")
    archive = data["archive"]
    if not isinstance(archive, str) or Path(archive).name != archive or not archive.endswith(".zip"):
        raise ValueError("archive 必须是当前案例目录中的 .zip 文件名")

    assets = data["assets"]
    if not isinstance(assets, list) or len(assets) < 2:
        raise ValueError("assets 至少列出两项实际要上传的素材")
    seen_tokens = set()
    seen_names = set()
    files = []
    for item in assets:
        token, name = item["token"], item["file"]
        match = TOKEN.fullmatch(token) if isinstance(token, str) else None
        if not match:
            raise ValueError(f"无效素材编号：{token!r}")
        if token in seen_tokens or name in seen_names:
            raise ValueError(f"素材编号或文件名重复：{token} / {name}")
        if not name.startswith(f"{match.group(1)}{match.group(2)}-"):
            raise ValueError(f"编号和文件名不一致：{token} / {name}")
        seen_tokens.add(token)
        seen_names.add(name)
        files.append(local_file(asset_folder, name))

    used_tokens = set(TOKEN.findall(prompt.read_text(encoding="utf-8")))
    used_tokens = {f"@{kind}{number}" for kind, number in used_tokens}
    if used_tokens != seen_tokens:
        raise ValueError(
            f"提示词与清单编号不一致；提示词缺少：{sorted(seen_tokens-used_tokens)}；"
            f"清单缺少：{sorted(used_tokens-seen_tokens)}"
        )
    return folder / archive, files


def verify_archive(archive: Path, files):
    with zipfile.ZipFile(archive) as package:
        names = package.namelist()
        expected = [file.name for file in files]
        if names != expected:
            raise ValueError(f"ZIP 内容或顺序不一致：{names}")
        broken = package.testzip()
        if broken:
            raise ValueError(f"ZIP 文件校验失败：{broken}")
        for file in files:
            source_hash = hashlib.sha256()
            archive_hash = hashlib.sha256()
            with file.open("rb") as source, package.open(file.name) as packed:
                while chunk := source.read(1024 * 1024):
                    source_hash.update(chunk)
                while chunk := packed.read(1024 * 1024):
                    archive_hash.update(chunk)
            if source_hash.digest() != archive_hash.digest():
                raise ValueError(f"ZIP 中的文件与当前原件内容不同：{file.name}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="案例目录中的素材清单 JSON")
    parser.add_argument("--check", action="store_true", help="仅核对现有 ZIP")
    args = parser.parse_args()
    archive, files = read_manifest(args.manifest.resolve())
    if not args.check:
        fd, temporary = tempfile.mkstemp(prefix=".assets-", suffix=".zip", dir=archive.parent)
        os.close(fd)
        try:
            with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as package:
                for file in files:
                    package.write(file, arcname=file.name)
            verify_archive(Path(temporary), files)
            os.replace(temporary, archive)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
    verify_archive(archive, files)
    print(f"PASS: {archive.name} 包含 {len(files)} 项编号素材，和提示词一致")


if __name__ == "__main__":
    main()
