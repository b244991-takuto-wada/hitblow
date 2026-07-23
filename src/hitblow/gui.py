"""Tkinterで表示するHit & BlowのGUI。"""

import tkinter as tk
from tkinter import ttk

from .core import judge, make_secret
from .cpu import (
    choose_guess,
    is_valid_secret,
    make_candidates,
    narrow_candidates,
)
from .item import high_low
from .timer import elapsed_time, format_time, start_timer


class HitBlowGUI:
    """プレイヤー対CPUのHit & Blowを画面上で進行する。"""

    def __init__(self, root, digits=3):
        self.root = root
        self.digits = digits
        self.timer_job = None
        self.game_token = 0

        self.root.title("Hit & Blow - CPU対戦")
        self.root.geometry("760x620")
        self.root.minsize(680, 560)
        self.root.configure(bg="#0f172a")

        self._set_style()
        self._build_widgets()
        self.reset_game()
        self.root.bind("<Return>", self._on_enter)

    def _set_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Main.TFrame", background="#0f172a")
        style.configure("Panel.TFrame", background="#1e293b")
        style.configure(
            "Title.TLabel",
            background="#0f172a",
            foreground="#f8fafc",
            font=("Yu Gothic UI", 24, "bold"),
        )
        style.configure(
            "Subtitle.TLabel",
            background="#0f172a",
            foreground="#94a3b8",
            font=("Yu Gothic UI", 10),
        )
        style.configure(
            "Info.TLabel",
            background="#1e293b",
            foreground="#e2e8f0",
            font=("Yu Gothic UI", 11, "bold"),
        )
        style.configure(
            "Status.TLabel",
            background="#1e293b",
            foreground="#38bdf8",
            font=("Yu Gothic UI", 12, "bold"),
        )
        style.configure(
            "Accent.TButton",
            font=("Yu Gothic UI", 11, "bold"),
            padding=(14, 8),
            background="#2563eb",
            foreground="white",
        )
        style.map(
            "Accent.TButton",
            background=[("active", "#3b82f6"), ("disabled", "#475569")],
        )
        style.configure(
            "Item.TButton",
            font=("Yu Gothic UI", 10, "bold"),
            padding=(12, 8),
            background="#ca8a04",
            foreground="white",
        )
        style.map(
            "Item.TButton",
            background=[("active", "#eab308"), ("disabled", "#475569")],
        )
        style.configure(
            "Secondary.TButton",
            font=("Yu Gothic UI", 10),
            padding=(10, 7),
        )

    def _build_widgets(self):
        main = ttk.Frame(self.root, padding=20, style="Main.TFrame")
        main.pack(fill="both", expand=True)

        ttk.Label(
            main,
            text="HIT & BLOW",
            style="Title.TLabel",
        ).pack(anchor="w")
        ttk.Label(
            main,
            text=f"CPUより先に、重複なしの{self.digits}桁を当てよう",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(0, 14))

        info = ttk.Frame(main, padding=12, style="Panel.TFrame")
        info.pack(fill="x", pady=(0, 12))
        info.columnconfigure((0, 1, 2), weight=1)

        self.timer_var = tk.StringVar(value="TIME  00:00.00")
        self.turn_var = tk.StringVar(value="数字を設定してください")
        self.count_var = tk.StringVar(value="あなた 0回 / CPU 0回")
        ttk.Label(info, textvariable=self.timer_var, style="Info.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(info, textvariable=self.turn_var, style="Status.TLabel").grid(
            row=0, column=1
        )
        ttk.Label(info, textvariable=self.count_var, style="Info.TLabel").grid(
            row=0, column=2, sticky="e"
        )

        secret_panel = ttk.Frame(main, padding=12, style="Panel.TFrame")
        secret_panel.pack(fill="x", pady=(0, 12))
        ttk.Label(
            secret_panel,
            text=f"CPUに当てさせる{self.digits}桁の数字",
            style="Info.TLabel",
        ).pack(side="left")
        self.secret_var = tk.StringVar()
        self.secret_entry = ttk.Entry(
            secret_panel,
            textvariable=self.secret_var,
            width=12,
            justify="center",
            font=("Consolas", 16, "bold"),
        )
        self.secret_entry.pack(side="left", padx=12)
        self.start_button = ttk.Button(
            secret_panel,
            text="対戦開始",
            command=self.start_game,
            style="Accent.TButton",
        )
        self.start_button.pack(side="left")
        ttk.Button(
            secret_panel,
            text="最初から",
            command=self.reset_game,
            style="Secondary.TButton",
        ).pack(side="right")

        guess_panel = ttk.Frame(main, padding=12, style="Panel.TFrame")
        guess_panel.pack(fill="x", pady=(0, 12))
        ttk.Label(
            guess_panel,
            text="CPUの数字を予想",
            style="Info.TLabel",
        ).pack(side="left")
        self.guess_var = tk.StringVar()
        self.guess_entry = ttk.Entry(
            guess_panel,
            textvariable=self.guess_var,
            width=12,
            justify="center",
            font=("Consolas", 16, "bold"),
        )
        self.guess_entry.pack(side="left", padx=12)
        self.guess_button = ttk.Button(
            guess_panel,
            text="予想する",
            command=self.submit_guess,
            style="Accent.TButton",
        )
        self.guess_button.pack(side="left", padx=(0, 8))
        self.item_button = ttk.Button(
            guess_panel,
            text="HIGH / LOW",
            command=self.use_high_low,
            style="Item.TButton",
        )
        self.item_button.pack(side="left")

        ttk.Label(
            main,
            text="対戦履歴",
            style="Subtitle.TLabel",
        ).pack(anchor="w")

        log_frame = ttk.Frame(main, style="Main.TFrame")
        log_frame.pack(fill="both", expand=True)
        self.log = tk.Text(
            log_frame,
            height=18,
            wrap="word",
            state="disabled",
            bg="#020617",
            fg="#e2e8f0",
            insertbackground="white",
            relief="flat",
            padx=12,
            pady=10,
            font=("Yu Gothic UI", 11),
        )
        scrollbar = ttk.Scrollbar(
            log_frame, orient="vertical", command=self.log.yview
        )
        self.log.configure(yscrollcommand=scrollbar.set)
        self.log.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.log.tag_configure("system", foreground="#94a3b8")
        self.log.tag_configure("player", foreground="#fb7185")
        self.log.tag_configure("cpu", foreground="#38bdf8")
        self.log.tag_configure("item", foreground="#facc15")
        self.log.tag_configure(
            "win", foreground="#4ade80", font=("Yu Gothic UI", 12, "bold")
        )
        self.log.tag_configure(
            "lose", foreground="#f87171", font=("Yu Gothic UI", 12, "bold")
        )

    def reset_game(self):
        """入力と履歴を初期状態に戻す。"""
        self.game_token += 1
        if self.timer_job is not None:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None

        self.cpu_secret = None
        self.player_secret = None
        self.cpu_candidates = []
        self.start_time = None
        self.player_tries = 0
        self.cpu_tries = 0
        self.player_turn = False
        self.game_over = False

        self.secret_var.set("")
        self.guess_var.set("")
        self.timer_var.set("TIME  00:00.00")
        self.turn_var.set("数字を設定してください")
        self.count_var.set("あなた 0回 / CPU 0回")
        self.secret_entry.configure(state="normal")
        self.start_button.configure(state="normal")
        self._set_play_controls(False)
        self._clear_log()
        self._write_log(
            "自分の数字を設定して「対戦開始」を押してください。\n",
            "system",
        )
        self.secret_entry.focus_set()

    def start_game(self):
        """プレイヤーの数字を確定し、対戦を開始する。"""
        player_secret = self.secret_var.get().strip()
        if not is_valid_secret(player_secret, self.digits):
            self.turn_var.set(f"重複なしの{self.digits}桁を入力してください")
            self.secret_entry.focus_set()
            return

        self.game_token += 1
        self.cpu_secret = make_secret(self.digits)
        self.player_secret = player_secret
        self.cpu_candidates = make_candidates(self.digits)
        self.start_time = start_timer()
        self.player_tries = 0
        self.cpu_tries = 0
        self.player_turn = True
        self.game_over = False

        self.secret_entry.configure(state="disabled")
        self.start_button.configure(state="disabled")
        self._set_play_controls(True)
        self.turn_var.set("あなたの手番")
        self._write_log(
            f"対戦開始。あなたの数字は {self.player_secret} です。\n",
            "system",
        )
        self._write_log(
            "HIGH / LOWは手番を消費せずに使用できます。\n",
            "system",
        )
        self._update_timer()
        self.guess_entry.focus_set()

    def submit_guess(self):
        """プレイヤーの予想を判定し、外れたらCPUの手番へ進める。"""
        if not self.player_turn or self.game_over:
            return

        guess = self.guess_var.get().strip()
        if len(guess) != self.digits or not guess.isdigit():
            self.turn_var.set(f"{self.digits}桁の数字を入力してください")
            self.guess_entry.focus_set()
            return

        self.guess_var.set("")
        self.player_tries += 1
        hit, blow = judge(self.cpu_secret, guess)
        current_time = format_time(elapsed_time(self.start_time))
        self._write_log(
            f"あなた  {guess}  Hit={hit}  Blow={blow}  [{current_time}]\n",
            "player",
        )
        self._update_count()

        if hit == self.digits:
            self._finish_game(
                f"あなたの勝ち！ {self.player_tries}回で正解しました。",
                "win",
            )
            return

        self.player_turn = False
        self.turn_var.set("CPUが考えています...")
        self._set_play_controls(False)
        token = self.game_token
        self.root.after(700, lambda: self._cpu_turn(token))

    def _cpu_turn(self, token):
        """CPUの予想を行い、外れたらプレイヤーへ手番を戻す。"""
        if token != self.game_token or self.game_over:
            return

        guess = choose_guess(self.cpu_candidates)
        self.cpu_tries += 1
        hit, blow = judge(self.player_secret, guess)
        self._write_log(
            f"CPU     {guess}  Hit={hit}  Blow={blow}\n",
            "cpu",
        )
        self._update_count()

        if hit == self.digits:
            self._finish_game(
                f"CPUの勝ち！ {self.cpu_tries}回で {self.player_secret} "
                "を当てました。",
                "lose",
            )
            return

        self.cpu_candidates = narrow_candidates(
            self.cpu_candidates, guess, hit, blow
        )
        self.player_turn = True
        self.turn_var.set("あなたの手番")
        self._set_play_controls(True)
        self.guess_entry.focus_set()

    def use_high_low(self):
        """CPUの数字をHIGHとLOWの並びで表示する。"""
        if not self.player_turn or self.game_over:
            return
        result = high_low(self.cpu_secret)
        self._write_log(f"ITEM    HIGH / LOW → {result}\n", "item")
        self.turn_var.set("アイテム使用：あなたの手番を続けます")
        self.guess_entry.focus_set()

    def _finish_game(self, message, tag):
        """勝敗を表示して操作を停止する。"""
        self.game_over = True
        self.player_turn = False
        self._set_play_controls(False)
        self.turn_var.set("対戦終了")
        self._write_log(f"{message}\n", tag)
        self._write_log(
            f"CPUの数字は {self.cpu_secret} でした。\n",
            "system",
        )
        self.timer_var.set(
            f"TIME  {format_time(elapsed_time(self.start_time))}"
        )

    def _update_timer(self):
        """画面上のタイマーを更新する。"""
        if self.start_time is None or self.game_over:
            self.timer_job = None
            return
        self.timer_var.set(
            f"TIME  {format_time(elapsed_time(self.start_time))}"
        )
        self.timer_job = self.root.after(50, self._update_timer)

    def _update_count(self):
        self.count_var.set(
            f"あなた {self.player_tries}回 / CPU {self.cpu_tries}回"
        )

    def _set_play_controls(self, enabled):
        state = "normal" if enabled else "disabled"
        self.guess_entry.configure(state=state)
        self.guess_button.configure(state=state)
        self.item_button.configure(state=state)

    def _clear_log(self):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

    def _write_log(self, message, tag):
        self.log.configure(state="normal")
        self.log.insert("end", message, tag)
        self.log.see("end")
        self.log.configure(state="disabled")

    def _on_enter(self, _event):
        if self.player_secret is None:
            self.start_game()
        else:
            self.submit_guess()


def play_gui(digits=3):
    """GUIを作成し、イベントループを開始する。"""
    root = tk.Tk()
    HitBlowGUI(root, digits)
    root.mainloop()