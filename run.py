import requests
import execjs
from lxml import html
import re

# 1. 初始化会话 & 读取本地JS文件
session = requests.Session()
with open("./RsRunDo.js", "r", encoding="utf-8") as f:
    js_code = f.read()

# 2. 配置请求头
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Pragma": "no-cache",
    "Referer": "https://www.xxxxx.com/search-ng/queryResource/index",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    "sec-ch-ua": "\"Chromium\";v=\"140\", \"Not=A?Brand\";v=\"24\", \"Google Chrome\";v=\"140\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"macOS\""
}

# 3. 首次请求：获取页面HTML
url = "https://www.xxxxxx.com/search-ng/queryResource/index"

response = session.get(url, headers=headers)
print("首次请求状态码:", response.status_code)

if response.status_code not in [200, 202]:
    print(f"请求失败，状态码: {response.status_code}，响应内容: {response.text[:200]}")
    exit()

# 4. 使用lxml和XPath解析HTML，提取关键信息
tree = html.fromstring(response.text)

# 4.1 提取带r="m"的meta标签content属性
meta_content = tree.xpath('//meta[@r="m"]/@content')
content_to_replace = meta_content[0] if meta_content else None
print("Meta标签content值:", content_to_replace[:50] + "..." if content_to_replace else "未找到meta标签")

# 4.2 提取所有type="text/javascript"且r="m"的script标签内容
script_contents = tree.xpath('//script[@type="text/javascript"][@r="m"]/text()')

# 4.3 提取带charset、src且r="m"的script标签的src路径
js_src_paths = tree.xpath('//script[@type="text/javascript"][@charset="utf-8"][@r="m"][@src]/@src')
js_src_path = js_src_paths[0].lstrip('/') if js_src_paths else None
remote_js_url = f"https://www.ouyeel.com/{js_src_path}" if js_src_path else None

# 5. 输出提取的基础信息，验证是否正确获取
print("\n----- 提取结果验证 -----")
print("1. Meta标签content值:", content_to_replace[:50] + "..." if content_to_replace else "未找到meta标签")
print("2. 符合条件的script标签数量:", len(script_contents))
if script_contents:
    print("   第1个script内容（前100字符）:", script_contents[0][:100] + "...")
print("3. 远程JS完整URL:", remote_js_url if remote_js_url else "未找到目标script标签")

# 6. 关键替换逻辑：处理3个占位符
print("\n----- 替换JS代码 -----")

# 6.1 替换"content_code_here"
has_placeholder = "content_code_here" in js_code
print(f"原始JS中是否包含content_code_here: {has_placeholder}")
if not has_placeholder:
    print("警告：原始JS文件中未找到content_code_here占位符，请检查文件名和内容")

if content_to_replace and has_placeholder:
    modified_js = re.sub(r'content_code_here', content_to_replace, js_code)
    replacement_count = modified_js.count(content_to_replace) - js_code.count(content_to_replace)
    if replacement_count > 0:
        print(f"成功替换content_code_here，替换次数: {replacement_count}")
        js_code = modified_js
        print("✅ 1.已请求远程JS并替换content_code_here")

# 6.2 替换"RsTs_js_here"
if script_contents:
    js_code = js_code.replace("'RsTs_js_here'", script_contents[0])
    print("✅ 2.已替换'RsTs_js_here'为第1个script内容")
else:
    print("\n❌ 未找到任何符合条件的script内容，无法替换'RsTs_js_here'")
    exit()

# 6.3 请求远程JS文件，替换"RsExecEnv_js_here"
if remote_js_url:
    remote_js_response = session.get(remote_js_url, headers=headers)
    if remote_js_response.status_code == 200:
        remote_js_content = remote_js_response.text
        js_code = js_code.replace("'RsExecEnv_js_here'", remote_js_content)
        print("✅ 3.已请求远程JS并替换'RsExecEnv_js_here'")
    else:
        print(f"\n❌ 请求远程JS失败，状态码: {remote_js_response.status_code}")
        exit()
else:
    print("\n❌ 未找到远程JS的src路径，无法替换'RsExecEnv_js_here'")
    exit()

# 7. 保存替换后的完整JS代码
with open("./Replaced_RsRunDo.js", "w", encoding="utf-8") as f:
    f.write(js_code)
print("\n✅ 替换后的JS已保存到 Replaced_RsRunDo.js")

# 8. 使用execjs执行替换后的JS

def cookie_to_dict(cookie_string):
    cookie_dict = {}
    # 按分号分割
    items = cookie_string.split(';')
    for item in items:
        item = item.strip()  # 去除空格
        if '=' in item:
            key, value = item.split('=', 1)  # 分割键值对
            cookie_dict[key] = value
    return cookie_dict
try:
    ctx = execjs.compile(js_code)
    print("✅ JS环境编译成功，可后续调用JS中的函数（如ctx.call('函数名', 参数)）")
    
    # 调用JS中的getCookie函数
    cookie = ctx.call("getCookie")
    # print("\n✅从JS中获取的Cookie:", cookie)
    # 将Cookie字符串转换为字典（输出所有键值对）
    cookie_dict = cookie_to_dict(cookie)
    print("\n📋 完整Cookie字典:", cookie_dict)
    # 提取key包含'T0'的键值对
    filtered_cookies = {k: v for k, v in cookie_dict.items() if 'T0' in k}
    print("\n🔍 包含'T0'的Cookie:", filtered_cookies)


except Exception as e:
    print(f"\n❌ JS执行失败，错误信息: {str(e)[:300]}")


# 测试接口是否正常，返回状态码是不是200
# res = session.get(url=url, headers=headers, params=params, cookies=filtered_cookies)
# print("请求状态码:", res.status_code)
# # res.encoding = 'utf-8'
# print("响应内容:", res.text)


# 跑数据,记得把params去掉，post请求不校验params，只对data有数据要求

# params = {
#     "K5nOZLud": "cp3V0alqEtiHonWU.uxrfhGRNcEI_9FdOi7UR69wmeylOaIsE1RxEHoGz_BX4Sm8QCr8Rgvlo5h0wGh6OCpX7wdSwfZU5SNG"
# }
headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://www.oxxxxx.com",
    "Pragma": "no-cache",
    "Referer": "https://www.oxxxxx.com/steel/search?pageIndex=0&pageSize=50",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    "sec-ch-ua": "\"Chromium\";v=\"140\", \"Not=A?Brand\";v=\"24\", \"Google Chrome\";v=\"140\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"macOS\""
}
data = {
    "criteriaJson": "{\"pageSize\":50,\"industryComponent\":null,\"channel\":null,\"productType\":null,\"sort\":null,\"warehouseCode\":null,\"key_search\":null,\"is_central\":null,\"searchField\":null,\"companyCode\":null,\"inquiryCategory\":null,\"inquirySpec\":null,\"provider\":null,\"shopCode\":null,\"packCodes\":null,\"steelFactory\":null,\"resourceIds\":null,\"providerCode\":null,\"jsonParam\":{\"keywordAnalyseResult\":null},\"excludeShowSoldOut\":null,\"pageIndex\":1,\"maxPage\":50}"
}
res_value = session.post("https://www.xxxxx.com/search-ng/commoditySearch/queryCommodityResult", 
                         headers=headers, 
                         cookies=filtered_cookies, 
                         data=data)

print(res_value.text)
print(res_value)
print(filtered_cookies)