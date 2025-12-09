# manage_qrcodes.py - 修复版
import os
import django
import qrcode
from PIL import Image
import sys

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wechat_survey.settings')
django.setup()

from survey.models import Survey, QRCode
import random
import string
import uuid

def list_surveys():
    """列出所有问卷"""
    surveys = Survey.objects.all()
    print("\n=== 现有问卷列表 ===")
    for i, survey in enumerate(surveys, 1):
        print(f"{i}. ID: {survey.id}")
        print(f"   标题: {survey.title}")
        print(f"   创建者: {survey.created_by}")
        print(f"   创建时间: {survey.created_at}")
        print(f"   回答数: {survey.responses.count()}")
        print()

def generate_qrcode_for_survey(survey_id=None, name="微信问卷二维码"):
    """为问卷生成二维码"""
    if survey_id is None:
        # 交互式选择问卷
        list_surveys()
        try:
            choice = int(input("请输入要生成二维码的问卷编号: "))
            surveys = list(Survey.objects.all())
            if 1 <= choice <= len(surveys):
                survey = surveys[choice - 1]
            else:
                print("无效的选择")
                return
        except ValueError:
            print("请输入数字")
            return
    else:
        # 通过ID查找问卷
        try:
            survey = Survey.objects.get(id=survey_id)
        except Survey.DoesNotExist:
            print(f"找不到ID为 {survey_id} 的问卷")
            return
        except ValueError:
            print("ID格式错误，请使用有效的UUID格式")
            print("例如: 123e4567-e89b-12d3-a456-426614174000")
            return
    
    # 生成短代码
    short_code = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    
    # 创建QRCode记录
    qrcode_obj = QRCode.objects.create(
        survey=survey,
        name=name,
        short_code=short_code
    )
    
    print("\n✓ 二维码创建成功:")
    print(f"   名称: {name}")
    print(f"   短代码: {short_code}")
    print(f"   对应问卷: {survey.title}")
    print(f"   问卷ID: {survey.id}")
    print(f"   扫描次数: {qrcode_obj.scan_count}")
    print(f"   创建时间: {qrcode_obj.created_at}")
    
    return qrcode_obj

def export_qrcode_image(qrcode_obj, save_path=None):
    """导出二维码图片"""
    from django.conf import settings
    
    # 生成访问URL（根据你的实际域名修改）
    # 本地开发用
    if settings.DEBUG:
        domain = "http://127.0.0.1:8000"
    else:
        domain = "https://yourdomain.com"  # 生产环境替换为你的域名
    
    redirect_url = f"{domain}/qrcode/{qrcode_obj.short_code}/redirect/"
    
    # 创建二维码
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(redirect_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # 保存图片
    if save_path is None:
        save_path = f"qrcode_{qrcode_obj.short_code}_{qrcode_obj.survey.title[:20]}.png"
    
    img.save(save_path)
    print(f"✓ 二维码图片已保存到: {save_path}")
    print(f"   访问链接: {redirect_url}")
    
    return img, save_path

def main():
    """主函数"""
    print("=== 微信问卷二维码生成器 ===")
    
    while True:
        print("\n请选择操作:")
        print("1. 查看所有问卷")
        print("2. 生成新的二维码")
        print("3. 列出所有二维码")
        print("4. 导出二维码图片")
        print("5. 退出")
        
        choice = input("请输入选项 (1-5): ").strip()
        
        if choice == '1':
            list_surveys()
        
        elif choice == '2':
            # 询问二维码名称
            name = input("请输入二维码名称（默认: 微信问卷二维码）: ").strip()
            if not name:
                name = "微信问卷二维码"
            
            # 询问是否指定问卷ID
            use_id = input("是否指定问卷ID? (y/N): ").strip().lower()
            if use_id == 'y':
                survey_id = input("请输入问卷UUID: ").strip()
                try:
                    # 验证UUID格式
                    uuid.UUID(survey_id)
                    qrcode_obj = generate_qrcode_for_survey(survey_id, name)
                except ValueError:
                    print("错误: 无效的UUID格式")
            else:
                qrcode_obj = generate_qrcode_for_survey(None, name)
            
            if qrcode_obj:
                # 询问是否立即导出图片
                export_now = input("是否立即导出二维码图片? (Y/n): ").strip().lower()
                if export_now != 'n':
                    export_qrcode_image(qrcode_obj)
        
        elif choice == '3':
            qrcodes = QRCode.objects.all().select_related('survey')
            print("\n=== 现有二维码列表 ===")
            for i, qr in enumerate(qrcodes, 1):
                print(f"{i}. 名称: {qr.name}")
                print(f"   短代码: {qr.short_code}")
                print(f"   问卷: {qr.survey.title}")
                print(f"   扫描次数: {qr.scan_count}")
                print(f"   创建时间: {qr.created_at}")
                print()
        
        elif choice == '4':
            qrcodes = list(QRCode.objects.all().select_related('survey'))
            if not qrcodes:
                print("没有可导出的二维码")
                continue
            
            print("\n=== 选择要导出的二维码 ===")
            for i, qr in enumerate(qrcodes, 1):
                print(f"{i}. {qr.name} - {qr.survey.title}")
            
            try:
                choice = int(input("请输入二维码编号: "))
                if 1 <= choice <= len(qrcodes):
                    qrcode_obj = qrcodes[choice - 1]
                    filename = input(f"请输入保存文件名（默认: qrcode_{qrcode_obj.short_code}.png）: ").strip()
                    if not filename:
                        filename = None
                    export_qrcode_image(qrcode_obj, filename)
                else:
                    print("无效的选择")
            except ValueError:
                print("请输入数字")
        
        elif choice == '5':
            print("再见！")
            break
        
        else:
            print("无效的选项，请重新输入")

def generate_test_qrcode():
    """生成测试二维码"""
    # 使用刚创建的问卷ID
    survey_id = "1e6100a7-3071-4610-a0d3-708a3c226e28"
    qrcode_obj = generate_qrcode_for_survey(survey_id, "测试二维码")
    if qrcode_obj:
        export_qrcode_image(qrcode_obj)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # 非交互式生成测试二维码
        generate_test_qrcode()
    else:
        try:
            main()
        except KeyboardInterrupt:
            print("\n程序被用户中断")
        except Exception as e:
            print(f"发生错误: {e}")
            import traceback
            traceback.print_exc()