"""推导式筛选并映射；解包绑定固定数量的值。"""
tickets = [("T-1", 5), ("T-2", 2), ("T-3", 4)]
urgent_ids = [ticket_id for ticket_id, priority in tickets if priority >= 4]
first_id, first_priority = tickets[0]

if __name__ == "__main__":
    print(urgent_ids, first_id, first_priority)
