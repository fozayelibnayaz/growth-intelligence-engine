"""
Eagle 3D Intelligence Platform - Telegram Notifications
"""

import requests

class TelegramNotifier:
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_message(self, message):
        """Send text message"""
        url = f"{self.base_url}/sendMessage"
        data = {'chat_id': self.chat_id, 'text': message, 'parse_mode': 'HTML'}
        
        try:
            response = requests.post(url, json=data, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def send_weekly_summary(self, df):
        """Send weekly summary"""
        if df.empty:
            return False
        
        total = len(df)
        avg_score = df['opportunity_score'].mean()
        b2b_count = df['is_b2b'].sum()
        
        message = f"""
🦅 <b>Eagle 3D Weekly Report</b>

📊 Opportunities: {total}
🎯 Avg Score: {avg_score:.1f}
💼 B2B Leads: {b2b_count}

🔥 Top 5:
"""
        
        for idx, row in df.sort_values('opportunity_score', ascending=False).head(5).iterrows():
            message += f"\n{idx+1}. [{row['opportunity_score']:.1f}] {row['title'][:40]}..."
        
        return self.send_message(message)

def get_telegram_setup_instructions():
    return """
📱 TELEGRAM SETUP (5 Min - Free)

1. Open Telegram → Search @BotFather
2. Send /newbot command
3. Choose name: "Eagle 3D Intelligence"
4. Choose username: "eagle3d_intel_bot"
5. Copy BOT TOKEN
6. Search your bot → Click START
7. Search @userinfobot → Get CHAT ID
8. Save both in Settings
"""