#!/usr/bin/env python3  
import sys  
import os  
import requests  
import json  
import argparse  
import socket  
import time  

# 配置  
API_KEY = os.environ.get("AI_API_KEY", "")  
ONLINE_API_URL = "https://api.siliconflow.cn/v1/chat/completions"  # 或OpenAI API  
ONLINE_MODEL = "Qwen/QwQ-32B"
OLLAMA_URL = "http://localhost:11434/api/chat"  # Ollama本地API  
OLLAMA_MODEL = "gemma3:1b"  # 本地模型名称  

def check_internet_connection():  
    """验证真实的互联网连接性"""  
    # 尝试获取具体内容并验证  
    try:  
        response = requests.get("https://www.baidu.com", timeout=3)  
        # 确认是否得到了预期的网页内容  
        if response.status_code == 200 and "<html" in response.text.lower():  
            return True  
        return False  
    except Exception:  
        pass  
        
    return False

def chat_with_online_api(prompt):  
    """使用在线API聊天 - 流式输出版"""  
    data = {  
        "model": ONLINE_MODEL,  
        "messages": [{"role": "user", "content": prompt}],  
        "temperature": 0.7,  
        "stream": True  # 启用流式输出  
    }  
    
    headers = {  
        "Content-Type": "application/json",  
        "Authorization": f"Bearer {API_KEY}"  
    }  
    
    try:  
        # 启用流式响应  
        with requests.post(ONLINE_API_URL, headers=headers, json=data,   
                          stream=True, timeout=60) as response:  
            
            if response.status_code != 200:  
                return f"API错误: {response.status_code}, {response.text}"  
            
            # 收集完整响应以便返回  
            full_response = ""  
            
            # 处理SSE格式的流式响应  
            for line in response.iter_lines():  
                if not line:  
                    continue  
                    
                # 移除"data: "前缀并解析JSON  
                if line.startswith(b'data: '):  
                    json_str = line[6:].decode('utf-8')  
                    
                    # 跳过[DONE]消息  
                    if json_str.strip() == "[DONE]":  
                        break  
                        
                    try:  
                        chunk = json.loads(json_str)  
                        
                        # 提取内容(不同API可能有不同结构)  
                        if "choices" in chunk and len(chunk["choices"]) > 0:  
                            delta = chunk["choices"][0].get("delta", {})  
                            if "content" in delta:  
                                # 使用get()方法提供默认值，避免None值  
                                content = delta.get("content", "")  
                                if content:  # 确保content不为None或空字符串  
                                    print(content, end="", flush=True)  
                                    full_response += content

                        # 检查思考过程字段 (根据API调整)  
                        if "reasoning_content" in delta:  
                            thinking = delta.get("reasoning_content", "")  
                            if thinking:  
                                print(thinking, end="", flush=True) 
                    except json.JSONDecodeError:  
                        continue  
            
            # 结束时打印换行  
            print()  
            return full_response  
            
    except requests.exceptions.RequestException as e:  
        return f"在线API请求失败: {str(e)}"

def chat_with_ollama(prompt):  
    """使用本地Ollama模型聊天 - 支持流式输出"""  
    data = {  
        "model": OLLAMA_MODEL,  
        "messages": [{"role": "user", "content": prompt}],  
        "stream": True  # 启用流式输出  
    }  
    
    headers = {"Content-Type": "application/json"}  
    
    try:  
        # 使用stream=True参数启用requests的流式处理  
        with requests.post(OLLAMA_URL, headers=headers, json=data,   
                          stream=True, timeout=30) as response:  
            
            if response.status_code != 200:  
                return f"Ollama错误: {response.status_code}"  
                
            # 存储完整响应用于返回  
            full_response = ""  
            
            # 逐行处理流式响应  
            for line in response.iter_lines():  
                if line:  
                    try:  
                        # 解析每个JSON块  
                        chunk = json.loads(line)  
                        if "message" in chunk and "content" in chunk["message"]:  
                            content = chunk["message"]["content"]  
                            # 实时打印内容  
                            print(content, end="", flush=True)  
                            full_response += content  
                    except json.JSONDecodeError:  
                        continue  
            
            # 打印换行符  
            print()  
            return full_response  
            
    except requests.exceptions.RequestException as e:  
        return f"Ollama请求失败: {str(e)}"

def chat(prompt):  
    """智能选择在线或离线服务进行聊天"""  
    print("正在处理请求...", file=sys.stderr)  
    
    if check_internet_connection() and API_KEY:  
        print("使用在线API...", file=sys.stderr)  
        return chat_with_online_api(prompt)  
    else:  
        if not API_KEY and check_internet_connection():  
            print("API密钥未设置，使用本地Ollama...", file=sys.stderr)  
        else:  
            print("无法连接到互联网，使用本地Ollama...", file=sys.stderr)  
        return chat_with_ollama(prompt)  

def translate(text):  
    """翻译文本"""  
    prompt = f"请翻译以下文本: {text}"  
    return chat(prompt)  

def main():  
    parser = argparse.ArgumentParser(description="终端AI助手 (自动在线/离线)")  
    parser.add_argument("command", choices=["chat", "dic"], help="选择功能: chat(聊天)或dic(翻译)")  
    parser.add_argument("prompt", nargs="*", help="要处理的文本")  
    
    args = parser.parse_args()  
    
    
    # 检查是否通过管道输入  
    if not sys.stdin.isatty():  
        # 从管道读取输入  
        prompt_text = sys.stdin.read().strip()  
    else:  
        # 从命令行参数读取输入  
        if not args.prompt:  
            print("错误: 请提供输入文本或通过管道传入")  
            sys.exit(1)  
        prompt_text = " ".join(args.prompt)  
    
    if args.command == "chat":  
        print(chat(prompt_text))  
    elif args.command == "dic":  
        print(translate(prompt_text))  

if __name__ == "__main__":  
    main()
