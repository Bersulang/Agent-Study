"""yield逐条产出，消费一次后生成器就结束。"""


def urgent_tickets(tickets):
    for ticket in tickets:
        if ticket["priority"] >= 4:
            yield ticket


if __name__ == "__main__":
    tickets = [{"id": "T-1", "priority": 5}, {"id": "T-2", "priority": 2}]
    for ticket in urgent_tickets(tickets):
        print(ticket["id"])
