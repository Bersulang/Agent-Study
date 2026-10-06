"""真实Playwright操作本地页面，无外部网站、Cookie或业务副作用。"""
from playwright.sync_api import sync_playwright

# 本地夹具模拟表单；生产页面变化时要重新定位和验证后置条件。
HTML = """<html><body>
<label>工单标题<input aria-label="工单标题" /></label>
<button onclick="document.querySelector('#result').textContent='DEMO-T-001'">提交</button>
<div id="result" role="status"></div>
</body></html>"""

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    try:
        page = browser.new_page()
        page.set_default_timeout(3000)
        page.set_content(HTML)
        page.get_by_label("工单标题").fill("登录失败")
        # 此处仅操作预先授权的本地夹具；真实写入前必须审批。
        page.get_by_role("button", name="提交").click()
        result = page.get_by_role("status").inner_text()
        assert result == "DEMO-T-001", "点击成功仍需检查后置条件"
        print("真实浏览器后置条件：", result)
    finally:
        browser.close()
