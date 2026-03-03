#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import threading
import webbrowser
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import imaplib
import poplib
import email
import re
import time
import io
from datetime import datetime, timedelta
from email.header import decode_header
import PyPDF2

app = Flask(__name__, static_folder='frontend')
CORS(app)

def decode_email_header(header):
    """解码邮件头部"""
    if header is None:
        return ""
    
    decoded_parts = decode_header(header)
    result = []
    
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            if encoding:
                try:
                    result.append(part.decode(encoding))
                except:
                    result.append(part.decode('utf-8', errors='ignore'))
            else:
                result.append(part.decode('utf-8', errors='ignore'))
        else:
            result.append(str(part))
    
    return ''.join(result)

def get_email_body(msg):
    """提取邮件正文"""
    body = ""
    
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            
            if "attachment" not in content_disposition:
                if content_type == "text/plain":
                    try:
                        payload = part.get_payload(decode=True)
                        charset = part.get_content_charset() or 'utf-8'
                        body += payload.decode(charset, errors='ignore')
                    except:
                        pass
                elif content_type == "text/html" and not body:
                    try:
                        payload = part.get_payload(decode=True)
                        charset = part.get_content_charset() or 'utf-8'
                        body += payload.decode(charset, errors='ignore')
                    except:
                        pass
    else:
        try:
            payload = msg.get_payload(decode=True)
            charset = msg.get_content_charset() or 'utf-8'
            body = payload.decode(charset, errors='ignore')
        except:
            pass
    
    return body

def parse_bill_from_text(text, filename=""):
    """从文本中解析账单信息"""
    bills = []
    
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        if not line:
            continue
        
        patterns = [
            (r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})\s+(.+?)\s+([-]?\d+\.?\d*)', 'date_merchant_amount'),
            (r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\s+(.+?)\s+([-]?\d+\.?\d*)', 'date_merchant_amount'),
            (r'(.+?)\s+([-]?\d+\.?\d*)\s+(\d{4}[-/]\d{1,2}[-/]\d{1,2})', 'merchant_amount_date'),
        ]
        
        for pattern, pattern_type in patterns:
            match = re.search(pattern, line)
            if match:
                if pattern_type == 'date_merchant_amount':
                    date_str, merchant, amount = match.groups()
                elif pattern_type == 'merchant_amount_date':
                    merchant, amount, date_str = match.groups()
                else:
                    continue
                
                try:
                    amount_float = float(amount)
                    
                    if amount_float == 0:
                        continue
                    
                    if re.search(r'还款|退款|返还|入账', merchant, re.IGNORECASE):
                        continue
                    
                    date_formats = [
                        '%Y-%m-%d', '%Y/%m/%d',
                        '%d-%m-%Y', '%d/%m/%Y',
                        '%m-%d-%Y', '%m/%d/%Y',
                    ]
                    
                    parsed_date = None
                    for fmt in date_formats:
                        try:
                            parsed_date = datetime.strptime(date_str, fmt)
                            break
                        except:
                            pass
                    
                    if not parsed_date:
                        continue
                    
                    category = categorize_merchant(merchant)
                    
                    bills.append({
                        'date': parsed_date.strftime('%Y-%m-%d'),
                        'merchant': merchant.strip(),
                        'amount': abs(amount_float),
                        'type': '支出' if amount_float < 0 else '收入',
                        'category': category,
                        'source': filename
                    })
                    
                except:
                    continue
    
    return bills

def categorize_merchant(merchant):
    """根据商家名称智能分类"""
    merchant_lower = merchant.lower()
    
    categories = {
        "餐饮美食": {
            "keywords": ["美团", "饿了么", "肯德基", "kfc", "麦当劳", "星巴克", "咖啡", "餐厅", 
                        "美食", "小吃", "火锅", "烧烤", "奶茶", "外卖", "饭堂", "餐饮", 
                        "德克士", "必胜客", "海底捞", "西贝", "真功夫", "华莱士", "沙县",
                        "拉面", "麻辣烫", "炸鸡", "汉堡", "披萨", "寿司", "烧烤", "串串"],
            "icon": "🍽️"
        },
        "网上购物": {
            "keywords": ["淘宝", "天猫", "京东", "拼多多", "pinduoduo", "淘宝网", "tmall",
                        "京东商城", "苏宁", "唯品会", "得物", "闲鱼", "网易严选", "考拉",
                        "shop", "store", "商城", "网购", "快递", "物流", "配送"],
            "icon": "🛒"
        },
        "交通出行": {
            "keywords": ["滴滴", "出行", "打车", "uber", "地铁", "公交", "高铁", "火车",
                        "机票", "航空", "机场", "加油站", "停车", "高速", "交通", "单车",
                        "摩拜", "ofo", "哈啰", "曹操", "神州", "一嗨", "租车"],
            "icon": "🚗"
        },
        "生活服务": {
            "keywords": ["水电费", "燃气", "物业", "房租", "水电", "宽带", "话费", "充值",
                        "移动", "联通", "电信", "生活", "缴费", "服务", "维修", "家政"],
            "icon": "🏠"
        },
        "娱乐休闲": {
            "keywords": ["电影", "游戏", "音乐", "视频", "会员", "vip", "娱乐", "休闲",
                        "健身", "运动", "旅游", "景点", "门票", "ktv", "网吧", "桌游"],
            "icon": "🎮"
        },
        "医疗健康": {
            "keywords": ["医院", "药店", "药品", "医疗", "健康", "体检", "诊所", "牙科",
                        "眼镜", "保健", "治疗", "门诊", "挂号"],
            "icon": "🏥"
        },
        "教育培训": {
            "keywords": ["教育", "培训", "课程", "学习", "书店", "图书", "考试", "学校",
                        "培训", "辅导", "网课", "知识", "付费", "专栏"],
            "icon": "📚"
        },
        "转账红包": {
            "keywords": ["转账", "红包", "微信", "支付宝", "qq", "转账", "收款", "付款",
                        "发红包", "收红包", "aa", "收款码"],
            "icon": "💰"
        },
        "其他消费": {
            "keywords": [],
            "icon": "📦"
        }
    }
    
    for category, info in categories.items():
        if category == "其他消费":
            continue
        for keyword in info["keywords"]:
            if keyword in merchant_lower:
                return category
    
    return "其他消费"

