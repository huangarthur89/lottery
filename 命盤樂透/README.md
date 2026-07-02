# 天機合參 · 命盤樂透整合系統

這是 Streamlit 版本的命盤與樂透整合系統，入口檔為 `app.py`。

## 伺服器啟動

```bash
streamlit run app.py
```

## 部署需求

部署平台會讀取 `requirements.txt` 安裝套件。請確認以下檔案與資料夾一起上傳：

- `app.py`
- `requirements.txt`
- `lottery_data.db`
- `dream_dict.py`
- `wheel_data.py`
- `pages/`
- `lottery/`
- `排命盤/`
- `.streamlit/config.toml`

## 關於 lottery_data.db

`lottery_data.db` 必須放在專案根目錄並一起上傳。伺服器休眠後重新啟動時，程式會直接讀取這個資料庫，避免每次冷啟動都重新抓取歷史開獎資料。

目前程式使用根目錄資料庫路徑，例如：

```python
root_dir / "lottery_data.db"
```

因此請不要把資料庫移到其他資料夾，也不要在 `.gitignore` 裡加入 `*.db` 或 `lottery_data.db`。

## 注意

樂透開獎屬隨機事件，本系統提供資料分析、命理合參與娛樂參考，不保證中獎或提高中獎機率。
