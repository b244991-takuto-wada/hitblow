"""CPU対戦機能を追加した Hit & Blow のゲーム進行。"""

from .core import judge, make_secret


def play(digits=3):
    cpu_secret = make_secret(digits)
    print(f"Hit & Blow CPU対戦（{digits} 桁・重複なし）")

    from .cpu import (
        choose_guess,
        is_valid_secret,
        make_candidates,
        narrow_candidates,
    )
    from .timer import start_timer

    while True:
        player_secret = input(
            f"CPUに当てさせる{digits}桁の数字を決めてください > "
        ).strip()
        if is_valid_secret(player_secret, digits):
            break
        print(f"異なる数字を使った{digits}桁の数字で入力してね")

    cpu_candidates = make_candidates(digits)
    start_time = start_timer()
    print("タイマーを開始しました。あなたが先攻です")

    player_tries = 0
    cpu_tries = 0
    while True:
        from .timer import elapsed_time, format_time, timed_input

        player_guess = timed_input(
            "あなたの予想 > ", start_time
        ).strip()

        if len(player_guess) != digits or not player_guess.isdigit():
            print(f"{digits} 桁の数字で入力してね")
            continue

        player_tries += 1
        player_hit, player_blow = judge(cpu_secret, player_guess)
        guess_time = elapsed_time(start_time)
        print(
            f"  \033[31mあなた: Hit={player_hit}  Blow={player_blow}\033[0m  "
        )

        if player_hit == digits:
            print(
                f"あなたの勝ち！ {player_tries} 回で当たり"
                f"（CPUの数字 {cpu_secret}）"
            )
            print(f"クリアタイム: {format_time(guess_time)}")
            break

        cpu_guess = choose_guess(cpu_candidates)
        cpu_tries += 1
        cpu_hit, cpu_blow = judge(player_secret, cpu_guess)
        print(f"CPUの予想 > {cpu_guess}")
        print(f"  CPU: Hit={cpu_hit}  Blow={cpu_blow}")

        if cpu_hit == digits:
            battle_time = elapsed_time(start_time)
            print(
                f"CPUの勝ち！ {cpu_tries} 回であなたの数字"
                f" {player_secret} を当てました"
            )
            print(f"対戦時間: {format_time(battle_time)}")
            print(f"CPUの数字は {cpu_secret} でした")
            break

        cpu_candidates = narrow_candidates(
            cpu_candidates, cpu_guess, cpu_hit, cpu_blow
        )