def parse_bill_from_pdf_text(pdf_text, filename=""):
    """从PDF文本中解析账单信息"""
    bills = []
    
    lines = pdf_text.split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        if not line:
            continue
        
        if re.search(r'消费日期|交易日期|记账日期|日期', line):
            continue
        
        if re.search(r'摘要|商户|交易摘要', line):
            continue
        
        if re.search(r'金额|人民币|交易金额', line):
            continue
        
        if re.search(r'合计|总计|余额', line):
            continue
        
        patterns = [
            (r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})\s+(.+?)\s+([-]?\d+\.?\d*)', 'date_merchant_amount'),
            (r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\s+(.+?)\s+([-]?\d+\.?\d*)', 'date_merchant_amount'),
            (r'(.+?)\s+([-]?\d+\.?\d*)\s+(\d{4}[-/]\d{1,2}[-/]\d{1,2})', 'merchant_amount_date'),
        ]
        
        for pattern, pattern_type in patterns:
            match = re.search(pattern, line)
            if match:
                if pattern_type == 'date_merchant_amount':
                    date_str, merchant, amount = match.groups()
                elif pattern_type == 'merchant_amount_date':
                    merchant, amount, date_str = match.groups()
                else:
                    continue
                
                try:
                    amount_float = float(amount)
                    
                    if amount_float == 0:
                        continue
                    
                    if re.search(r'还款|退款|返还|入账', merchant, re.IGNORECASE):
                        continue
                    
                    date_formats = [
                        '%Y-%m-%d', '%Y/%m/%d',
                        '%d-%m-%Y', '%d/%m/%Y',
                        '%m-%d-%Y', '%m/%d/%Y',
                    ]
                    
                    parsed_date = None
                    for fmt in date_formats:
                        try:
                            parsed_date = datetime.strptime(date_str, fmt)
                            break
                        except:
                            pass
                    
                    if not parsed_date:
                        continue
                    
                    category = categorize_merchant(merchant)
                    
                    bills.append({
                        'date': parsed_date.strftime('%Y-%m-%d'),
                        'merchant': merchant.strip(),
                        'amount': abs(amount_float),
                        'type': '支出' if amount_float < 0 else '收入',
                        'category': category,
                        'source': filename
                    })
                    
                except:
                    continue
    
    return bills

@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

@app.route('/frontend/<path:filename>')
def serve_frontend(filename):
    return send_from_directory('frontend', filename)

