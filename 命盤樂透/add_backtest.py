import os

code_to_append = """
# ==========================================
# 4. 🔥 真金不怕火煉：歷史回測引擎 (Backtesting System)
# ==========================================
st.markdown("---")
with st.expander("🔥 真金不怕火煉：歷史回測引擎", expanded=False):
    st.markdown("透過時光倒流技術，退回至指定期數「之前」，僅使用當時的歷史大數據與您的專屬命理參數進行盲測，驗證系統演算法的真實命中率。")

    db_path = os.path.join(root_dir, 'lottery_data.db')
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        test_table = "lotto" if "大樂透" in game_choice else "super_lotto"
        
        try:
            # 讀取最近 50 期供回測選擇
            test_df = pd.read_sql_query(f"SELECT * FROM {test_table} ORDER BY 期別 DESC LIMIT 50", conn)
            
            if not test_df.empty and len(test_df) > 10:
                options = test_df['期別'].astype(str).tolist()
                # 排除最新一期 (index 0)，從第二期開始回測，避免拿已經知道的結果自欺欺人
                target_issue = st.selectbox("⏳ 選擇時光回測目標 (將隱藏該期與未來的數據進行盲測)：", options[1:20]) 
                
                if st.button("⚖️ 啟動盲測驗證", use_container_width=True):
                    # 1. 切割時空：分離目標期與其過去的歷史數據
                    target_idx = test_df[test_df['期別'].astype(str) == target_issue].index[0]
                    target_data = test_df.iloc[target_idx]
                    # 嚴格限制：只拿目標期「之前」的 30 期數據當作歷史
                    history_data = test_df.iloc[target_idx + 1 : target_idx + 31] 
                    
                    num_cols = ['N1', 'N2', 'N3', 'N4', 'N5', 'N6']
                    actual_nums = target_data[num_cols].values.tolist()
                    
                    # 2. 重新計算歷史環境 (假裝回到過去重新算頻率與遺漏)
                    hist_all_nums = history_data[num_cols].values.flatten()
                    hist_freq = pd.Series(hist_all_nums).value_counts().to_dict()
                    
                    hist_overdue = {}
                    for n in range(1, max_num + 1):
                        matches = history_data[history_data[num_cols].isin([n]).any(axis=1)].index
                        if len(matches) > 0:
                            hist_overdue[n] = int(matches.min() - (target_idx + 1))
                        else:
                            hist_overdue[n] = 30
                            
                    # 3. 啟動合參大腦：執行與主程式完全相同的權重演算法
                    bt_scores = {}
                    for n in range(1, max_num + 1):
                        score = 0
                        tail = n % 10
                        score += min(20, (hist_freq.get(n, 0) / 15) * 20)
                        score += min(20, (hist_overdue.get(n, 0) / 30) * 20)
                        if tail in self_tails: score += 15
                        elif tail in mother_tails: score += 10
                        if tail == wealth_star_tail: score += 5
                        if n == life_path or sum(int(d) for d in str(n)) == life_path or tail == life_path: 
                            score += 20
                        elif n % life_path == 0: 
                            score += 10
                        bt_scores[n] = round(score, 1)

                    # 擷取當時算出來的「策略一：天機獨尊組」前 6 碼
                    bt_sorted = sorted(bt_scores.items(), key=lambda x: x[1], reverse=True)
                    bt_top_6 = [x[0] for x in bt_sorted[:6]]
                    
                    # 4. 對答案與畫面渲染
                    hits = set(bt_top_6).intersection(set(actual_nums))
                    
                    def render_bt_balls(nums, actuals):
                        html = ""
                        for n in sorted(nums):
                            if n in actuals:
                                # 命中時，球會放大並閃爍紅光
                                html += f"<div class='ball ball-red' style='transform: scale(1.15); box-shadow: 0px 0px 12px #D32F2F; border: 2px solid #FFCDD2;'>{n:02d}</div>"
                            else:
                                # 沒命中時，球會變成灰色並半透明
                                html += f"<div class='ball ball-gold' style='opacity: 0.35; filter: grayscale(100%);'>{n:02d}</div>"
                        return html
                    
                    actual_html = "".join([f"<div class='ball ball-blue'>{n:02d}</div>" for n in sorted(actual_nums)])
                    predict_html = render_bt_balls(bt_top_6, actual_nums)
                    
                    st.success(f"✅ 時光回測完畢！時空座標定錨於：【{target_issue}】期")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown("**📌 當期真實開獎號碼：**")
                        st.markdown(actual_html, unsafe_allow_html=True)
                    with col_b:
                        st.markdown("**🎯 系統盲測推薦 (策略一)：** *(亮紅色為成功命中)*")
                        st.markdown(predict_html, unsafe_allow_html=True)
                    
                    st.info(f"**📊 數據報告：** 在嚴格遮蔽未來數據的盲測條件下，演算法第一區成功命中了 **{len(hits)}** 顆號碼！")
            else:
                st.warning("資料庫資料量不足，無法執行回測，請等待資料庫累積更多期數。")
        except Exception as e:
            st.error(f"回測引擎讀取失敗，請確認資料庫格式。錯誤: {e}")
        finally:
            conn.close()
    else:
        st.info("⚠️ 找不到 `lottery_data.db` 資料庫，回測引擎暫時封印。請先確保根目錄存在有效資料庫。")
"""

with open("/Volumes/MSI 2T/Antigravity/阿舍AI/命盤樂透/pages/3_命盤_樂透合參.py", "a", encoding="utf-8") as f:
    f.write("\n")
    f.write(code_to_append)
