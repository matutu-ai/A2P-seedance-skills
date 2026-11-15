#!/usr/bin/env python3
"""Seedance 提示词基础自检。

用法:
  python3 -I scripts/lint_prompt.py PROMPT.txt --total 15 --assets 1 [--banned 品牌A 价格 ...]

检查:
  1. 时间轴 "a–b秒" 是否从 0 起连续覆盖 total 秒，无重叠、无空档
  2. "图片N" 引用是否都不超过素材数量 --assets
  3. 是否出现 --banned 中的违禁词（品牌、价格、功效等）
退出码: 0 通过, 1 有问题。
"""
import argparse
import re
import sys

RANGE = re.compile(r"(\d+(?:\.\d+)?)\s*[–—\-~至到]\s*(\d+(?:\.\d+)?)\s*秒")
NEG = re.compile(r"不要|不得|不|避免|无|没有|禁止|勿")
REF = re.compile(r"图片\s*(\d+)")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--total", type=float, required=True, help="总时长（秒）")
    ap.add_argument("--assets", type=int, required=True, help="素材图片数量")
    ap.add_argument("--banned", nargs="*", default=[], help="不得出现的词")
    a = ap.parse_args()

    text = open(a.file, encoding="utf-8").read()
    problems = []

    # 1 时间轴
    ranges = sorted((float(s), float(e)) for s, e in RANGE.findall(text))
    if not ranges:
        problems.append("未找到形如 “0–5秒” 的时间轴")
    else:
        if ranges[0][0] != 0:
            problems.append(f"时间轴未从 0 秒开始（起点 {ranges[0][0]:g}）")
        for (s1, e1), (s2, e2) in zip(ranges, ranges[1:]):
            if s2 < e1:
                problems.append(f"时间轴重叠: {s1:g}–{e1:g} 与 {s2:g}–{e2:g}")
            elif s2 > e1:
                problems.append(f"时间轴有空档: {e1:g}–{s2:g}")
        for s, e in ranges:
            if e <= s:
                problems.append(f"时间段无效: {s:g}–{e:g}")
        if ranges[-1][1] != a.total:
            problems.append(f"时间轴终点 {ranges[-1][1]:g} 与总时长 {a.total:g} 不符")

    # 2 素材引用
    refs = {int(n) for n in REF.findall(text)}
    bad = sorted(n for n in refs if n < 1 or n > a.assets)
    if bad:
        problems.append(f"引用了不存在的素材: 图片{bad}（共 {a.assets} 张）")
    if a.assets > 0 and refs and set(range(1, a.assets + 1)) - refs:
        missing = sorted(set(range(1, a.assets + 1)) - refs)
        problems.append(f"素材未被引用: 图片{missing}")

    # 3 违禁词
    # 含否定词的句子是排除项（如“不添加价格”），不算违禁
    sentences = [x for x in re.split(r"[。；;\n]", text) if x.strip()]
    positive = [x for x in sentences if not NEG.search(x)]
    for w in a.banned:
        if w and any(w in x for x in positive):
            problems.append(f"出现违禁词（非排除句）: {w}")

    if problems:
        print("未通过:")
        for p in problems:
            print(" -", p)
        return 1
    print(f"通过: 时间轴 {len(ranges)} 段覆盖 0–{a.total:g} 秒；素材引用 {sorted(refs)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
