import json
from typing import Dict, List, Optional

class SimpleDatabase:
    def __init__(self):
        self.tables: Dict[str, List[Dict]] = {}

        self.title_maxnum = 10
        self.content_maxnum = 100
        self.create_table("所有的诗",["ID","标题","内容"])

        # 读取文件内容并构建字符到位置的映射字典
        with open("all_char.txt", 'r', encoding='utf-8') as f:
            self.char_to_pos = {char: pos for pos, char in enumerate(f.read())}
        
        self.pos_to_char = {pos: char for char, pos in self.char_to_pos.items()}
        
        self.char_num = len(self.char_to_pos)
        
        self.all_str_cnt = [0, self.char_num]
        for str_len in range(2, self.content_maxnum + 1):
            ans = pow(self.char_num, str_len)
            self.all_str_cnt.append(ans + self.all_str_cnt[str_len-1])
        
    def create_table(self, table_name: str, columns: List[str]):
        if table_name not in self.tables:
            self.tables[table_name] = []
            print(f"表 '{table_name}' 成功创建，列内容: {columns}")
        else:
            print(f"表 '{table_name}' 已经存在了")
    
    def get_char_positions(self, input_str):
        # 获取每个字符的位置
        return [self.char_to_pos.get(char, -1) for char in input_str]
    
    def str_to_id(self, input_str):
        pos = self.get_char_positions(input_str)
        ans = 0
        for i,value in enumerate(pos):
            ans += pow(self.char_num, i) * value
        return ans + self.all_str_cnt[len(pos)-1]
    
    def id_to_str(self, id:int):
        length = 1
        while id >= self.all_str_cnt[length]:
            length += 1
        
        id -= self.all_str_cnt[length - 1]
        
        pos = []
        for i in range(length):
            char_pos = id % self.char_num
            pos.append(char_pos)
            id = id // self.char_num
        
        ans = ""
        for p in pos:
            ans += self.pos_to_char[p]

        return ans

    def all_poem_cnt(self):
        return self.all_str_cnt[self.title_maxnum] * self.all_str_cnt[self.content_maxnum]
    
    def id_to_poem(self, id: int)->tuple[str,str]:
        title_id = id // self.all_str_cnt[self.content_maxnum]
        content_id = id % self.all_str_cnt[self.content_maxnum]
        return self.id_to_str(title_id), self.id_to_str(content_id)
    
    def poem_to_id(self, title:str, content:str):
        title_id = self.str_to_id(title)
        content_id = self.str_to_id(content)
        return title_id * self.all_str_cnt[self.content_maxnum] + content_id

    def query_data(
        self, 
        table_name: str, 
        max_rows: int = 10,
        filters: Optional[Dict[str, str]] = None
    ) -> Dict:
        if table_name not in self.tables:
            return {"error": f"表 '{table_name}' 不存在"}
        
        title = "一"
        content = "一"

        have_text = False

        if "title" in filters:
            title = filters["title"]
            if len(title) > self.title_maxnum:
                return {"error": f"标题至多{self.title_maxnum}字"}
            if -1 in self.get_char_positions(title):
                return {"error": f"标题存在非法字符"}
            have_text = True
        if "content" in filters:
            content = filters["content"]
            if len(content) > self.content_maxnum:
                return {"error": f"内容至多{self.content_maxnum}字"}
            if -1 in self.get_char_positions(content):
                return {"error": f"内容存在非法字符"}
            have_text = True

        parsed_id = self.poem_to_id(title, content)

        if "id" in filters:
            id = int(filters["id"])
            if id < 0 or id >= self.all_poem_cnt():
                return {"error": "不存在符合查询的数据"}
            if have_text and parsed_id != id:
                return {"error": "不存在符合查询的数据"}
            parsed_id = id
        elif not have_text:
            return {"error": "空的筛选条件"}
        
        return {
            "page": parsed_id // max_rows + 1,
            "row": parsed_id % max_rows
        }

    
    def get_page(
        self, 
        table_name: str, 
        page: int, 
        max_rows: int = 10,
        filters: Optional[Dict[str, str]] = None
    ) -> Dict:
        if table_name not in self.tables:
            return {"error": f"表 '{table_name}' 不存在"}
        
        start_id = (page - 1) * max_rows
        end_id = start_id + max_rows

        data = []
        for i in range(start_id, end_id):
            title, content = self.id_to_poem(i)
            data.append({"ID":i, "标题":title, "内容":content})
        
        total_rows = self.all_poem_cnt()
        pages = (total_rows // max_rows) + (1 if total_rows % max_rows else 0)

        if page < 1 or page > pages:
            return {"error": f"不合法的页号。页号范围: 1-{pages}"}

        return {
            "data": data,
            "total_rows": total_rows,
            "page": page,
            "total_pages": pages
        }

    

# 示例用法
if __name__ == "__main__":
    db = SimpleDatabase()
    print(db.all_poem_cnt())
    