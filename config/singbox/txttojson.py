import json
import argparse
import re

def extract_domains(input_file):
    raw_domains = []
    
    # 尝试直接作为完整 JSON 解析
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
            data = json.loads(content)
            # 遍历规则寻找域名列表
            if isinstance(data, dict) and "rules" in data:
                for rule in data["rules"]:
                    for key in ["domain", "domain_suffix", "domain_keyword"]:
                        if key in rule:
                            raw_domains.extend(rule[key])
                if raw_domains:
                    print(f"检测到标准 JSON 格式，提取出 {len(raw_domains)} 条规则")
                    return raw_domains
    except Exception:
        # 解析 JSON 失败则进入流式正则匹配模式
        pass

    # 正则表达式说明：
    # 1. (?:\|\||")? : 匹配可选的 || 或 引号开头
    # 2. ([a-zA-Z0-9\-\.]+) : 捕获域名主体
    # 3. (?:\^|")? : 匹配可选的 ^ 或 引号结尾
    pattern = re.compile(r'(?:\|\||")?([a-zA-Z0-9\-\.]+)(?:\^|")?')

    print(f"正在以流式正则模式解析: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # 跳过空行和元数据注释行
            if not line or line[0] in ('!', '#', '[', '{', '}', ']'):
                continue
            
            match = pattern.search(line)
            if match:
                domain = match.group(1).lower()
                # 进一步检查提取出的是否是合法域名格式（防止误读 metadata 里的域名）
                if "." in domain:
                    raw_domains.append(domain)
    
    return raw_domains

def main():
    parser = argparse.ArgumentParser(description="Sing-box 规则全能转换器 (支持混合/JSON/ABP)")
    parser.add_argument("-i", "--input", required=True, help="输入文件")
    parser.add_argument("-o", "--output", required=True, help="输出 json 文件")
    args = parser.parse_args()

    # 1. 提取
    all_extracted = extract_domains(args.input)
    total_raw = len(all_extracted)

    # 2. 去重并排序
    unique_domains = sorted(list(set(all_extracted)))
    duplicate_count = total_raw - len(unique_domains)

    # 3. 构建 sing-box 配置
    result = {
        "version": 2,
        "rules": [
            {
                "domain_suffix": unique_domains
            }
        ]
    }

    # 4. 写入
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print("-" * 35)
    print(f"处理完成：")
    print(f"· 总计识别条数: {total_raw}")
    print(f"· 过滤重复条数: {duplicate_count}")
    print(f"· 最终唯一域名: {len(unique_domains)}")
    print(f"· 结果已保存至: {args.output}")
    print("-" * 35)

if __name__ == "__main__":
    main()