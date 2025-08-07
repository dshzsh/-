# 定义中文字符的Unicode范围
chinese_ranges = [
    (0x4E00, 0x9FFF),    # 基本汉字
    (0x3400, 0x4DBF),    # 扩展A
    (0x20000, 0x2A6DF),  # 扩展B
    (0x2A700, 0x2B73F),  # 扩展C
    (0x2B740, 0x2B81F),  # 扩展D
    (0x2B820, 0x2CEAF),  # 扩展E
    (0x2CEB0, 0x2EBEF),  # 扩展F
    (0x3007, 0x3007),    # 〇
    (0x3000, 0x303F),    # 中文标点符号等
    (0xFF00, 0xFFEF),    # 全角ASCII、全角标点等
    (0x3300, 0x33FF),    # 中文兼容字符
    (0xFE30, 0xFE4F),    # 中文竖排标点
    (0xF900, 0xFAFF),    # CJK兼容汉字
    (0x31C0, 0x31EF),    # 中文笔画
    (0x2F00, 0x2FDF),    # 康熙部首
]

# 打开文件准备写入
with open('all_char.txt', 'w', encoding='utf-8') as f:
    # 遍历所有范围
    for start, end in chinese_ranges:        
        # 写入该范围内的所有字符
        for code in range(start, end + 1):
            try:
                char = chr(code)
                # 检查字符是否是有效的中文字符
                f.write(char)
                    
            except ValueError:
                pass  # 跳过无效的代码点