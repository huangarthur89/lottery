import os

filepath = "/Volumes/MSI 2T/Antigravity/阿舍AI/命盤樂透/pages/3_命盤_樂透合參.py"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# The old block we created in the previous step
old_block = """    # ⚠️ 注意：下面的 HTML 標籤必須「緊貼最左側」，不能有縮排，否則會被當成程式碼顯示！
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
    st.markdown(ticket_html, unsafe_allow_html=True)"""

new_block = """    # ⚠️ 終極修復：將所有的 HTML 壓縮在一起，消除所有「空白行」與「縮排」，徹底防止 Markdown 誤判！
    ticket_html = f\"\"\"<div style="background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); padding: 30px; border-radius: 12px; box-shadow: 0 20px 40px rgba(0,0,0,0.5); border: 2px solid #D4AF37; max-width: 600px; margin: 0 auto; color: #FFF; font-family: 'Noto Serif TC', serif;"><div style="text-align: center; border-bottom: 1px dashed #D4AF37; padding-bottom: 15px; margin-bottom: 20px;"><h2 style="color: #D4AF37; margin: 0; font-weight: 900; letter-spacing: 2px;">STAR★START 天機預測單</h2><p style="color: #94a3b8; font-size: 14px; margin-top: 5px;">生成時間：{today.strftime('%Y-%m-%d %H:%M')}</p></div><div style="margin-bottom: 20px; font-size: 15px; line-height: 1.8;"><div style="display: flex; justify-content: space-between;"><span style="color:#D4AF37;">目標：</span><span>{game_choice}</span></div><div style="display: flex; justify-content: space-between;"><span style="color:#D4AF37;">命主五行：</span><span>{day_master} ({day_element})</span></div><div style="display: flex; justify-content: space-between;"><span style="color:#D4AF37;">生命靈數：</span><span>{life_path}</span></div><div style="display: flex; justify-content: space-between;"><span style="color:#D4AF37;">今日干支：</span><span>{today_ganzhi} ({t_stem_element} / {t_branch_element})</span></div><div style="display: flex; justify-content: space-between;"><span style="color:#D4AF37;">當日流勢：</span><span>天干 {t_s_god} / 地支 {t_b_god}</span></div></div><div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px; border-left: 4px solid #D4AF37; margin-bottom: 20px;"><p style="margin:0; font-size: 14px; color: #cbd5e1;">💡 <b>流日玄學判定：</b>{daily_comment}</p></div><div style="margin-bottom: 15px;"><p style="color: #D4AF37; font-weight: bold; margin-bottom: 5px;">🏆 策略一：天機獨尊組</p><p style="font-size: 20px; font-weight: 900; letter-spacing: 3px; margin:0;">{', '.join([f'{n:02d}' for n in top_6])} <span style="color:#c084fc; font-size: 16px;">[{z2_display}]</span></p></div><div style="margin-bottom: 15px;"><p style="color: #D4AF37; font-weight: bold; margin-bottom: 5px;">🔮 策略二：靈數共振組</p><p style="font-size: 20px; font-weight: 900; letter-spacing: 3px; margin:0;">{', '.join([f'{n:02d}' for n in strat_res])} <span style="color:#c084fc; font-size: 16px;">[{z2_display}]</span></p></div><div style="margin-bottom: 20px;"><p style="color: #D4AF37; font-weight: bold; margin-bottom: 5px;">💧 策略三：貴人生旺反轉組</p><p style="font-size: 20px; font-weight: 900; letter-spacing: 3px; margin:0;">{', '.join([f'{n:02d}' for n in strat_cold])} <span style="color:#c084fc; font-size: 16px;">[{z2_display}]</span></p></div><div style="text-align: center; border-top: 1px dashed #D4AF37; padding-top: 15px;"><p style="color: #64748b; font-size: 12px; margin: 0;">建議您手機截圖保留此單，攜至彩券行作為劃卡依據。</p></div></div>\"\"\"
    
    st.markdown(ticket_html, unsafe_allow_html=True)"""

if old_block in content:
    content = content.replace(old_block, new_block)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
else:
    print("Old block not found!")
