#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试完整对比功能"""

import sys
import os

# 添加 src 到路径
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from core.doc_comparator import DocumentComparator

# 测试文件（使用桌面上的文件）
file_x = "/Users/yuclaw/Desktop/信息技术服务协议（数字证书预存）-广东铭鸿数据有限公司.docx"
file_y = "/Users/yuclaw/Desktop/信息技术服务协议（数字证书预存）-广东铭鸿数据有限公司 2.docx"

print(f"原文档：{file_x}")
print(f"修改文档：{file_y}")
print()

# 检查文件是否存在
if not os.path.exists(file_x):
    print(f"❌ 原文档不存在：{file_x}")
    sys.exit(1)
if not os.path.exists(file_y):
    print(f"❌ 修改文档不存在：{file_y}")
    sys.exit(1)

print("✅ 文件存在，开始对比...")
print()

try:
    comparator = DocumentComparator()
    
    # 加载文档
    print("1. 加载文档...")
    comparator.load_documents(file_x, file_y)
    print(f"   文档 X: {len(comparator.paragraphs_x)} 段落")
    print(f"   文档 Y: {len(comparator.paragraphs_y)} 段落")
    
    # 分析结构
    print("2. 分析结构...")
    comparator.analyze_structure()
    
    # 对比内容
    print("3. 对比内容...")
    comparator.compare_content()
    print(f"   发现 {len(comparator.changes)} 处改动")
    
    # 生成输出
    print("4. 生成输出文档...")
    save_path = os.path.expanduser("~/Documents")
    output_options = {
        'detail_list': True,
        'report': True,
        'save_path': save_path
    }
    
    result_file = comparator.generate_output(output_options)
    print(f"   ✅ 结果文档：{result_file}")
    print(f"   ✅ 文件大小：{os.path.getsize(result_file)} bytes")
    
    # 检查 Excel 报告
    import glob
    excel_files = glob.glob(os.path.join(save_path, "合同对比报告_*.xlsx"))
    if excel_files:
        excel_file = max(excel_files, key=os.path.getctime)
        print(f"   ✅ Excel 报告：{excel_file}")
        print(f"   ✅ 文件大小：{os.path.getsize(excel_file)} bytes")
    
    print()
    print("🎉 对比完成！")
    
except Exception as e:
    print(f"\n❌ 对比失败：{e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
