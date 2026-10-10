"""阶段30—43服务、状态和集成边界行为检查。"""
from .foundation import _load_student, _load_example, _case, _raises


def _function(lesson_dir, name):
    """每次检查单独加载练习，避免学生模块状态泄漏到下一案例。"""
    module = _load_student(lesson_dir)
    function = getattr(module, name, None)
    if not callable(function):
        raise AssertionError(f"请在exercises/practice.py实现{name}(...)练习接口")
    return function


def build_service_cases(stage, lesson_dir):
    """返回30—43每阶段至少三个有行为结果的断言。"""
    cases = []
    if stage == 30:
        def mixed_roles():
            result = _function(lesson_dir, "batch_route")(["政策", "", "工单"], {"knowledge", "ticket"})
            assert len(result["routes"]) == 3 and result["routes"][1]["role"] == "human", "空请求转人工，且每个输入均有路由"
            assert sum(result["counts"].values()) == 3, "角色统计应覆盖整个批次"
        def unknown_role_fallback():
            result = _function(lesson_dir, "batch_route")(["政策"], {"ticket"})
            assert result["routes"][0]["role"] == "human", "未获许可的路由应转人工"
        def input_unchanged():
            requests = ["政策", "工单"]
            before = requests.copy()
            _function(lesson_dir, "batch_route")(requests, {"knowledge", "ticket"})
            assert requests == before, "批量路由不得改写调用方列表"
        cases += [_case("按职责路由并统计请求", mixed_roles), _case("未授权职责路由转人工", unknown_role_fallback), _case("路由过程保留原始请求", input_unchanged)]
    elif stage == 31:
        tasks = [{"id": "plan", "required": True}, {"id": "audit", "required": False}]
        def required_missing_blocks():
            result = _function(lesson_dir, "summarize_required")(tasks, {})
            assert result["status"] == "blocked" and "plan" in result["missing"], "缺少必需任务应阻止完成"
        def optional_missing_warns():
            result = _function(lesson_dir, "summarize_required")(tasks, {"plan": "ok"})
            assert result["status"] == "completed" and "audit" in result["warnings"], "可选任务缺失只产生警告"
        def duplicate_id_is_one_task():
            result = _function(lesson_dir, "summarize_required")([tasks[0], tasks[0]], {"plan": "ok"})
            assert result["status"] == "completed" and result["missing"] == [], "重复task id代表同一逻辑任务"
        cases += [_case("缺少必需子任务阻止完成", required_missing_blocks), _case("缺少可选子任务只告警", optional_missing_warns), _case("重复任务编号按同一任务处理", duplicate_id_is_one_task)]
    elif stage == 32:
        def reader_needs_question():
            result = _function(lesson_dir, "safe_handoff")("owner", "reader", {"question": ""}, [])
            assert result["status"] == "needs_clarification", "reader缺少问题时应追问"
        def ticket_needs_id():
            result = _function(lesson_dir, "safe_handoff")("owner", "ticket", {"title": "申请"}, [])
            assert result["status"] == "needs_clarification", "ticket接收者缺少ticket_id时应追问"
        def handoff_does_not_mutate_facts():
            facts = {"question": "查询报销", "extra": "保留"}
            before = facts.copy()
            result = _function(lesson_dir, "safe_handoff")("owner", "reader", facts, [])
            assert facts == before and result["status"] == "transferred", "交接成功且输入事实不变"
        cases += [_case("reader接收者需要问题字段", reader_needs_question), _case("ticket接收者需要工单编号", ticket_needs_id), _case("交接不修改原始事实", handoff_does_not_mutate_facts)]
    elif stage == 33:
        def missing_blocks():
            result = _function(lesson_dir, "dependency_summary")(None, "ticket")
            assert result["status"] == "blocked" and "knowledge" in result["missing"], "必需知识缺失时不能汇总"
        def both_ready_summarize():
            result = _function(lesson_dir, "dependency_summary")("policy", "ticket")
            assert result["status"] == "completed" and result["summary"], "依赖都成功时才生成摘要"
        def empty_differs_from_timeout():
            result = _function(lesson_dir, "dependency_summary")("", "ticket")
            assert result["status"] == "blocked" and "knowledge" in result["empty"], "合法空结果应单独标注而不是误报超时"
        cases += [_case("必需依赖缺失时阻止汇总", missing_blocks), _case("依赖齐全后生成摘要", both_ready_summarize), _case("正常空结果区别于超时", empty_differs_from_timeout)]
    elif stage == 34:
        def atomic_merge():
            state = {"version": 2, "status": "new", "owner": "A"}
            result = _function(lesson_dir, "merge_many")(state, [{"status": "blocked"}, {"status": "ready"}], 2)
            assert result == {"version": 3, "status": "ready", "owner": "A"}, "一批合法补丁只增加一次版本"
        def bad_patch_rejected():
            state = {"version": 2, "status": "new"}
            before = state.copy()
            _raises(lambda: _function(lesson_dir, "merge_many")(state, [{"status": "ready"}, {"version": -1}], 2), "非法补丁必须拒绝")
            assert state == before, "失败后原始状态完全不变"
        def stale_version_rejected():
            _raises(lambda: _function(lesson_dir, "merge_many")({"version": 2}, [{"status": "ready"}], 1), "过期版本不能合并")
        cases += [_case("批量合并只增加一次版本", atomic_merge), _case("非法补丁原子失败", bad_patch_rejected), _case("过期版本拒绝合并", stale_version_rejected)]
    elif stage == 35:
        evidence = [{"active": True, "authority": 1, "value": "旧"}, {"active": True, "authority": 3, "value": "新"}, {"active": False, "authority": 9, "value": "撤销"}]
        def highest_active_wins():
            result = _function(lesson_dir, "choose_evidence")(evidence)
            assert result["status"] == "selected" and result["value"] == "新", "应忽略撤销项并按权威级别选择"
        def equal_authority_conflicts():
            result = _function(lesson_dir, "choose_evidence")([{"active": True, "authority": 2, "value": "A"}, {"active": True, "authority": 2, "value": "B"}])
            assert result["status"] == "conflict", "最高权威证据值冲突时需显式冲突"
        def no_active_evidence():
            result = _function(lesson_dir, "choose_evidence")([{"active": False, "authority": 3, "value": "old"}])
            assert result["status"] == "no_evidence", "只有撤销证据时不能给答案"
        cases += [_case("选择最高权威的有效证据", highest_active_wins), _case("最高等级证据冲突时报告冲突", equal_authority_conflicts), _case("仅有撤销证据时不回答", no_active_evidence)]
    elif stage == 36:
        def even_distribution():
            result = _function(lesson_dir, "allocate_budget")(8, ["a", "b", "c"])
            assert result == {"a": 3, "b": 3, "c": 2}, "预算均分，余数按输入顺序分配"
        def zero_tasks_zero_budget():
            assert _function(lesson_dir, "allocate_budget")(0, []) == {}, "零预算空任务集有效"
        def positive_budget_without_tasks_rejected():
            _raises(lambda: _function(lesson_dir, "allocate_budget")(1, []), "正预算无任务接收者应拒绝")
        cases += [_case("预算均分且余数按顺序分配", even_distribution), _case("零预算允许空任务列表", zero_tasks_zero_budget), _case("正预算没有任务时拒绝", positive_budget_without_tasks_rejected)]
    elif stage == 37:
        def cancels_active_task():
            registry = _load_registry(lesson_dir)
            registry.submit("t1", "工单")
            registry.tasks["t1"]["artifact"] = "keep"
            result = _function(lesson_dir, "cancel_terminal")(registry, "t1")
            assert result["status"] == "canceled" and registry.get("t1")["artifact"] == "keep", "取消活动任务但保留已有产物"
        def completed_not_cancelable():
            registry = _load_registry(lesson_dir)
            registry.submit("t1", "工单"); registry.finish("t1")
            result = _function(lesson_dir, "cancel_terminal")(registry, "t1")
            assert result["status"] == "not_cancelable", "终态任務不能取消"
        def unknown_task():
            result = _function(lesson_dir, "cancel_terminal")(_load_registry(lesson_dir), "missing")
            assert result["status"] == "not_found", "未知任务返回not_found"
        cases += [_case("取消活动任务保留产物", cancels_active_task), _case("已完成任务不可取消", completed_not_cancelable), _case("未知任务返回未找到", unknown_task)]
    elif stage == 38:
        reports = [{"name": "cheap-low-quality", "quality": .7, "p95_ms": 100, "latency_budget_ms": 500, "cost": 1}, {"name": "fast-expensive", "quality": .95, "p95_ms": 800, "latency_budget_ms": 500, "cost": 5}, {"name": "best", "quality": .92, "p95_ms": 300, "latency_budget_ms": 500, "cost": 3}]
        def quality_latency_then_cost():
            result = _function(lesson_dir, "choose_architecture")(reports, .9)
            assert result == "best", "先满足质量与延迟约束，再按成本选择"
        def no_eligible_architecture():
            result = _function(lesson_dir, "choose_architecture")(reports, .99)
            assert result == "none", "没有满足质量门槛的架构应返回none"
        def order_independent():
            result = _function(lesson_dir, "choose_architecture")(list(reversed(reports)), .9)
            assert result == "best", "报告输入顺序不能决定结果"
        cases += [_case("满足质量延迟门槛后选最低成本", quality_latency_then_cost), _case("无方案达标时不选架构", no_eligible_architecture), _case("架构选择不依赖输入顺序", order_independent)]
    elif stage == 39:
        def event_cursor_and_session():
            service = _load_service(lesson_dir)
            task_id = service.create("s1", "查询工单")
            service.advance(task_id)
            result = _function(lesson_dir, "replay_events")(service, task_id, "s1", 1)
            assert [event["seq"] for event in result] == [2, 3], "after表示最后已见序号，只返回其后事件"
        def session_isolation():
            service = _load_service(lesson_dir)
            task_id = service.create("s1", "查询工单")
            _raises(lambda: _function(lesson_dir, "replay_events")(service, task_id, "s2", 0), "错误会话不能读取事件", (PermissionError,))
        def negative_cursor_rejected():
            _raises(lambda: _function(lesson_dir, "replay_events")({}, "t1", "s1", -1), "负游标应在读取前拒绝")
        cases += [_case("事件续读只返回游标之后", event_cursor_and_session), _case("拒绝跨会话读取事件", session_isolation), _case("负事件游标拒绝", negative_cursor_rejected)]
    elif stage == 40:
        def map_auth_and_retryable():
            classify = _function(lesson_dir, "classify_http_error")
            assert classify(401) == "authentication" and classify(403) == "authorization" and classify(429) == "retryable_read"
        def not_found_distinct():
            assert _function(lesson_dir, "classify_http_error")(404) == "not_found", "404应单独分类"
        def other_error_permanent():
            assert _function(lesson_dir, "classify_http_error")(400) == "permanent", "未知写错误不能自动重试"
        cases += [_case("区分认证授权和限流错误", map_auth_and_retryable), _case("404映射为资源不存在", not_found_distinct), _case("不可重试HTTP错误分类", other_error_permanent)]
    elif stage == 41:
        def _rows():
            from tempfile import TemporaryDirectory
            module = _load_student(lesson_dir)
            demo = _load_example(lesson_dir)
            function = getattr(module, "list_recoverable", None)
            if not callable(function):
                raise AssertionError("请实现list_recoverable(store)")
            with TemporaryDirectory() as folder:
                store = demo.Store(demo.Path(folder) / "exercise.db")
                try:
                    store.create("T-1")
                    store.create("T-2")
                    store.save("T-2", "completed", 0)
                    return function(store)
                finally:
                    store.close()
        def recoverable_states_only():
            rows = _rows()
            assert {row["state"] for row in rows} <= {"new", "ready"}, "恢复列表只含new与ready"
            assert all({"id", "state", "version"} <= row.keys() for row in rows), "恢复行应提供最小状态契约"
        def no_completed_rows():
            rows = _rows()
            assert all(row["state"] != "completed" for row in rows), "已完成任务不能作为待恢复任务"
        def stable_read_across_reopen():
            rows = _rows()
            second = _rows()
            assert [{key: row[key] for key in ("id", "state", "version")} for row in rows] == [{key: row[key] for key in ("id", "state", "version")} for row in second], "恢复业务字段应稳定，诊断时间等附加字段可变化"
        cases += [_case("仅列出可恢复任务", recoverable_states_only), _case("恢复列表排除已完成任务", no_completed_rows), _case("重连后恢复结果保持一致", stable_read_across_reopen)]
    elif stage == 42:
        def active_lease_renewed():
            from tempfile import TemporaryDirectory
            module = _load_student(lesson_dir)
            demo = _load_example(lesson_dir)
            with TemporaryDirectory() as folder:
                queue = demo.Queue(demo.Path(folder) / "exercise.db")
                try:
                    queue.enqueue("j1")
                    token = queue.claim("j1", "w1", 5)
                    assert module.renew(queue, "j1", "w1", token, 6, 10) is True, "当前worker在到期前可续租"
                finally:
                    queue.close()
        def expired_lease_rejected():
            from tempfile import TemporaryDirectory
            module = _load_student(lesson_dir)
            demo = _load_example(lesson_dir)
            with TemporaryDirectory() as folder:
                queue = demo.Queue(demo.Path(folder) / "exercise.db")
                try:
                    queue.enqueue("j1")
                    token = queue.claim("j1", "w1", 5)
                    assert module.renew(queue, "j1", "w1", token, 15, 10) is False, "到期租约不得续租"
                finally:
                    queue.close()
        def stale_owner_token_rejected():
            from tempfile import TemporaryDirectory
            module = _load_student(lesson_dir)
            demo = _load_example(lesson_dir)
            with TemporaryDirectory() as folder:
                queue = demo.Queue(demo.Path(folder) / "exercise.db")
                try:
                    queue.enqueue("j1")
                    old_token = queue.claim("j1", "w1", 5)
                    queue.claim("j1", "w2", 16)
                    assert module.renew(queue, "j1", "w1", old_token, 17, 10) is False, "旧owner/token不能续租新worker任务"
                finally:
                    queue.close()
        cases += [_case("当前worker可在到期前续租", active_lease_renewed), _case("过期租约禁止续租", expired_lease_rejected), _case("接管后的旧token失效", stale_owner_token_rejected)]
    elif stage == 43:
        def unknown_does_not_execute():
            from tempfile import TemporaryDirectory
            module = _load_student(lesson_dir)
            demo = _load_example(lesson_dir)
            with TemporaryDirectory() as folder:
                ledger = demo.Ledger(demo.Path(folder) / "exercise.db")
                try:
                    result = module.query_operation(ledger, "k1", {"kind": "close", "ticket_id": "T-1"})
                    assert result["status"] == "unknown"
                    assert ledger.db.execute("SELECT COUNT(*) FROM effects").fetchone()[0] == 0, "查询未知操作不能执行副作用"
                finally:
                    ledger.close()
        def same_digest_replays_record():
            from tempfile import TemporaryDirectory
            module = _load_student(lesson_dir)
            demo = _load_example(lesson_dir)
            with TemporaryDirectory() as folder:
                ledger = demo.Ledger(demo.Path(folder) / "exercise.db")
                try:
                    action = {"kind": "close", "ticket_id": "T-1"}
                    ledger.approve("a1", action, 200)
                    ledger.execute("k1", "a1", action, 100)
                    result = module.query_operation(ledger, "k1", action)
                    assert result["status"] == "completed" and result["result"] == "closed:T-1", "相同请求返回原结果"
                finally:
                    ledger.close()
        def digest_conflict():
            from tempfile import TemporaryDirectory
            module = _load_student(lesson_dir)
            demo = _load_example(lesson_dir)
            with TemporaryDirectory() as folder:
                ledger = demo.Ledger(demo.Path(folder) / "exercise.db")
                try:
                    action = {"kind": "close", "ticket_id": "T-1"}
                    ledger.approve("a1", action, 200)
                    ledger.execute("k1", "a1", action, 100)
                    result = module.query_operation(ledger, "k1", {"kind": "close", "ticket_id": "T-2"})
                finally:
                    ledger.close()
            assert result["status"] == "conflict", "相同key不同摘要必须冲突"
        cases += [_case("查询未知操作不触发副作用", unknown_does_not_execute), _case("幂等查询返回已存结果", same_digest_replays_record), _case("同键不同动作摘要冲突", digest_conflict)]
    return cases


def _load_registry(lesson_dir):
    return _load_example(lesson_dir).TaskRegistry()


def _load_service(lesson_dir):
    return _load_example(lesson_dir).TaskService()


def _case(name, check):
    return name, check
