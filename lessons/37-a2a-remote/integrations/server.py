"""官方a2a-sdk 0.3.26服务：规范0.3、JSON-RPC、真实Task与Artifact。"""
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.apps import A2AStarletteApplication
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore, TaskUpdater
from a2a.types import AgentCapabilities, AgentCard, AgentSkill, Part, TextPart, TaskState
from a2a.utils import new_task

class TicketExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        # SDK生成task/context id并管理协议消息；业务只关心输入与产物。
        task = context.current_task or new_task(context.message)
        if context.current_task is None:
            await event_queue.enqueue_event(task)
        updater = TaskUpdater(event_queue, task.id, task.context_id)
        text = context.get_user_input()
        if text == 'wait':
            # 进入等待用户补充状态，客户端可用tasks/cancel取消。
            await updater.update_status(TaskState.input_required, final=True)
            return
        await updater.update_status(TaskState.working)
        if text != 'T-7':
            await updater.update_status(TaskState.failed, final=True)
            return
        await updater.add_artifact([Part(root=TextPart(text='T-7: open'))], name='ticket-status')
        await updater.complete()

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        # DefaultRequestHandler先检查task存在与可取消状态。
        task = context.current_task
        updater = TaskUpdater(event_queue, task.id, task.context_id)
        await updater.cancel()

skill = AgentSkill(id='ticket-status', name='工单状态', description='查询固定教学工单T-7', tags=['ticket'], examples=['T-7'])
card = AgentCard(name='工单Agent', description='真实A2A协议，本地固定业务数据',
                 url='http://127.0.0.1:9999/', version='1.0.0',
                 default_input_modes=['text'], default_output_modes=['text'],
                 capabilities=AgentCapabilities(streaming=False), skills=[skill])
handler = DefaultRequestHandler(agent_executor=TicketExecutor(), task_store=InMemoryTaskStore())
app = A2AStarletteApplication(agent_card=card, http_handler=handler).build()

if __name__ == '__main__':
    import uvicorn
    # 未实现生产身份认证，只监听loopback；不可直接对外部署。
    uvicorn.run(app, host='127.0.0.1', port=9999)
