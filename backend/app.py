#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import imaplib
import poplib
import email
import re
import time
import io
import os
from datetime import datetime, timedelta
from email.header import decode_header
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import PyPDF2

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

def decode_email_header(header):
    """解码邮件头部"""
    if not header:
        return ""
    
    decoded = []
    for part, encoding in decode_header(header):
        if isinstance(part, bytes):
            decoded.append(part.decode(encoding or 'utf-8', errors='ignore'))
        else:
            decoded.append(str(part))
    return ''.join(decoded)

def parse_bill_from_email(msg):
    """从邮件内容中解析账单数据"""
    bills = []
    body = ""  # 初始化body变量
    
    print("\n========== 开始解析邮件 ==========")
    print(f"邮件主题: {msg.get('Subject', '')}")
    print(f"发件人: {msg.get('From', '')}")
    
    # 检查邮件是否包含附件
    if msg.is_multipart():
        print("邮件是多部分格式")
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))
            filename = part.get_filename()
            
            print(f"\n部分类型: {content_type}")
            print(f"Content-Disposition: {content_disposition}")
            print(f"文件名: {filename}")
            
            # 检查是否是PDF附件
            if filename:
                # 解码文件名
                try:
                    from email.header import decode_header
                    decoded_filename = decode_header(filename)[0][0]
                    if isinstance(decoded_filename, bytes):
                        decoded_filename = decoded_filename.decode('gbk', errors='ignore')
                    print(f"✅ 找到附件: {decoded_filename}")
                    
                    if decoded_filename.lower().endswith('.pdf'):
                        print(f"✅ 找到PDF附件: {decoded_filename}")
                        # 获取PDF内容
                        pdf_content = part.get_payload(decode=True)
                        print(f"PDF文件大小: {len(pdf_content)} 字节")
                        
                        # 解析PDF内容
                        try:
                            pdf_file = io.BytesIO(pdf_content)
                            pdf_reader = PyPDF2.PdfReader(pdf_file)
                            print(f"PDF页数: {len(pdf_reader.pages)}")
                            
                            # 提取所有页面的文本
                            pdf_text = ""
                            for page_num, page in enumerate(pdf_reader.pages):
                                page_text = page.extract_text()
                                pdf_text += page_text
                                print(f"\n第 {page_num + 1} 页内容（前300字符）:\n{page_text[:300]}")
                            
                            # 从PDF文本中解析账单数据
                            pdf_bills = parse_bill_from_pdf_text(pdf_text, decoded_filename)
                            bills.extend(pdf_bills)
                            print(f"从PDF中提取了 {len(pdf_bills)} 条账单记录")
                            
                        except Exception as e:
                            print(f"解析PDF失败: {e}")
                except Exception as e:
                    print(f"解码文件名失败: {e}")
                
            # 获取邮件正文
            if content_type == "text/plain" and "attachment" not in content_disposition:
                try:
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    print(f"\n邮件正文内容（前500字符）:\n{body[:500]}")
                except:
                    try:
                        body = part.get_payload(decode=True).decode('gbk', errors='ignore')
                        print(f"\n邮件正文内容（前500字符）:\n{body[:500]}")
                    except:
                        print("无法解码邮件正文")
                        continue
    else:
        print("邮件是单部分格式")
        try:
            body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            print(f"\n邮件正文内容（前500字符）:\n{body[:500]}")
        except:
            try:
                body = msg.get_payload(decode=True).decode('gbk', errors='ignore')
                print(f"\n邮件正文内容（前500字符）:\n{body[:500]}")
            except:
                print("无法解码邮件正文")
                body = ""
    
    print("\n========== 邮件解析结束 ==========\n")
    
    # 解析账单数据 - 支持多种格式
    patterns = [
        # 格式1: 日期 商家 金额
        r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})\s+([^\d]+?)\s+(\d+\.?\d*)\s*元',
        # 格式2: 日期 金额 商家
        r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})\s+(\d+\.?\d*)\s*元\s+([^\d]+)',
        # 格式3: 商家 日期 金额
        r'([^\d]+?)\s+(\d{4}[-/]\d{1,2}[-/]\d{1,2})\s+(\d+\.?\d*)\s*元',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, body)
        for match in matches:
            try:
                if len(match) == 3:
                    if re.match(r'\d{4}[-/]\d{1,2}[-/]\d{1,2}', match[0]):
                        date = match[0].replace('/', '-')
                        merchant = match[1].strip()
                        amount = float(match[2])
                    else:
                        merchant = match[0].strip()
                        date = match[1].replace('/', '-')
                        amount = float(match[2])
                    
                    if amount > 0:
                        bills.append({
                            "date": date,
                            "merchant": merchant,
                            "category": categorize_merchant(merchant),
                            "amount": amount
                        })
            except:
                continue
    
    return bills

