"""CPU対戦で使う予想候補の作成・選択・絞り込み。"""

import random
from itertools import permutations

from .core import judge


def is_valid_secret(value, digits=3):
    """valueが重複なしのdigits桁の数字ならTrueを返す。"""
    return (
        len(value) == digits
        and value.isdigit()
        and len(set(value)) == digits
    )


def make_candidates(digits=3):
    """CPUが予想に使う、重複なしの数字の候補を全て作る。"""
    if not 1 <= digits <= 10:
        raise ValueError("digitsは1以上10以下にしてください")
    return [
        "".join(candidate)
        for candidate in permutations("0123456789", digits)
    ]


def choose_guess(candidates):
    """残っている候補からCPUの予想を一つ選ぶ。"""
    if not candidates:
        raise ValueError("予想できる候補がありません")
    return random.choice(candidates)


def narrow_candidates(candidates, guess, hit, blow):
    """直前のHit・Blowと矛盾する候補を取り除く。"""
    return [
        candidate
        for candidate in candidates
        if judge(candidate, guess) == (hit, blow)
    ]