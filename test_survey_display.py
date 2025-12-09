import requests

# 测试问卷页面是否能正确显示选项
survey_url = 'http://127.0.0.1:8000/survey/500b5de8-758a-4ead-a627-ec7b9c98df65/'

print(f"测试问卷页面: {survey_url}")

# 发送请求获取页面内容
response = requests.get(survey_url)
if response.status_code != 200:
    print(f"错误: 无法访问问卷页面，状态码: {response.status_code}")
    exit(1)

html = response.text

# 检查是否包含问题
print("\n1. 检查问题是否显示:")
if '您是通过什么渠道知道我们的？' in html:
    print("  ✓ 找到单选题")
else:
    print("  ✗ 未找到单选题")

if '您喜欢我们产品的哪些方面？（可多选）' in html:
    print("  ✓ 找到多选题")
else:
    print("  ✗ 未找到多选题")

# 检查是否包含选项
print("\n2. 检查选项是否显示:")
options = ['朋友推荐', '广告', '搜索引擎', '社交媒体', '其他']
for option in options:
    if option in html:
        print(f"  ✓ 找到选项: {option}")
    else:
        print(f"  ✗ 未找到选项: {option}")

# 检查选项数量
print("\n3. 检查选项数量:")
single_choice_options = html.count('radio-label')
multiple_choice_options = html.count('checkbox-label')
print(f"  ✓ 单选题选项数量: {single_choice_options}")
print(f"  ✓ 多选题选项数量: {multiple_choice_options}")

# 检查提交按钮
print("\n4. 检查其他元素:")
if '提交问卷' in html:
    print("  ✓ 找到提交按钮")
else:
    print("  ✗ 未找到提交按钮")

# 检查是否有表单元素
if '<form' in html:
    print("  ✓ 找到表单元素")
else:
    print("  ✗ 未找到表单元素")

print("\n测试完成！")
