import requests

# 测试问卷提交功能
survey_url = 'http://127.0.0.1:8000/survey/500b5de8-758a-4ead-a627-ec7b9c98df65/'
submit_url = 'http://127.0.0.1:8000/api/surveys/500b5de8-758a-4ead-a627-ec7b9c98df65/submit/'

print(f"测试问卷提交功能")
print(f"问卷页面: {survey_url}")
print(f"提交URL: {submit_url}")

# 先获取CSRF令牌
response = requests.get(survey_url)
if response.status_code != 200:
    print(f"错误: 无法访问问卷页面，状态码: {response.status_code}")
    exit(1)

# 提取CSRF令牌
import re
csrf_token = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', response.text)
if not csrf_token:
    print("错误: 无法提取CSRF令牌")
    exit(1)
csrf_token = csrf_token.group(1)
print(f"✓ 成功获取CSRF令牌")

# 准备提交数据
data = {
    'csrfmiddlewaretoken': csrf_token,
    'survey': '500b5de8-758a-4ead-a627-ec7b9c98df65',
    'answers': {
        # 这里需要根据实际问题结构调整
        'question_1': '5',  # 评分题，假设问题ID为1
        'question_2': 'friend',  # 单选题，选择朋友推荐
        'question_3': ['design', 'quality']  # 多选题，选择产品设计和产品质量
    }
}

print(f"\n准备提交的数据:")
print(f"  问卷ID: {data['survey']}")
print(f"  答案: {data['answers']}")

# 提交问卷
response = requests.post(submit_url, data=data)
print(f"\n提交结果:")
print(f"  状态码: {response.status_code}")
print(f"  响应内容: {response.text}")

if response.status_code == 200:
    print("✓ 问卷提交成功！")
else:
    print("✗ 问卷提交失败")

print("\n测试完成！")
