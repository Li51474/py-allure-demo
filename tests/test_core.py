import pytest, allure               # ① 新增 allure
import pandas as pd
from utils.config_helper import get_var, save_var, extract_by_json
import requests, json, urllib.parse
from pathlib import Path

# tests/test_core.py
df = EXCEL_PATH = Path(__file__).with_name("CRM.xlsx")

df = pd.read_excel("CRM.xlsx", sheet_name="CS")
df.columns = df.columns.str.strip()
df = df.loc[:, ~df.columns.duplicated()]
COL = {"编号": "id", "描述": "desc", "请求url": "url", "请求方式": "method", "请求头": "headers",
       "请求体": "body", "Json参数": "json", "URL参数": "params", "提取变量": "extract", "使用变量": "use"}
df = df.rename(columns=COL)
cases = df.fillna("").to_dict("records")

@pytest.mark.parametrize("case", cases, ids=[c["id"] for c in cases])
def test_api(case):
    # ② 用 allure 动态标题与描述
    allure.dynamic.title(case["id"])
    allure.dynamic.description(case.get("desc", ""))

    url   = case["url"].strip()
    method= case["method"].upper()

    headers = json.loads(case["headers"]) if case["headers"] else {}
    for var in filter(None, map(str.strip, str(case["use"]).split(","))):
        headers[var] = get_var(var)

    params     = dict(urllib.parse.parse_qsl(case["body"])) if case["body"] else None
    json_data  = json.loads(case["json"])   if case["json"] else None
    url_params = json.loads(case["params"]) if case["params"] else {}
    if url_params:
        url += "?" + urllib.parse.urlencode(url_params)

    kwargs = {"headers": headers}
    kwargs["json" if json_data else "data"] = json_data or params or {}

    # ③ 用 allure 记录请求-响应
    with allure.step(f"【{method}】{url}"):
        allure.attach(json.dumps(kwargs, ensure_ascii=False, indent=2),
                      name="request", attachment_type=allure.attachment_type.JSON)
        resp = requests.request(method, url, **kwargs)
        allure.attach(resp.text, name="response",
                      attachment_type=allure.attachment_type.JSON)
    print("status_code =", resp.status_code)
    assert resp.status_code == 200, f"接口失败: {case['id']}"

    if case["extract"]:
        value = extract_by_json(resp.text, f"$.{case['extract']}")
        save_var(case["extract"], value)
        allure.attach(str(value), name="extracted", 
                      attachment_type=allure.attachment_type.TEXT)


# test_core.py
# …（前面所有代码）

# if __name__ == "__main__":
#     import os
#     import subprocess
#     import webbrowser
#     import sys

#     # 1. 让 Python 能找到 utils
#     root = os.path.dirname(os.path.abspath(__file__))
#     sys.path.insert(0, root)

#     # 2. 生成 Allure 原始数据
#     cmd = [
#         sys.executable, "-m", "pytest",
#         __file__,               # 当前脚本
#         "-sv",                  # 详细输出
#         "--maxfail=0",          # 不中断
#         "--alluredir", "allure-results"
#     ]
#     subprocess.run(cmd, cwd=root)

#     # 3. 生成 HTML 报告
#     subprocess.run(["allure", "generate", "allure-results",
#                     "--clean", "-o", "allure-report"], cwd=root)

#     # 4. 自动打开浏览器
#     report = os.path.join(root, "allure-report", "index.html")
#     webbrowser.open("file://" + report)
