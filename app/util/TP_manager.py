import json
import os
import re
import zipfile


def unzip_file(zip_path, extract_path):
    if not os.path.exists(zip_path):
        print(f"错误: 文件 '{zip_path}' 不存在。")
        return

    if not zipfile.is_zipfile(zip_path):
        print(f"错误: '{zip_path}' 不是一个有效的ZIP文件。")
        return

    # 确保解压路径存在，如果不存在则创建
    os.makedirs(extract_path, exist_ok=True)

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
    except Exception as e:
        print(f"解压过程中出错: {str(e)}")


def handle_TP_lists(file_path, output_dir):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # 定义需要加双引号的键名
    keys_to_quote = r'\b(id|filename|name|x|y|z)\b'
    pattern = rf'({keys_to_quote})\s*:'

    def replacer(match):
        return f'"{match.group(1)}":'

    # 查找指定的键并替换
    updated_content = re.sub(pattern, replacer, content)

    list_pattern = re.compile(r'static\s+(\w+)\s*=\s*(\[[\s\S]*?\]);')
    lists = list_pattern.findall(updated_content)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for list_name, list_content in lists:
        if list_name == "CustomTpList":
            continue

        list_content = re.sub(r',\s*}', '}', list_content)
        list_content = re.sub(r',\s*]', ']', list_content)

        try:
            list_data = json.loads(list_content)  # 将字符串解析为JSON对象
            list_file_path = os.path.join(output_dir, f'{list_name}.json')
            with open(list_file_path, 'w', encoding='utf-8') as list_file:
                json.dump(list_data, list_file, ensure_ascii=False, indent=4)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON for {list_name}: {e}")


def load_json_files(input_dir):
    json_files = {}
    for file_name in os.listdir(input_dir):
        if file_name.endswith('.json'):
            list_name = os.path.splitext(file_name)[0]
            with open(os.path.join(input_dir, file_name), 'r', encoding='utf-8') as file:
                json_files[list_name] = json.load(file)
    return json_files


def combine_to_js(json_files, selected_files, output_js_path):
    # 添加开头内容
    combined_js_content = '''"use strict";
Object.defineProperty(exports, "__esModule", { value: !0 }),
  (exports.ModTpFile = void 0);
const puerts_1 = require("puerts"),
  UE = require("ue"),
  Info_1 = require("../../../Core/Common/Info"),
  Log_1 = require("../../../Core/Common/Log"),
  ModManager_1 = require("../ModManager"),
  ModCustomTp_1 = require("./ModCustomTp");

class ModTpFile {
'''

    # 合成所有列表到一个大列表
    all_in_one_list = []
    current_id = 1  # 用于重新分配唯一的ID

    for file_path in selected_files:
        list_name = os.path.splitext(os.path.basename(file_path))[0]
        if list_name in json_files:
            list_content = json_files[list_name]
            for item in list_content:
                item_copy = item.copy()
                item_copy['id'] = current_id  # 更新ID值
                item_copy['filename'] = 'all_in_one'  # 更新filename
                current_id += 1
                all_in_one_list.append(item_copy)
        else:
            print(f"Warning: {list_name}.json not found in the specified directory.")

    # 对 all_in_one 列表进行排序（假设按照 id 排序）
    all_in_one_list = sorted(all_in_one_list, key=lambda x: x['id'])

    # 自定义JSON格式化函数，确保缩进格式正确
    def format_json(data):
        return json.dumps(data, ensure_ascii=False, indent=4).replace('\n', '\n    ')

    # 添加 all_in_one 列表作为第一个静态属性
    combined_js_content += f'    static all_in_one = {format_json(all_in_one_list)};\n'

    # 添加其他静态属性
    for file_path in selected_files:
        list_name = os.path.splitext(os.path.basename(file_path))[0]
        if list_name in json_files:
            list_content = format_json(json_files[list_name])
            combined_js_content += f'    static {list_name} = {list_content};\n'

    # 获取所有列表名，包括 all_in_one
    all_lists = ",\n    ".join(
        ['this.all_in_one'] + [f'this.{os.path.splitext(os.path.basename(file_path))[0]}' for file_path in selected_files])

    # 添加结尾内容
    combined_js_content += f'''
  static CustomTpList = [
    {all_lists}
  ];
}}
exports.ModTpFile = ModTpFile;
'''

    with open(output_js_path, 'w', encoding='utf-8') as js_file:
        js_file.write(combined_js_content)
