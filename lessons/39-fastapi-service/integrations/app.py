"""真实FastAPI应用：任务生命周期、有限SSE续读、本地交互页面。"""
import json
from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel, Field, field_validator
import importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location('lesson_domain', Path(__file__).resolve().parents[1] / 'examples' / 'demo.py')
domain = importlib.util.module_from_spec(spec)
spec.loader.exec_module(domain)
service = domain.TaskService()
app = FastAPI()

class CreateTask(BaseModel):
    # 类型注解供Pydantic读取；Field再限制字符串长度。
    session_id: str = Field(min_length=1, max_length=100)
    prompt: str = Field(min_length=1, max_length=2000)

    @field_validator('session_id', 'prompt')
    @classmethod
    def strip_nonblank(cls, value):
        if not value.strip():
            raise ValueError('不能只有空白')
        return value.strip()

def owned(task_id, session_id):
    task = service.tasks.get(task_id)
    # 本地session头只是隔离教具，生产必须从认证身份获取owner。
    if task is None or task['session'] != session_id:
        raise HTTPException(status_code=404, detail='task_not_found')
    return task

@app.post('/tasks', status_code=201)
def create(body: CreateTask):
    key = service.create(body.session_id, body.prompt)
    return {'task_id': key, **service.read(key)}

@app.get('/tasks/{task_id}')
def read(task_id: str, x_session_id: str = Header()):
    owned(task_id, x_session_id)
    return service.read(task_id)

@app.post('/tasks/{task_id}/advance')
def advance(task_id: str, x_session_id: str = Header()):
    owned(task_id, x_session_id)
    # 人工触发领域推进便于验证。可靠后台执行在42阶段实现。
    service.advance(task_id)
    return service.read(task_id)

@app.delete('/tasks/{task_id}')
def cancel(task_id: str, x_session_id: str = Header()):
    owned(task_id, x_session_id)
    try:
        service.cancel(task_id)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return service.read(task_id)

@app.get('/tasks/{task_id}/events')
def events(task_id: str, after: int = Query(default=0, ge=0), x_session_id: str = Header()):
    task = owned(task_id, x_session_id)
    snapshot = list(task['events'])
    def stream():
        for seq, event in enumerate(snapshot, start=1):
            if seq > after:
                # SSE每帧必须有空行；id用于客户端重连时记录游标。
                data = json.dumps({'seq': seq, 'type': event}, ensure_ascii=False)
                yield f'id: {seq}\nevent: {event}\ndata: {data}\n\n'
    return StreamingResponse(stream(), media_type='text/event-stream')

@app.get('/', response_class=HTMLResponse)
def page():
    # 教学页面只显示返回文本，用textContent避免解释模型内容为HTML。
    # 原始字符串保留JavaScript的反斜杠，防止Python把\\n提前变成真实换行。
    return r'''<!doctype html><html lang="zh"><meta charset="utf-8"><title>任务演示</title>
    <h1>工单助手任务接口</h1><p>本地教学：创建后推进或取消，再读取事件。</p>
    <input id="prompt" value="查询工单T-7"><button onclick="createTask()">创建</button>
    <button onclick="action('advance')">推进</button><button onclick="action('cancel')">取消</button>
    <button onclick="replay()">读取事件</button><pre id="out"></pre>
    <script>
    let taskId=''; const sid=crypto.randomUUID(); let after=0;
    const out=document.getElementById('out');
    async function show(r){out.textContent=await r.text();}
    async function createTask(){let r=await fetch('/tasks',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({session_id:sid,prompt:document.getElementById('prompt').value})});
    let body=await r.json(); if(r.ok){taskId=body.task_id;after=0;}out.textContent=JSON.stringify(body,null,2);}
    async function action(kind){if(!taskId)return;let url='/tasks/'+taskId+(kind==='advance'?'/advance':'');
    await show(await fetch(url,{method:kind==='advance'?'POST':'DELETE',headers:{'X-Session-Id':sid}}));}
    async function replay(){if(!taskId)return;let r=await fetch('/tasks/'+taskId+'/events?after='+after,{headers:{'X-Session-Id':sid}});
    let data=await r.text();out.textContent=data;for(let line of data.split('\n'))if(line.startsWith('id: '))after=Number(line.slice(4));}
    </script></html>'''

if __name__ == '__main__':
    import uvicorn
    # 只有显式执行集成文件才启动服务，默认demo不会占用端口。
    uvicorn.run(app, host='127.0.0.1', port=8000)
