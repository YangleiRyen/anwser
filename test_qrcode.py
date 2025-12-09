#!/usr/bin/env python3
"""
测试二维码功能是否正常工作
"""
import requests
import sys
import time

# 测试服务器URL
base_url = "http://127.0.0.1:8000"

print("开始测试二维码功能...")

# 1. 测试二维码图片生成
test_short_code = "test1234"
try:
    image_url = f"{base_url}/qrcode/{test_short_code}/image/"
    response = requests.get(image_url, timeout=5)
    if response.status_code == 200:
        print(f"✅ 二维码图片生成成功: {image_url}")
        print(f"   响应状态码: {response.status_code}")
        print(f"   内容类型: {response.headers.get('Content-Type')}")
    else:
        print(f"❌ 二维码图片生成失败: {image_url}")
        print(f"   响应状态码: {response.status_code}")
except Exception as e:
    print(f"❌ 测试二维码图片生成时出错: {str(e)}")

# 2. 测试带样式参数的二维码生成
try:
    styled_url = f"{base_url}/qrcode/{test_short_code}/image/?fill_color=0000ff&back_color=ffffff&error_correction=M&box_size=12&border=5"
    response = requests.get(styled_url, timeout=5)
    if response.status_code == 200:
        print(f"✅ 带样式参数的二维码生成成功: {styled_url}")
        print(f"   响应状态码: {response.status_code}")
        print(f"   内容类型: {response.headers.get('Content-Type')}")
    else:
        print(f"❌ 带样式参数的二维码生成失败: {styled_url}")
        print(f"   响应状态码: {response.status_code}")
except Exception as e:
    print(f"❌ 测试带样式参数的二维码生成时出错: {str(e)}")

# 3. 测试不同颜色组合
try:
    colors = [
        ("red", "#ff0000"),
        ("green", "#00ff00"),
        ("blue", "#0000ff"),
        ("yellow", "#ffff00")
    ]
    print("\n测试不同颜色组合:")
    for color_name, color_code in colors:
        color_url = f"{base_url}/qrcode/{test_short_code}/image/?fill_color={color_code[1:]}&back_color=ffffff"
        response = requests.get(color_url, timeout=5)
        if response.status_code == 200:
            print(f"✅ {color_name} 二维码生成成功")
        else:
            print(f"❌ {color_name} 二维码生成失败")
        time.sleep(0.5)  # 避免请求过快
except Exception as e:
    print(f"❌ 测试颜色组合时出错: {str(e)}")

print("\n测试完成！")