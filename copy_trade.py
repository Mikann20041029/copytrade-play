import json
import os
import time
import math
import requests

STATE_PATH = "state.json"

def env(name: str, default: str | None = None) -> str | None:
    v = os.getenv(name)
    if v is None or v == "":
        return default
    return v

def load_state() -> dict:
    try:
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"last_signal": None, "last_action_id": None, "last_seen_ts": None}

def save_state(state: dict) -> None:
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def get_leader_signal(leader_id: str) -> str | None:
    """
    ここが「コピー元の向きを取得」する唯一の関数です。
    戻り値は必ず以下のどれかにしてください:
      - "long"
      - "short"
      - None (ノーポジ)

    画像の人は Nansen を使ったと言っていますが、
    Nansenの具体エンドポイントはあなたのプラン/権限で変わるので
    ここだけ差し替えれば、全体はそのまま動きます。
    """
    # ---- 最小の“仮”実装：何もしない（常にノーポジ） ----
    # 本番にするなら、このreturnを置き換えてください。
    return None

def get_account_usd_available() -> float:
    # 遊びなら固定でもいいですが、ここは将来のために関数化
    # Hyperliquidで実残高を取るならここを実装
    return 20.0

def get_btc_mid_price() -> float:
    # 実運用は取引所のmidを使ってください（ここは仮）
    return 50000.0

def place_order(signal: str | None, usd: float, dry_run: bool) -> str:
    """
    signal:
      - "long" なら買い（ロング）
      - "short"なら売り（ショート）
      - None    ならクローズ
    戻り値: action_id（重複防止のため一意な文字列）
    """
    action_id = f"{int(time.time())}:{signal}:{usd:.2f}"

    if dry_run:
        print(f"[DRY_RUN] action={action_id}")
        return action_id

    # ここにHyperliquid等の発注処理を書く（あなたの鍵・署名方式に依存）
    # 事故防止のため、このテンプレは“実発注”を空実装にしています。
    raise RuntimeError("DRY_RUN=false で動かす前に place_order を実装してください。")

def main():
    leader_id = env("LEADER_ID")
    if not leader_id:
        raise RuntimeError("LEADER_ID が未設定です（GitHub Secretsに入れてください）。")

    position_ratio = float(env("POSITION_RATIO", "0.2"))
    min_usd = float(env("MIN_USD", "10"))
    dry_run = (env("DRY_RUN", "true").lower() == "true")

    state = load_state()
    prev = state.get("last_signal")

    sig = get_leader_signal(leader_id)
    print(f"signal={sig} (prev={prev})")

    if sig == prev:
        print("no change -> skip")
        state["last_seen_ts"] = int(time.time())
        save_state(state)
        return

    av_usd = get_account_usd_available()
    usd = av_usd * position_ratio

    if usd < min_usd:
        print(f"insufficient: ${usd:.2f} < ${min_usd:.2f} -> skip")
        # それでも状態は更新（同じ変化で連続実行しないため）
        state["last_signal"] = sig
        state["last_seen_ts"] = int(time.time())
        save_state(state)
        return

    # 参考表示（サイズ感）
    mid = get_btc_mid_price()
    sz = math.ceil((usd / mid) * 100000) / 100000
    print(f"balance≈${av_usd:.2f} ratio={position_ratio} usd=${usd:.2f} mid≈{mid:.2f} sz≈{sz} BTC")

    action_id = place_order(sig, usd, dry_run=dry_run)
    print(f"done action_id={action_id}")

    state["last_signal"] = sig
    state["last_action_id"] = action_id
    state["last_seen_ts"] = int(time.time())
    save_state(state)

if __name__ == "__main__":
    main()