def parse_bill_from_pdf_text(pdf_text, filename):
    """从PDF文本中解析账单数据"""
    bills = []
    
    print(f"\n========== 开始解析PDF文本 ==========")
    print(f"PDF文本长度: {len(pdf_text)}")
    
    # 平安银行账单格式解析
    # 格式: 交易日期 记账日期 交易说明 人民币金额
    # 例如: 2024-07-28 2024-07-28 （特约）美团 ￥20.00
    
    # 匹配平安银行账单格式
    pattern = r'(\d{4}-\d{2}-\d{2})\s+\d{4}-\d{2}-\d{2}\s+(.+?)\s+￥(-?\d+\.?\d*)'
    
    matches = re.findall(pattern, pdf_text)
    print(f"匹配到 {len(matches)} 条交易记录")
    
    for match in matches:
        try:
            date = match[0]
            merchant = match[1].strip()
            amount_str = match[2]
            
            # 处理金额
            amount = abs(float(amount_str))
            
            # 过滤掉无效数据和还款相关记录
            exclude_keywords = ['交易说明', 'Description', '人民币金额', 'RMB Amount', 
                              '还款', '还款金抵扣', '一键还款', '口袋银行', '自动还款', 
                              '溢缴款', '利息', '手续费', '年费', '滞纳金', '退款', 
                              '退货', '冲正', '撤销', '退回']
            
            is_excluded = any(keyword in merchant for keyword in exclude_keywords)
            
            if amount > 0 and len(merchant) > 0 and not is_excluded:
                bills.append({
                    "date": date,
                    "merchant": merchant,
                    "category": categorize_merchant(merchant),
                    "amount": amount,
                    "source": filename
                })
                print(f"  ✅ {date} | {merchant} | ￥{amount}")
            elif is_excluded:
                print(f"  ❌ 过滤掉还款/费用记录: {merchant}")
        except Exception as e:
            print(f"解析账单失败: {e}")
            continue
    
    print(f"从PDF中提取了 {len(bills)} 条有效账单记录")
    print("========== PDF文本解析结束 ==========\n")
    
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
            "keywords": ["淘宝", "天猫", "京东", "拼多多", "超市", "便利店", "盒马", "永辉", 
                        "沃尔玛", "家乐福", "大润发", "苏宁", "国美", "唯品会", "得物",
                        "网易严选", "小红书", "抖音", "快手", "直播"],
            "icon": "🛒"
        },
        "交通出行": {
            "keywords": ["滴滴", "出行", "打车", "地铁", "公交", "火车", "机票", "酒店", 
                        "高德", "百度地图", "携程", "去哪儿", "飞猪", "12306", "交通卡",
                        "加油", "中石油", "中石化", "停车", "高速"],
            "icon": "🚗"
        },
        "娱乐休闲": {
            "keywords": ["电影", "游戏", "音乐", "视频", "娱乐", "ktv", "网吧", "网咖",
                        "腾讯视频", "爱奇艺", "优酷", "b站", "哔哩", "steam", "王者荣耀",
                        "和平精英", "剧本杀", "密室", "游乐场", "景区", "门票"],
            "icon": "🎮"
        },
        "医疗健康": {
            "keywords": ["药店", "医院", "诊所", "药房", "医疗", "健康", "体检", "牙科",
                        "眼镜", "药房", "大参林", "老百姓", "益丰", "同仁堂"],
            "icon": "🏥"
        },
        "教育培训": {
            "keywords": ["教育", "培训", "课程", "学习", "书籍", "书店", "网校", "英语",
                        "编程", "设计", "考研", "考证", "驾校", "考试"],
            "icon": "📚"
        },
        "通讯服务": {
            "keywords": ["话费", "流量", "宽带", "通讯", "移动", "联通", "电信", "手机",
                        "充值", "缴费"],
            "icon": "📱"
        },
        "生活缴费": {
            "keywords": ["电费", "水费", "燃气", "物业", "房租", "供暖", "有线电视"],
            "icon": "🏠"
        },
        "金融服务": {
            "keywords": ["保险", "理财", "基金", "股票", "证券", "银行", "贷款", "信用卡"],
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

def fetch_bills_from_pop3(user_email, auth_code, pop3_server):
    """从POP3服务器获取账单"""
    bills = []
    
    try:
        # 连接POP3服务器
        if pop3_server == "pop.qq.com":
            port = 995
        elif pop3_server == "pop.163.com":
            port = 995
        elif pop3_server == "pop.gmail.com":
            port = 995
        elif pop3_server == "outlook.office365.com":
            port = 995
        else:
            port = 995
        
        print(f"正在连接POP3服务器 {pop3_server}:{port}...")
        mail = poplib.POP3_SSL(pop3_server, port)
        
        print(f"正在登录邮箱: {user_email}")
        try:
            mail.user(user_email)
            mail.pass_(auth_code)
            print("POP3登录成功")
        except Exception as e:
            error_msg = str(e)
            if "USER" in error_msg or "PASS" in error_msg:
                raise Exception(f"POP3登录失败，请检查邮箱和授权码是否正确。错误: {e}")
            raise Exception(f"POP3登录失败: {e}")
        
        # 获取邮件数量
        try:
            num_messages = len(mail.list()[1])
            print(f"邮箱中共有 {num_messages} 封邮件")
        except Exception as e:
            print(f"获取邮件数量失败: {e}")
            num_messages = 0
        
        # 获取最近的邮件（最多200封）
        recent_count = min(num_messages, 200)
        print(f"正在获取最近的 {recent_count} 封邮件...")
        
        for i in range(num_messages - recent_count + 1, num_messages + 1):
            try:
                # 获取邮件
                response, lines, octets = mail.retr(i)
                
                # 调试：检查lines的类型
                if lines:
                    print(f"邮件 {i}: lines[0]类型 = {type(lines[0])}")
                
                # 尝试解析邮件，先尝试字节，再尝试字符串
                try:
                    msg_content = b'\r\n'.join(lines)
                    msg = email.message_from_bytes(msg_content)
                except Exception as e:
                    print(f"邮件 {i} 使用message_from_bytes失败: {e}")
                    try:
                        msg_content = '\r\n'.join(lines)
                        msg = email.message_from_string(msg_content)
                    except Exception as e2:
                        print(f"邮件 {i} 使用message_from_string也失败: {e2}")
                        continue
                
                # 检查是否是平安银行邮件
                from_header = decode_email_header(msg.get('From', ''))
                subject_header = decode_email_header(msg.get('Subject', ''))
                
                if 'pingan' in from_header.lower() or '平安' in from_header.lower() or \
                   '账单' in subject_header or '消费' in subject_header:
                    print(f"找到平安银行邮件: {subject_header}")
                    
                    # 解析账单
                    email_bills = parse_bill_from_email(msg)
                    bills.extend(email_bills)
            except Exception as e:
                print(f"解析邮件 {i} 失败: {e}")
                continue
        
        mail.quit()
        
        # 去重：基于日期、商家和金额的组合
        if bills:
            print(f"去重前共有 {len(bills)} 条账单记录")
            unique_bills = []
            seen = set()
            
            for bill in bills:
                # 创建唯一键：日期 + 商家 + 金额
                key = f"{bill['date']}_{bill['merchant']}_{bill['amount']}"
                if key not in seen:
                    seen.add(key)
                    unique_bills.append(bill)
                else:
                    print(f"  ⚠️ 发现重复账单: {bill['date']} | {bill['merchant']} | ¥{bill['amount']}")
            
            bills = unique_bills
            print(f"去重后共有 {len(bills)} 条唯一账单记录")
        
        if not bills:
            print("未找到账单数据，返回空列表")
        
        return bills
        
    except Exception as e:
        print(f"POP3连接失败: {e}")
        raise

def fetch_bills_from_imap(user_email, auth_code, imap_server):
    """从IMAP服务器获取账单"""
    bills = []
    
    try:
        # 连接IMAP服务器
        if imap_server == "imap.qq.com":
            port = 993
        elif imap_server == "imap.163.com":
            port = 993
        elif imap_server == "imap.gmail.com":
            port = 993
        elif imap_server == "outlook.office365.com":
            port = 993
        else:
            port = 993
        
        print(f"正在连接 {imap_server}:{port}...")
        mail = imaplib.IMAP4_SSL(imap_server, port)
        
        print(f"正在登录邮箱: {user_email}")
        try:
            mail.login(user_email, auth_code)
            print("登录成功")
        except Exception as e:
            error_msg = str(e)
            if "LOGIN" in error_msg or "password" in error_msg:
                raise Exception(f"登录失败，请检查邮箱和授权码是否正确。163邮箱必须使用授权码，不能使用邮箱密码。错误: {e}")
            raise Exception(f"登录失败: {e}")
        
        # 选择收件箱
        try:
            print("正在选择收件箱...")
            
            # 163邮箱特殊处理：尝试不同的INBOX访问方式
            if "163.com" in user_email:
                print("检测到163邮箱，尝试多种INBOX访问方式...")
                
                # 方法1：直接使用INBOX
                try:
                    print("方法1: 尝试直接选择INBOX")
                    status, msg_count = mail.select("INBOX")
                    if status == "OK":
                        print(f"✅ 方法1成功！收件箱选择成功，共有 {msg_count[0]} 封邮件")
                    else:
                        raise Exception(f"方法1失败，状态码: {status}")
                except Exception as e:
                    print(f"方法1失败: {e}")
                    
                    # 方法2：使用INBOX（小写）
                    try:
                        print("方法2: 尝试选择inbox（小写）")
                        status, msg_count = mail.select("inbox")
                        if status == "OK":
                            print(f"✅ 方法2成功！收件箱选择成功，共有 {msg_count[0]} 封邮件")
                        else:
                            raise Exception(f"方法2失败，状态码: {status}")
                    except Exception as e2:
                        print(f"方法2失败: {e2}")
                        
                        # 方法3：使用UTF-7编码的INBOX
                        try:
                            print("方法3: 尝试使用UTF-7编码")
                            # INBOX的UTF-7编码
                            inbox_utf7 = "INBOX"
                            status, msg_count = mail.select(inbox_utf7)
                            if status == "OK":
                                print(f"✅ 方法3成功！收件箱选择成功，共有 {msg_count[0]} 封邮件")
                            else:
                                raise Exception(f"方法3失败，状态码: {status}")
                        except Exception as e3:
                            print(f"方法3失败: {e3}")
                            
                            # 方法4：列出邮箱并尝试选择第一个
                            try:
                                print("方法4: 列出所有邮箱并尝试选择")
                                status, mailboxes = mail.list()
                                if status == "OK":
                                    for i, mailbox in enumerate(mailboxes):
                                        mailbox_str = mailbox.decode()
                                        print(f"  邮箱{i}: {mailbox_str}")
                                        
                                        # 尝试选择每个邮箱
                                        try:
                                            if '"' in mailbox_str:
                                                parts = mailbox_str.split('"')
                                                mailbox_name = parts[-2] if len(parts) > 2 else "INBOX"
                                            else:
                                                mailbox_name = "INBOX"
                                            
                                            status, msg_count = mail.select(mailbox_name)
                                            if status == "OK":
                                                print(f"✅ 方法4成功！成功选择邮箱: {mailbox_name}，共有 {msg_count[0]} 封邮件")
                                                break
                                        except:
                                            continue
                                    else:
                                        raise Exception("无法选择任何邮箱")
                            except Exception as e4:
                                raise Exception(f"所有方法都失败了: {e4}")
            else:
                # 其他邮箱使用标准方式
                status, msg_count = mail.select("INBOX")
                if status != "OK":
                    raise Exception(f"选择收件箱失败，状态码: {status}")
                print(f"收件箱选择成功，共有 {msg_count[0]} 封邮件")
            
        except Exception as e:
            raise Exception(f"选择收件箱失败: {e}")
        
        print("正在搜索平安银行邮件...")
        
        # 搜索平安银行邮件
        search_criteria = [
            '(FROM "pingan")',
            '(FROM "平安")',
            '(SUBJECT "账单")',
            '(SUBJECT "消费")',
        ]
        
        for criteria in search_criteria:
            try:
                status, messages = mail.search(None, criteria)
                if status == "OK" and messages[0]:
                    email_ids = messages[0].split()
                    print(f"找到 {len(email_ids)} 封邮件")
                    
                    # 获取最近的邮件（最多100封）
                    for email_id in email_ids[-100:]:
                        try:
                            status, msg_data = mail.fetch(email_id, "(RFC822)")
                            if status == "OK":
                                raw_email = msg_data[0][1]
                                msg = email.message_from_bytes(raw_email)
                                
                                # 解析账单
                                email_bills = parse_bill_from_email(msg)
                                bills.extend(email_bills)
                        except Exception as e:
                            print(f"解析邮件 {email_id} 失败: {e}")
                            continue
                    break
            except Exception as e:
                print(f"搜索失败: {e}")
                continue
        
        try:
            mail.close()
        except:
            pass
        try:
            mail.logout()
        except:
            pass
        
        # 去重：基于日期、商家和金额的组合
        if bills:
            print(f"去重前共有 {len(bills)} 条账单记录")
            unique_bills = []
            seen = set()
            
            for bill in bills:
                # 创建唯一键：日期 + 商家 + 金额
                key = f"{bill['date']}_{bill['merchant']}_{bill['amount']}"
                if key not in seen:
                    seen.add(key)
                    unique_bills.append(bill)
                else:
                    print(f"  ⚠️ 发现重复账单: {bill['date']} | {bill['merchant']} | ¥{bill['amount']}")
            
            bills = unique_bills
            print(f"去重后共有 {len(bills)} 条唯一账单记录")
        
        if not bills:
            print("未找到账单数据，返回空列表")
        
        return bills
        
    except Exception as e:
        print(f"IMAP连接失败: {e}")
        raise

@app.route('/api/fetch-bills', methods=['POST'])
def fetch_bills():
    """获取账单数据"""
    data = request.json
    user_email = data.get('email', '')
    auth_code = data.get('authCode', '')
    imap_server = data.get('imapServer', 'imap.qq.com')
    use_pop3 = data.get('usePop3', False)
    
    if not user_email or not auth_code:
        return jsonify({
            "success": False,
            "message": "邮箱或授权码不能为空"
        }), 400
    
    try:
        print(f"收到请求: {user_email}, IMAP服务器: {imap_server}, 使用POP3: {use_pop3}")
        
        # 根据用户选择使用POP3或IMAP
        if use_pop3:
            # 使用POP3协议
            pop3_server = imap_server.replace('imap.', 'pop.')
            print(f"使用POP3协议: {pop3_server}")
            bills = fetch_bills_from_pop3(user_email, auth_code, pop3_server)
        else:
            # 使用IMAP协议
            print(f"使用IMAP协议: {imap_server}")
            bills = fetch_bills_from_imap(user_email, auth_code, imap_server)
        
        if not bills:
            return jsonify({
                "success": False,
                "message": "未找到账单数据，请检查邮箱中是否有平安银行账单邮件"
            }), 404
        
        return jsonify({
            "success": True,
            "message": f"获取账单成功，共 {len(bills)} 条记录",
            "data": bills
        })
        
    except Exception as e:
        print(f"获取账单失败: {e}")
        return jsonify({
            "success": False,
            "message": f"获取账单失败: {str(e)}"
        }), 500

@app.route('/api/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    })

# Vercel部署需要导出app对象
# 本地开发时运行以下代码
if __name__ == '__main__':
    print("🚀 平安银行账单分析系统后端启动")
    print("📍 API服务: http://localhost:8080")
    print("📊 前端页面: 在浏览器打开 frontend/index.html")
    print("📧 支持邮箱: QQ邮箱、163邮箱、Gmail、Outlook")
    app.run(host='0.0.0.0', port=8080, debug=True)