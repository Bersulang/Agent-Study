"""模拟模型只用于测试接口形状，不代表真实智能。"""
class MockModel:
    def complete(self, messages):
        # 模拟响应明确标记；usage是固定教学数据，不是tokenizer结果。
        question = messages[-1]["content"]
        return {"text": f"[模拟回答]请核查制度来源：{question}",
                "usage": {"input_tokens": 20, "output_tokens": 10}}

def estimated_cost(usage, input_per_million, output_per_million):
    # 教学费率由调用者提供，不能当成当前供应商价格。
    return (usage["input_tokens"] * input_per_million +
            usage["output_tokens"] * output_per_million) / 1_000_000

if __name__ == "__main__":
    model = MockModel()
    messages = [{"role": "system", "content": "只依据已给制度回答"},
                {"role": "user", "content": "如何申请VPN？"}]
    result = model.complete(messages)
    print(result["text"])
    print(f"模拟usage：{result['usage']}")
    print(f"教学费率估算：{estimated_cost(result['usage'], 1, 2):.6f}")