@app.route('/api/fetch-bills', methods=['POST'])
def fetch_bills():
    try:
        data = request.json
        user_email = data.get('email')
        auth_code = data.get('authCode')
        imap_server = data.get('imapServer')
        use_pop3 = data.get('usePop3', True)
        
        if not user_email or not auth_code:
            return jsonify({
                'success': False,
                'message': '请输入邮箱和授权码'
            })
        
        bills = []
        email_count = 0
        
        if use_pop3:
            try:
                if '163.com' in user_email:
                    mail = poplib.POP3_SSL('pop.163.com', 995)
                elif 'qq.com' in user_email:
                    mail = poplib.POP3_SSL('pop.qq.com', 995)
                elif 'gmail.com' in user_email:
                    mail = poplib.POP3_SSL('pop.gmail.com', 995)
                else:
                    mail = poplib.POP3_SSL(imap_server.replace('imap', 'pop'), 995)
                
                mail.user(user_email)
                mail.pass_(auth_code)
                
                num_messages = len(mail.list()[1])
                email_count = num_messages
                
                for i in range(min(num_messages, 50)):
                    try:
                        resp, lines, octets = mail.retr(i + 1)
                        raw_email = b'\r\n'.join(lines)
                        msg = email.message_from_bytes(raw_email)
                        
                        subject = decode_email_header(msg.get('Subject'))
                        
                        if '平安银行' in subject or '信用卡' in subject or '账单' in subject:
                            for part in msg.walk():
                                if part.get_content_maintype() == 'multipart':
                                    continue
                                if part.get('Content-Disposition') is None:
                                    continue
                                
                                file_name = decode_email_header(part.get_filename())
                                
                                if file_name and file_name.lower().endswith('.pdf'):
                                    try:
                                        pdf_data = part.get_payload(decode=True)
                                        pdf_file = io.BytesIO(pdf_data)
                                        pdf_reader = PyPDF2.PdfReader(pdf_file)
                                        
                                        pdf_text = ""
                                        for page in pdf_reader.pages:
                                            pdf_text += page.extract_text() + "\n"
                                        
                                        pdf_bills = parse_bill_from_pdf_text(pdf_text, file_name)
                                        bills.extend(pdf_bills)
                                        
                                    except Exception as e:
                                        print(f"解析PDF失败: {str(e)}")
                                        continue
                    except Exception as e:
                        print(f"处理邮件失败: {str(e)}")
                        continue
                
                mail.quit()
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': f'POP3连接失败: {str(e)}。请检查授权码是否正确。'
                })
        else:
            try:
                if '163.com' in user_email:
                    mail = imaplib.IMAP4_SSL('imap.163.com', 993)
                elif 'qq.com' in user_email:
                    mail = imaplib.IMAP4_SSL('imap.qq.com', 993)
                elif 'gmail.com' in user_email:
                    mail = imaplib.IMAP4_SSL('imap.gmail.com', 993)
                else:
                    mail = imaplib.IMAP4_SSL(imap_server, 993)
                
                mail.login(user_email, auth_code)
                
                mail.select('INBOX')
                
                typ, search_data = mail.search(None, 'ALL')
                email_ids = search_data[0].split()
                email_count = len(email_ids)
                
                for email_id in email_ids[-50:]:
                    try:
                        typ, msg_data = mail.fetch(email_id, '(RFC822)')
                        for response_part in msg_data:
                            if isinstance(response_part, tuple):
                                msg = email.message_from_bytes(response_part[1])
                                
                                subject = decode_email_header(msg.get('Subject'))
                                
                                if '平安银行' in subject or '信用卡' in subject or '账单' in subject:
                                    for part in msg.walk():
                                        if part.get_content_maintype() == 'multipart':
                                            continue
                                        if part.get('Content-Disposition') is None:
                                            continue
                                        
                                        file_name = decode_email_header(part.get_filename())
                                        
                                        if file_name and file_name.lower().endswith('.pdf'):
                                            try:
                                                pdf_data = part.get_payload(decode=True)
                                                pdf_file = io.BytesIO(pdf_data)
                                                pdf_reader = PyPDF2.PdfReader(pdf_file)
                                                
                                                pdf_text = ""
                                                for page in pdf_reader.pages:
                                                    pdf_text += page.extract_text() + "\n"
                                                
                                                pdf_bills = parse_bill_from_pdf_text(pdf_text, file_name)
                                                bills.extend(pdf_bills)
                                                
                                            except Exception as e:
                                                print(f"解析PDF失败: {str(e)}")
                                                continue
                    except Exception as e:
                        print(f"处理邮件失败: {str(e)}")
                        continue
                
                mail.close()
                mail.logout()
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': f'IMAP连接失败: {str(e)}。请检查授权码是否正确。'
                })
        
        if not bills:
            return jsonify({
                'success': False,
                'message': f'已扫描 {email_count} 封邮件，但未找到平安银行账单。请确保邮箱中有平安银行信用卡账单邮件。'
            })
        
        bills.sort(key=lambda x: x['date'], reverse=True)
        
        return jsonify({
            'success': True,
            'message': f'成功读取 {email_count} 封邮件，解析出 {len(bills)} 条账单记录',
            'data': bills
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'发生错误: {str(e)}'
        })

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat()
    })

def run_flask():
    app.run(host='127.0.0.1', port=8080, debug=False, use_reloader=False)

def main():
    print("🚀 平安银行账单分析系统启动中...")
    print("📍 正在初始化...")
    
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    time.sleep(1)
    
    try:
        import webview
        window = webview.create_window(
            '平安银行账单分析系统',
            'http://127.0.0.1:8080/',
            width=1400,
            height=900,
            resizable=True,
            min_size=(1200, 700)
        )
        webview.start()
    except ImportError:
        print("❌ 未安装 pywebview 库")
        print("正在使用浏览器打开...")
        webbrowser.open('http://127.0.0.1:8080/')
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 系统已关闭")

if __name__ == '__main__':
    main()
