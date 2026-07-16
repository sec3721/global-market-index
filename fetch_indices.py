import os
import yfinance as yf
import pandas as pd
from datetime import datetime

# 1. 定義要抓取的全球指數 (分類別)
INDICES = {
    "美國三大指數": {
        "^DJI": "道瓊斯工業指數 (Dow Jones)",
        "^GSPC": "標準普爾 500 指數 (S&P 500)",
        "^IXIC": "納斯達克綜合指數 (Nasdaq)",
        "^VIX" : "Volatility Index",
        "DX-Y.NYB": "US Dollar Index ",
        "^RUT" : "羅素2000指數",
        "^GSPTSE": "加拿大標普綜合指數"

    },
    "歐洲主要指數": {
        "^FTSE": "英國富時 100 指數 (FTSE 100)",
        "^GDAXI": "德國 DAX 指數 (DAX)",
        "^FCHI": "法國 CAC 40 指數 (CAC 40)",
        "^STOXX50E" : "EURO STOXX 50I",
        "^N100" : "Euronext100 Index"

    },
    "亞洲主要指數": {
        "^N225": "日本日經 225 指數 (Nikkei 225)",
        "^HSI": "香港恒生指數 (Hang Seng)",
        "000001.SS": "上證綜合指數 (SSE Composite)",
        "^KS11": "韓國綜合指數 (KOSPI)",
        "^BSESN":"印度孟買指數",
        "^AXJO":"S&P/ASX 200",
    },

    "商品" : {
      "GC=F": "Gold Future",
      "SI=F": "Silver Future",
      "PL=F":"Platinum Future",
      "HG=F": "Copper Future",
      "CL=F": "Crude Oil ",
      "BZ=F": "Brent Crude Oil",
      "NG=F":"Natural Gas Future" 
    }
        


    }
       




    


def fetch_data():
    all_data = {}
    
    for category, tickers in INDICES.items():
        category_list = []
        for ticker, name in tickers.items():
            try:
                # 抓取最近 2 天的歷史數據計算升跌幅
                t = yf.Ticker(ticker)
                hist = t.history(period="2d")
                
                if len(hist) >= 1:
                    # 最新收盤價
                    close_price = hist['Close'].iloc[-1]
                    
                    # 計算升跌幅 
                    #（如果歷史數據只有1天，可能無法計算變動，因此作防錯處理）
                    if len(hist) >= 2:
                        prev_close = hist['Close'].iloc[-2]
                        change_pct = ((close_price - prev_close) / prev_close) * 100
                    else:
                        change_pct = 0.0
                        
                    category_list.append({
                        "symbol": ticker,
                        "name": name,
                        "price": f"{close_price:,.2f}",
                        "change_pct": change_pct,
                        "change_pct_str": f"{change_pct:+.2f}%",
                        "status_class": "up" if change_pct > 0 else ("down" if change_pct < 0 else "flat")
                    })
                else:
                    print(f"無法獲取 {ticker} 的歷史數據")
            except Exception as e:
                print(f"獲取 {ticker} ({name}) 出錯: {e}")
                
        all_data[category] = category_list
        
    return all_data

def generate_html(data):
    update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 開始構建 HTML 模板
    html_content = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>全球主要股指行情</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: #f4f6f9;
            color: #333;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: #fff;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }}
        h1 {{
            text-align: center;
            color: #1a1a1a;
            margin-bottom: 5px;
        }}
        .update-time {{
            text-align: center;
            font-size: 14px;
            color: #777;
            margin-bottom: 30px;
        }}
        .category-section {{
            margin-bottom: 35px;
        }}
        .category-title {{
            font-size: 20px;
            font-weight: bold;
            border-left: 5px solid #007bff;
            padding-left: 10px;
            margin-bottom: 15px;
            color: #2c3e50;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 10px;
        }}
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #eef2f5;
        }}
        th {{
            background-color: #f8f9fa;
            color: #6c757d;
            font-weight: 600;
        }}
        .price {{
            font-family: "Courier New", Courier, monospace;
            font-weight: bold;
        }}
        .change {{
            font-weight: bold;
        }}
        /* 綠升紅跌 (華人市場習慣)，若要美股標準可自行調換顏色 */
        .up {{
            color: #28a745; 
        }}
        .down {{
            color: #dc3545;
        }}
        .flat {{
            color: #6c757d;
        }}
        
        /* 手機響應式優化 */
        @media (max-width: 600px) {{
            th, td {{
                padding: 8px 10px;
                font-size: 14px;
            }}
        }}
    </style>
</head>
<body>

<div class="container">
    <h1>全球主要指數行情</h1>
    <div class="update-time">最後更新時間：{update_time} (伺服器時間)</div>
    
    <div id="market-data">
    """
    
    # 動態生成各個分類的表格
    for category, items in data.items():
        html_content += f"""
        <div class="category-section">
            <div class="category-title">{category}</div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 40%;">指數名稱</th>
                        <th style="width: 30%;">最新收市價</th>
                        <th style="width: 30%;">當日升跌 %</th>
                    </tr>
                </thead>
                <tbody>"""
                
        for item in items:
            html_content += f"""
                    <tr>
                        <td><strong>{item['name']}</strong> <span style="color:#999; font-size:12px;">{item['symbol']}</span></td>
                        <td class="price">{item['price']}</td>
                        <td class="change {item['status_class']}">{item['change_pct_str']}</td>
                    </tr>"""
                    
        html_content += """
                </tbody>
            </table>
        </div>"""
        
    html_content += """
    </div>
</div>

</body>
</html>
"""
    # 寫入 index.html
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("成功生成 index.html！")

if __name__ == "__main__":
    print("正在從 Yahoo Finance 獲取即時數據...")
    data = fetch_data()
    print("正在生成網頁...")
    generate_html(data)