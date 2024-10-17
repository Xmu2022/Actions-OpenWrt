import requests
from bs4 import BeautifulSoup
import json
import re
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from telegram import Bot
import asyncio
import getpass
import os
import pickle
import sys
# 忽略不安全的请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Telegram bot 配置
TELEGRAM_API_TOKEN = '7291969511:AAG0e6C0dlIaGqOUpv_-1JHvQ2lJhTUrP5c'
CHAT_ID = '-1002031723207'

# 初始化 Telegram bot
bot = Bot(token=TELEGRAM_API_TOKEN)

domains = ["69yun69.com"]

def update_main_code():
    """通过 HTTPS 更新网站的最新主程序代码，重试三次"""
    url = "https://69yun69.com/download/scritps/checkin_69.py"  # 这是更新的代码的 URL
    local_path = sys.argv[0]  # 获取当前运行的脚本文件路径
    max_retries = 3

    # 读取当前脚本的内容
    with open(local_path, "r", encoding="utf-8") as file:
        current_code = file.read()

    for attempt in range(max_retries):
        try:
            response = requests.get(url, verify=False)
            if response.status_code == 200:
                new_code = response.text

                # 对比新旧代码
                if new_code.strip() == current_code.strip():
                    print("代码未更新，继续执行本地代码。")
                    return

                # 如果代码有变化，则更新本地文件
                with open(local_path, "w", encoding="utf-8") as file:
                    file.write(new_code)
                print("代码已更新，重新启动脚本...")
                # 重新启动当前脚本
                os.execv(sys.executable, [sys.executable] + sys.argv)
            else:
                print(f"尝试 {attempt + 1} 更新代码失败, 状态码: {response.status_code}")
        except Exception as e:
            print(f"尝试 {attempt + 1} 更新代码失败, 错误: {e}")

    print("无法更新代码，继续执行本地代码。")

# 在程序运行前进行代码更新
update_main_code()



def convert_mb_to_gb(mb_value):
    """将MB转换为GB，并保留两位小数"""
    if mb_value.endswith("MB"):
        mb = float(mb_value.replace("MB", "").strip())
        gb = mb / 1024
        return f"{gb:.2f}GB"
    return mb_value

async def auto_checkin(domain, email, passwd):
    login_url = f"https://{domain}/auth/login"
    checkin_url = f"https://{domain}/user/checkin"
    user_info_url = f"https://{domain}/user"

    session = requests.Session()

    # 模拟登录请求
    login_data = {
        "email": email,
        "passwd": passwd,
        "code": ""
    }
    headers = {
        "Referer": "; auto"
    }

    login_response = session.post(login_url, data=login_data, headers=headers, verify=False)

    # 检查是否登录成功
    if login_response.status_code != 200:
        return None, None, None, None, None

    # 模拟签到请求
    checkin_response = session.post(checkin_url, headers=headers, verify=False)

    # 登录成功后获取用户信息页面
    user_info_response = session.get(user_info_url, headers=headers, verify=False)

    # 提取页面信息
    user_info_text = user_info_response.text

    # 使用 BeautifulSoup 解析 HTML 并提取套餐级别
    soup = BeautifulSoup(user_info_text, 'html.parser')

    # 根据具体的 HTML 结构，定位并提取套餐级别信息
    package_level_div = soup.find('div', class_='card-body pt-2 pl-5 pr-3 pb-1')
    if package_level_div:
        # 提取 p 标签中的文本
        package_level_text = package_level_div.find('p', class_='text-dark-50')
        if package_level_text:
            # 进一步处理提取出的文本，去除多余的空白字符
            package_level = package_level_text.get_text(strip=True).split(':')[0].strip()
        else:
            package_level = "N/A"
    else:
        package_level = "N/A"

    username_match = re.search(r"name: '([^']*)'", user_info_text)
    expire_date_match = re.search(r"Class_Expire': '([^']*)'", user_info_text)
    traffic_match = re.search(r"Unused_Traffic': '([^']*)'", user_info_text)

    username = username_match.group(1) if username_match else "N/A"
    expire_date = expire_date_match.group(1) if expire_date_match else "N/A"
    traffic = convert_mb_to_gb(traffic_match.group(1)) if traffic_match else "N/A"

    checkin_result_json = json.loads(checkin_response.text)

    # 判断签到状态
    if checkin_result_json.get("ret") == 0:
        message = f"您似乎已经签到过了...\n用户名: {username}\n套餐到期时间: {expire_date}\n剩余流量: {traffic}\n套餐级别: {package_level}"
    elif checkin_result_json.get("ret") == 1:
        message = f"签到成功！尊贵的 {package_level}，您获得了 {checkin_result_json.get('traffic')} 流量.\n用户名: {username}\n套餐到期时间: {expire_date}\n剩余流量: {traffic}\n套餐级别: {package_level}"
    else:
        message = f"签到失败!\n{checkin_response.text}\n用户名: {username}\n套餐到期时间: {expire_date}\n剩余流量: {traffic}\n套餐级别: {package_level}"

    return message

async def send_telegram_message(message):
    """发送消息到 Telegram"""
    await bot.send_message(chat_id=CHAT_ID, text=message)

def load_credentials():
    """从文件加载用户名和密码"""
    if os.path.exists('credentials.pkl'):
        with open('credentials.pkl', 'rb') as file:
            return pickle.load(file)
    return [], []

def save_credentials(usernames, passwords):
    """将用户名和密码保存到文件"""
    with open('credentials.pkl', 'wb') as file:
        pickle.dump((usernames, passwords), file)

def update_main_code(url, max_retries=3):
    """尝试更新主程序代码"""
    attempt = 0
    while attempt < max_retries:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                with open(__file__, 'wb') as file:
                    file.write(response.content)
                print("主程序代码已成功更新.")
                return True
            else:
                print(f"更新失败，状态码: {response.status_code}")
        except Exception as e:
            print(f"尝试更新主程序代码时出错: {e}")
        attempt += 1
        print(f"第 {attempt} 次重试...")
    print("无法更新主程序代码，继续执行本地代码.")
    return False

async def main():

    usernames, passwords = load_credentials()

    # 如果没有保存的用户名和密码，要求用户输入
    if not usernames or not passwords:
        # num_accounts = int(input("请输入账户数量: "))
        num_accounts = 1
        for i in range(num_accounts):
            # username = input(f"请输入第 {i + 1} 个用户名: ")
            username = "11111@11111.1"
            # password = getpass.getpass(prompt=f"请输入第 {i + 1} 个密码: ")
            password = '12345678'
            usernames.append(username)
            passwords.append(password)
        save_credentials(usernames, passwords)

    for i in range(len(usernames)):
        for domain in domains:
            print(f"Checking in for {usernames[i]} with domain {domain}")
            checkin_result = await auto_checkin(domain, usernames[i], passwords[i])
            if checkin_result:
                print(checkin_result)
                await send_telegram_message(checkin_result)
                break
            else:
                print('签到失败!')

if __name__ == "__main__":
    asyncio.run(main())
