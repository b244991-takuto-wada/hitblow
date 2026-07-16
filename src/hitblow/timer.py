"""Hit & Blow のカウントアップタイマー。"""

import msvcrt
import sys
import time


def start_timer():
    """タイマーを開始し、開始時刻を返す。"""
    return time.perf_counter()


def elapsed_time(start_time):
    """開始時刻から現在までの経過秒数を返す。"""
    return time.perf_counter() - start_time


def format_time(seconds):
    """経過秒数を「分:秒.百分の一秒」の形に整える。"""
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    return f"{minutes:02d}:{remaining_seconds:05.2f}"


def _draw_input_line(prompt, entered, start_time, previous_length):
    """経過時間と入力欄を同じ行に表示する。"""
    display = (
        f"経過時間: {format_time(elapsed_time(start_time))}"
        f" | {prompt}{''.join(entered)}"
    )
    spaces = " " * max(0, previous_length - len(display))
    sys.stdout.write(f"\r{display}{spaces}")
    sys.stdout.flush()
    return len(display)


def timed_input(prompt, start_time, refresh_interval=0.05):
    """経過時間を更新しながら予想を入力する。"""
    entered = []
    previous_length = 0

    while True:
        previous_length = _draw_input_line(
            prompt, entered, start_time, previous_length
        )

        if msvcrt.kbhit():
            char = msvcrt.getwch()

            if char in ("\r", "\n"):
                _draw_input_line(prompt, entered, start_time, previous_length)
                print()
                return "".join(entered)

            if char == "\x03":
                raise KeyboardInterrupt

            if char == "\b":
                if entered:
                    entered.pop()
            elif char in ("\x00", "\xe0"):
                # 矢印キーなどは読み捨てる
                msvcrt.getwch()
            elif char.isprintable():
                entered.append(char)

        time.sleep(refresh_interval)