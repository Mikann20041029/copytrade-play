目的: コピー元(LEADER_ID)のポジション方向(long/short/none)を取得し、自分の口座を同じ方向に合わせる。

まずは必ず DRY_RUN=true で動作確認すること。

必要なSecrets:
- LEADER_ID
- POSITION_RATIO (例: 0.2)
- DRY_RUN ("true" 推奨)
- MIN_USD ("10" 推奨)

任意:
- NANSEN_API_KEY / NANSEN_BASE_URL
- HL_API_BASE / HL_WALLET_ADDRESS / HL_PRIVATE_KEY
