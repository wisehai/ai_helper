#!/usr/bin/env python3  
import sys  
import os  
import requests  
import json  
import argparse  

# 配置API密钥和URL  
API_KEY = os.environ.get("AI_API_KEY", "")  
# 选择DeepSeek或OpenAI API  
API_URL = "https://api.siliconflow.cn/v1/chat/completions"  # 或OpenAI的URL  

def chat(prompt):  
    """与AI聊天"""  
    data = {  
        "model": "THUDM/GLM-4-9B-0414",  # 或者gpt-3.5-turbo等  
        "messages": [{"role": "user", "content": prompt}],  
        "temperature": 0.7  
    }  
    
    headers = {  
        "Content-Type": "application/json",  
        "Authorization": f"Bearer {API_KEY}"  
    }  
    
    response = requests.post(API_URL, headers=headers, json=data)  
    if response.status_code == 200:  
        return response.json()["choices"][0]["message"]["content"]  
    else:  
        return f"错误: {response.status_code}, {response.text}"  

def translate(text):  
    """翻译文本"""  
    prompt = f"请翻译以下文本: {text}"  
    return chat(prompt)  

def main():  
    parser = argparse.ArgumentParser(description="终端AI助手")  
    parser.add_argument("command", choices=["chat", "dic"], help="选择功能: chat(聊天)或dic(翻译)")  
    parser.add_argument("prompt", nargs="*", help="要处理的文本")  
    
    args = parser.parse_args()  
    
    if not API_KEY:  
        print("错误: 未设置API密钥。请设置环境变量AI_API_KEY。")  
        sys.exit(1)  
    
    # 检查是否通过管道输入  
    if not sys.stdin.isatty():  
        # 从管道读取输入  
        prompt_text = sys.stdin.read().strip()  
    else:  
        # 从命令行参数读取输入  
        if not args.prompt:  
            print("错误: 请提供输入文本")  
            sys.exit(1)  
        prompt_text = " ".join(args.prompt)  
    
    if args.command == "chat":  
        print(chat(prompt_text))  
    elif args.command == "dic":  
        print(translate(prompt_text))  

if __name__ == "__main__":  
    main()
