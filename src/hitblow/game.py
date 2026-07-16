"""ゲームの進行（入力・表示・ループ）。

★ チームで足す機能は **自分の担当の場所**に書く（1機能=1ファイル）。
   下の「ここに足す」場所は3か所（① 開始時 ② 入力コマンド ③ 勝利時）。
   ペアごとに**別の場所**を直すので、並行作業でも衝突しない。
   import も自分の場所の近くに書くこと（ファイル先頭にまとめない＝衝突回避）。
"""

from .core import judge, make_secret


def play(digits=3):
    secret = make_secret(digits)
    print(f"Hit & Blow（{digits} 桁・重複なし）")

    # ===== ① 開始時に足す（難易度・あいさつ など）: ここに書く =====
    from .timer import start_timer

    start_time = start_timer()
    print("タイマーを開始しました")

    tries = 0
    while True:
        # ===== ② 入力コマンドに足す（ヒント など）: ここに書く（import もここに） =====
        from .timer import elapsed_time, format_time, timed_input
        from .item import high_low

        guess = timed_input(
            "予想（highlowでアイテム使用） > ",
            start_time
        ).strip()

        if guess.lower() == "highlow":
            print("HIGH / LOW の結果")
            print(high_low(secret))
            continue

        if len(guess) != digits or not guess.isdigit():
            print(f"{digits} 桁の数字で入力してね")
            continue

        tries += 1
        hit, blow = judge(secret, guess)

        guess_time = elapsed_time(start_time)

        print(
            f"  Hit={hit}  Blow={blow}  "
            f"経過時間={format_time(guess_time)}"
        )

        if hit == digits:

            # ===== ③ 勝利時に足す（スコア・履歴 など）: ここに書く =====
            clear_time = guess_time

            print(f"正解！ {tries} 回で当たり（答え {secret}）")
            print(f"クリアタイム: {format_time(clear_time)}")
            break