import os
import re

filepath = "/Volumes/MSI 2T/Antigravity/阿舍AI/命盤樂透/pages/3_命盤_樂透合參.py"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

marker = "# ==========================================\n# 4. 🔥 真金不怕火煉：歷史回測引擎 (Backtesting System)"

new_code = """
    # ==========================================
    # 🏆 終極功能：生成「專屬天機預測單」與真實當日流勢
    # ==========================================
    st.markdown("---")
    st.markdown("### 📜 專屬天機預測單 (Ticket of Destiny)")

    # 1. 嚴謹計算：真實當日五行與十神流勢
    today = datetime.now()
    lunar_today = Solar.fromYmd(today.year, today.month, today.day).getLunar()
    today_ganzhi = lunar_today.getDayInGanZhi()
    t_stem, t_branch = today_ganzhi[0], today_ganzhi[1]
    
    branch_wu_xing = {'子':'水', '丑':'土', '寅':'木', '卯':'木', '辰':'土', '巳':'火', '午':'火', '未':'土', '申':'金', '酉':'金', '戌':'土', '亥':'水'}
    t_stem_element = wu_xing_map.get(t_stem, '水')
    t_branch_element = branch_wu_xing.get(t_branch, '水')

    # 十神生剋矩陣：依據命主五行 vs 今日五行推演
    ten_gods = {
        '木': {'木':'比劫 (人緣合夥)', '火':'食傷 (靈感產出)', '土':'正偏財 (財富流動)', '金':'官殺 (壓力責任)', '水':'印星 (貴人資源)'},
        '火': {'火':'比劫 (人緣合夥)', '土':'食傷 (靈感產出)', '金':'正偏財 (財富流動)', '水':'官殺 (壓力責任)', '木':'印星 (貴人資源)'},
        '土': {'土':'比劫 (人緣合夥)', '金':'食傷 (靈感產出)', '水':'正偏財 (財富流動)', '木':'官殺 (壓力責任)', '火':'印星 (貴人資源)'},
        '金': {'金':'比劫 (人緣合夥)', '水':'食傷 (靈感產出)', '木':'正偏財 (財富流動)', '火':'官殺 (壓力責任)', '土':'印星 (貴人資源)'},
        '水': {'水':'比劫 (人緣合夥)', '木':'食傷 (靈感產出)', '火':'正偏財 (財富流動)', '土':'官殺 (壓力責任)', '金':'印星 (貴人資源)'}
    }
    
    t_s_god = ten_gods[day_element][t_stem_element]
    t_b_god = ten_gods[day_element][t_branch_element]
    
    # 判斷今日財運強弱給予建議
    if '財' in t_s_god or '財' in t_b_god or '食傷' in t_s_god or '食傷' in t_b_god:
        daily_comment = "今日天地氣場與您命盤呈【生財】之象，直覺敏銳，宜果斷下注。"
    elif '印' in t_s_god or '印' in t_b_god:
        daily_comment = "今日【印星】護體，偏財屬穩健型，建議優先參考系統的大數據策略一。"
    else:
        daily_comment = "今日氣場偏向【克耗】，宜保守小試，隨緣勿執著。"

    # 2. 繪製高質感預測單 UI
    z2_display = f"第二區：{zone2_final:02d}" if zone2_final else "無第二區"
    
    ticket_html = f\"\"\"
    <div style="background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); padding: 30px; border-radius: 12px; box-shadow: 0 20px 40px rgba(0,0,0,0.5); border: 2px solid #D4AF37; max-width: 600px; margin: 0 auto; color: #FFF; font-family: 'Noto Serif TC', serif;">
        <div style="text-align: center; border-bottom: 1px dashed #D4AF37; padding-bottom: 15px; margin-bottom: 20px;">
            <h2 style="color: #D4AF37; margin: 0; font-weight: 900; letter-spacing: 2px;">STAR★START 天機預測單</h2>
            <p style="color: #94a3b8; font-size: 14px; margin-top: 5px;">生成時間：{today.strftime('%Y-%m-%d %H:%M')}</p>
        </div>
        
        <div style="margin-bottom: 20px; font-size: 15px; line-height: 1.8;">
            <div style="display: flex; justify-content: space-between;"><span style="color:#D4AF37;">目標：</span><span>{game_choice}</span></div>
            <div style="display: flex; justify-content: space-between;"><span style="color:#D4AF37;">命主五行：</span><span>{day_master} ({day_element})</span></div>
            <div style="display: flex; justify-content: space-between;"><span style="color:#D4AF37;">生命靈數：</span><span>{life_path}</span></div>
            <div style="display: flex; justify-content: space-between;"><span style="color:#D4AF37;">今日干支：</span><span>{today_ganzhi} ({t_stem_element} / {t_branch_element})</span></div>
            <div style="display: flex; justify-content: space-between;"><span style="color:#D4AF37;">當日流勢：</span><span>天干 {t_s_god} / 地支 {t_b_god}</span></div>
        </div>
        
        <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px; border-left: 4px solid #D4AF37; margin-bottom: 20px;">
            <p style="margin:0; font-size: 14px; color: #cbd5e1;">💡 <b>流日玄學判定：</b>{daily_comment}</p>
        </div>

        <div style="margin-bottom: 15px;">
            <p style="color: #D4AF37; font-weight: bold; margin-bottom: 5px;">🏆 策略一：天機獨尊組</p>
            <p style="font-size: 20px; font-weight: 900; letter-spacing: 3px; margin:0;">{', '.join([f'{n:02d}' for n in top_6])} <span style="color:#c084fc; font-size: 16px;">[{z2_display}]</span></p>
        </div>
        <div style="margin-bottom: 15px;">
            <p style="color: #D4AF37; font-weight: bold; margin-bottom: 5px;">🔮 策略二：靈數共振組</p>
            <p style="font-size: 20px; font-weight: 900; letter-spacing: 3px; margin:0;">{', '.join([f'{n:02d}' for n in strat_res])} <span style="color:#c084fc; font-size: 16px;">[{z2_display}]</span></p>
        </div>
        <div style="margin-bottom: 20px;">
            <p style="color: #D4AF37; font-weight: bold; margin-bottom: 5px;">💧 策略三：貴人生旺反轉組</p>
            <p style="font-size: 20px; font-weight: 900; letter-spacing: 3px; margin:0;">{', '.join([f'{n:02d}' for n in strat_cold])} <span style="color:#c084fc; font-size: 16px;">[{z2_display}]</span></p>
        </div>
        
        <div style="text-align: center; border-top: 1px dashed #D4AF37; padding-top: 15px;">
            <p style="color: #64748b; font-size: 12px; margin: 0;">建議您手機截圖保留此單，攜至彩券行作為劃卡依據。</p>
        </div>
    </div>
    \"\"\"
    st.markdown(ticket_html, unsafe_allow_html=True)
    
    # 3. 提供純文字檔下載按鈕
    export_txt = f\"\"\"STAR★START 天機預測單
生成時間：{today.strftime('%Y-%m-%d %H:%M')}
---------------------------
目標遊戲：{game_choice}
今日流勢：{today_ganzhi} | 天干 {t_s_god} / 地支 {t_b_god}
流日判定：{daily_comment}
---------------------------
🏆 策略一 (天機獨尊)：{', '.join([f'{n:02d}' for n in top_6])} | {z2_display}
🔮 策略二 (靈數共振)：{', '.join([f'{n:02d}' for n in strat_res])} | {z2_display}
💧 策略三 (生旺反轉)：{', '.join([f'{n:02d}' for n in strat_cold])} | {z2_display}
---------------------------
祝您好運！
\"\"\"
    
    col_dl1, col_dl2, col_dl3 = st.columns([1,2,1])
    with col_dl2:
        st.download_button(
            label="💾 下載預測單 (TXT檔)",
            data=export_txt,
            file_name=f"天機預測單_{today.strftime('%Y%m%d')}.txt",
            mime="text/plain",
            use_container_width=True
        )

"""

if marker in content and "🏆 終極功能：生成「專屬天機預測單」與真實當日流勢" not in content:
    content = content.replace(marker, new_code + marker)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
