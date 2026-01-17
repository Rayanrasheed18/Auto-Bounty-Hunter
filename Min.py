import requests
import subprocess
import os

# --- Configurations ---
TELEGRAM_TOKEN = "8571011779:AAEg45iyKlEDQQFV4BYYsOrcodkCN9d4ihU"
CHAT_ID = "7955490868"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=data)
    except:
        print("Error sending to Telegram")

def get_h1_targets():
    """وەرگرتنی لیستی نوێترین ئەو سایتانەی لە هاکروان پاداشت دەدەن"""
    try:
        url = "https://raw.githubusercontent.com/projectdiscovery/public-bugbounty-programs/master/chaos-bugbounty-list.json"
        res = requests.get(url)
        data = res.json()
        domains = []
        for program in data['programs']:
            # تەنها ئەو سایتانە وەر دەگرێت کە پارە دەدەن
            if "hackerone" in program['url'].lower():
                domains.extend(program['domains'])
        return list(set(domains)) # لابردنی ناوە دووبارەکان
    except:
        return ["starbucks.com", "uber.com", "tesla.com"]

def generate_report(domain, vuln_detail):
    # ڕاپۆرتی کوردی بۆ مۆبایلەکەت
    ku_msg = (
        f"💰 **هەواڵێکی خۆش! کەلێن دۆزرایەوە**\n\n"
        f"🌐 ئامانج: `{domain}`\n"
        f"📝 زانیاری: \n`{vuln_detail}`\n\n"
        f"🚀 ئێستا بڕۆ ناو HackerOne و ڕاپۆرتەکەت بنێرە!"
    )
    
    # ڕاپۆرتی ئینگلیزی ئامادە کراو بۆ ناردن
    en_report = (
        f"Vulnerability Report for {domain}\n"
        f"---------------------------------\n"
        f"I have discovered a security vulnerability during my automated research.\n"
        f"Details: {vuln_detail}\n\n"
        f"Please investigate and remediate this issue."
    )
    
    with open(f"REPORT_{domain}.txt", "w") as f:
        f.write(en_report)
    
    send_telegram(ku_msg)

def start_hunting():
    send_telegram("🛰️ **سیستەمی ڕاوچی دەستی پێکرد...**\nپشکنین بۆ +٢٠٠٠ سایت دەکرێت.")
    targets = get_h1_targets()
    
    # پاشەکەوت کردنی لیستەکە بۆ ناو فایلێک بۆ ئەوەی Nuclei بیخوێنێتەوە
    with open("targets.txt", "w") as f:
        for t in targets:
            f.write(t + "\n")

    # کارپێکردنی Nuclei بۆ دۆزینەوەی هەڵە مەترسیدارەکان
    # -l: لیستی سایتەکان، -severity: تەنها هەڵە گەورەکان
    cmd = "nuclei -l targets.txt -severity critical,high -silent"
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

    if output:
        results = output.decode().strip().split('\n')
        for line in results:
            generate_report("Target Found", line)
    else:
        send_telegram("✅ پشکنین تەواو بوو، هیچ کەلێنێکی نوێ نەدۆزرایەوە.")

if __name__ == "__main__":
    start_hunting()
