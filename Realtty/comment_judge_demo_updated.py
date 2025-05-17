import json
import re
from difflib import get_close_matches
import os

# 文本预处理函数（去除标点和空格，转小写）
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r"[^一-龥a-zA-Z0-9]", "", text)
    return text

# 在文件前部导入和加载表达归一数据
with open(os.path.join("wordbank", "expression_groups.json"), "r", encoding="utf-8") as f:
    expression_groups = json.load(f)

# 替换归一函数
def normalize_comment(comment):
    comment = comment.lower()
    for main, variants in expression_groups.items():
        for var in variants:
            if var in comment:
                return main  # 直接归一为中心表达
    comment = re.sub(r"[啊呀呢吧嘛哦哟]", "", comment)
    comment = re.sub(r"[我你他她它我们你们他们她们的]", "", comment)
    comment = re.sub(r"[了吧吗啦哈]", "", comment)
    return comment.strip()

# 匹配函数
def match_from_dict(comment, dictionary):
    normalized_comment = normalize_comment(comment)
    matched = []
    for phrase in dictionary:
        if phrase in normalized_comment:
            matched.append(dictionary[phrase])
        else:
            close = get_close_matches(phrase, [normalized_comment], n=1, cutoff=0.85)
            if close:
                matched.append(dictionary[phrase])
    return matched

# 分析函数
def analyze_comment(comment, dictionaries):
    comment = preprocess_text(comment)
    matches = []
    for d in dictionaries:
        matches += match_from_dict(comment, d)

    if not matches:
        return {
            "主观性": 0.0,
            "情绪强度": 0.0,
            "情绪": [],
            "结构标签": [],
            "匹配数量": 0
        }

    avg_subjectivity = sum([m["主观性"] for m in matches]) / len(matches)
    avg_emotion = sum([m["情绪强度"] for m in matches]) / len(matches)
    emotions = list({e for m in matches for e in m["情绪"]})
    tags = list({t for m in matches for t in m["结构标签"]})

    return {
        "主观性": round(avg_subjectivity, 2),
        "情绪强度": round(avg_emotion, 2),
        "情绪": emotions,
        "结构标签": tags,
        "匹配数量": len(matches)
    }

# 主程序
if __name__ == "__main__":
    # 加载所有主观词库模块
    dictionaries = []
    dict_folder = os.path.join("wordbank", "subjective_dicts")
    for filename in os.listdir(dict_folder):
        if filename.endswith(".json"):
            file_path = os.path.join(dict_folder, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                dictionaries.append(data)

    while True:
        comment = input("请输入评论（q退出）：\n>> ").strip()
        if comment.lower() == "q":
            break
        result = analyze_comment(comment, dictionaries)
        print("\n评分结果：")
        for k, v in result.items():
            print(f"{k}: {v}")
        print("-" * 40)