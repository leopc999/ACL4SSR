import re
import os
import sys


def split_list_file(input_file):
    # 构造输出文件名
    base_name = os.path.splitext(input_file)[0]
    domain_output_file = f"{base_name}_domain.txt"
    ipcidr_output_file = f"{base_name}_ipcidr.txt"
    classical_output_file = f"{base_name}_classical.txt"

    # 初始化结果存储
    domain_rules = []
    ip_rules = []
    classical_rules = []

    # 定义正则表达式匹配模式
    domain_suffix_pattern = r"^DOMAIN-SUFFIX,([^,]+)$"
    domain_pattern = r"^DOMAIN,([^,]+)$"
    ip_patterns = [
        r"^IP-CIDR,([^,]+)(,no-resolve)?$",
        r"^IP-CIDR6,([^,]+)(,no-resolve)?$"
    ]
    classical_patterns = [
        r"^DOMAIN-KEYWORD,([^,]+)$",
        r"^URL-REGEX,(.+)$"
    ]
    user_agent_pattern = r"^USER-AGENT,"

    # 读取和处理文件
    with open(input_file, "r", encoding="utf-8") as infile:
        for line in infile:
            line = line.strip()  # 去除首尾空白字符

            if line.startswith("#") or not line:  # 跳过注释和空行
                continue

            # 匹配 DOMAIN-SUFFIX 规则
            match = re.match(domain_suffix_pattern, line)
            if match:
                domain_rules.append(f"+.{match.group(1)}")  # 转换为 +.<domain>
                continue

            # 匹配 DOMAIN 规则
            match = re.match(domain_pattern, line)
            if match:
                domain_rules.append(match.group(1))  # 转换为 <domain>
                continue

            # 匹配 IP-CIDR 和 IP-CIDR6 规则
            matched = False
            for pattern in ip_patterns:
                match = re.match(pattern, line)
                if match:
                    ip_rules.append(match.group(1))  # 提取 IP 部分，去除 no-resolve
                    matched = True
                    break

            if matched:
                continue

            # 处理 URL-REGEX -> DOMAIN-REGEX，保存到 classical
            for pattern in classical_patterns:
                match = re.match(pattern, line)
                if match:
                    if "URL-REGEX" in line:
                        converted_rule = re.sub(r"^URL-REGEX,", "DOMAIN-REGEX,", line)
                        classical_rules.append(converted_rule)
                    else:
                        classical_rules.append(line)
                    matched = True
                    break

            if matched:
                continue

            # 过滤 USER-AGENT，其余规则保留到 classical
            if not re.match(user_agent_pattern, line):
                classical_rules.append(line)

    # 写入 DOMAIN 文件（如果有内容）
    if domain_rules:
        with open(domain_output_file, "w", encoding="utf-8") as domain_out:
            domain_out.write("\n".join(domain_rules))
        print(f"DOMAIN 规则已保存到: {domain_output_file}")

    # 写入 IPCIDR 文件（如果有内容）
    if ip_rules:
        with open(ipcidr_output_file, "w", encoding="utf-8") as ip_out:
            ip_out.write("\n".join(ip_rules))
        print(f"IPCIDR 规则已保存到: {ipcidr_output_file}")

    # 写入 CLASSICAL 文件（如果有内容）
    if classical_rules:
        with open(classical_output_file, "w", encoding="utf-8") as classical_out:
            classical_out.write("\n".join(classical_rules))
        print(f"CLASSICAL 规则已保存到: {classical_output_file}")


# 替换为你的文件名
input_file = sys.argv[1]
split_list_file(input_file)

