"""先读懂普通类和组合：仓库持有工单对象。"""


class Ticket:
    def __init__(self, ticket_id, priority):
        self.ticket_id = ticket_id
        self.priority = priority


class TicketRepository:
    def __init__(self, tickets):
        # 组合表示Repository使用Ticket；它不是Ticket的子类。
        self.tickets = list(tickets)

    def find(self, ticket_id):
        for ticket in self.tickets:
            if ticket.ticket_id == ticket_id:
                return ticket
        return None


if __name__ == "__main__":
    repository = TicketRepository([Ticket("T-1", 4)])
    print(repository.find("T-1").priority)
