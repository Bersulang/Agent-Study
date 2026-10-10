"""阶段44—56开放式项目中可独立自动检查的代码子集。"""
from .foundation import _load_student, _call_solve, _case, _raises


def build_advanced_cases(stage, lesson_dir):
    """用契约样例检查学生实现，不把设计说明或真实集成算作自动通过。"""
    cases = []
    if stage == 44:
        base = {"cases": [{"id": "a", "category": "normal", "expected": "answer"}, {"id": "b", "category": "incomplete", "expected": "clarify"}], "predictions": [{"id": "a", "action": "answer"}, {"id": "b", "action": "clarify"}], "threshold": 1.0}
        def complete_predictions():
            report = _call_solve(lesson_dir, base)
            assert report["success_rate"] == 1 and "incomplete" in report["by_category"], "不完整参数类别也进入评估分母"
        def missing_duplicate_rejected():
            for predictions in (base["predictions"][:-1], base["predictions"] + [base["predictions"][0]]):
                _raises(lambda predictions=predictions: _call_solve(lesson_dir, {**base, "predictions": predictions}), "缺失或重复预测必须拒绝")
        def security_failure_blocks_release():
            unsafe = {**base, "predictions": [{"id": "a", "action": "answer", "security_violation": True}, base["predictions"][1]], "threshold": 0.0}
            report = _call_solve(lesson_dir, unsafe)
            assert report["release"] is False, "总体通过率达标仍不能掩盖安全失败"
        cases += [_case("不完整输入类别纳入评估分母", complete_predictions), _case("缺失或重复预测拒绝", missing_duplicate_rejected), _case("安全违规阻止发布", security_failure_blocks_release)]
    elif stage == 45:
        def revoked_approval_blocks_write():
            result = _call_solve(lesson_dir, {"events": ["approved", "revoked", "write"], "finished": False})
            assert result["allowed_writes"] == 0 and result["violations"], "审批撤销后不能写入"
        def read_only_allowed():
            result = _call_solve(lesson_dir, {"events": ["read"], "finished": False})
            assert result["allowed_reads"] == 1 and result["allowed_writes"] == 0, "只读轨迹无需写审批"
        def finished_trace_terminal():
            result = _call_solve(lesson_dir, {"events": ["finished", "write"], "finished": True})
            assert result["allowed_writes"] == 0, "任务结束后不得继续写入"
        cases += [_case("撤销审批阻止写操作", revoked_approval_blocks_write), _case("合法只读轨迹允许", read_only_allowed), _case("任务结束后拒绝新写入", finished_trace_terminal)]
    elif stage == 46:
        def trace_has_safe_error_and_request_id():
            result = _call_solve(lesson_dir, {"request_id": "req-1", "error": {"type": "TimeoutError", "body": "secret body"}, "input_tokens": 10, "output_tokens": 5})
            assert result["request_id"] == "req-1" and result["error_type"] == "TimeoutError", "轨迹需关联请求并记录错误类型"
            assert "secret body" not in str(result), "轨迹不能包含敏感错误正文"
        def nonnegative_cost():
            result = _call_solve(lesson_dir, {"request_id": "r", "input_tokens": 10, "output_tokens": 5})
            assert result["cost"] >= 0, "成本不可为负"
        def invalid_tokens_rejected():
            _raises(lambda: _call_solve(lesson_dir, {"request_id": "r", "input_tokens": -1, "output_tokens": 0}), "负token计数必须拒绝")
        cases += [_case("轨迹关联请求并脱敏错误", trace_has_safe_error_and_request_id), _case("轨迹成本保持非负", nonnegative_cost), _case("负token数拒绝", invalid_tokens_rejected)]
    elif stage == 47:
        def allow_safe_local_files():
            result = _call_solve(lesson_dir, {"kind": "file", "path": "reports/summary.md", "workspace": "reports"})
            assert result["allowed"] is True, "工作区内允许的文本文件可读取"
        def block_traversal():
            result = _call_solve(lesson_dir, {"kind": "file", "path": "../secrets.txt", "workspace": "reports"})
            assert result["allowed"] is False, "路径穿越必须拒绝"
        def validate_url():
            good = _call_solve(lesson_dir, {"kind": "url", "url": "https://example.test/report"})
            bad = _call_solve(lesson_dir, {"kind": "url", "url": "https://user:pass@example.test:22/private"})
            assert good["allowed"] is True and bad["allowed"] is False, "拒绝userinfo和非允许端口"
        cases += [_case("工作区内安全文本文件允许", allow_safe_local_files), _case("路径穿越访问拒绝", block_traversal), _case("不安全URL账号或端口拒绝", validate_url)]
    elif stage == 48:
        def cache_key_scoped_to_tenant():
            a = _call_solve(lesson_dir, {"tenant": "a", "user": "u", "key": "q", "writer": False})
            b = _call_solve(lesson_dir, {"tenant": "b", "user": "u", "key": "q", "writer": False})
            assert a["cache_key"] != b["cache_key"], "不同租户不能共享缓存"
        def writer_not_implicitly_approved():
            result = _call_solve(lesson_dir, {"tenant": "a", "user": "u", "key": "q", "writer": True, "approval": False})
            assert result["allowed"] is False, "写操作没有审批不能放行"
        def audit_redacts_sensitive_body():
            result = _call_solve(lesson_dir, {"tenant": "a", "user": "u", "key": "q", "body": "secret", "token": "secret-token"})
            assert "secret" not in str(result) and "secret-token" not in str(result), "审计结果不得保存正文或token"
        cases += [_case("缓存键按租户隔离", cache_key_scoped_to_tenant), _case("写操作需审批", writer_not_implicitly_approved), _case("审计结果隐藏正文和token", audit_redacts_sensitive_body)]
    elif stage == 49:
        def readiness_fails_when_dependency_down():
            result = _call_solve(lesson_dir, {"data_dir_writable": True, "dependency_healthy": False})
            assert result["readiness_status"] == 503 and result["liveness_status"] == 200, "依赖故障影响readiness而不代表进程死亡"
        def startup_requires_writable_data_dir():
            _raises(lambda: _call_solve(lesson_dir, {"data_dir_writable": False, "dependency_healthy": True}), "启动目录不可写应拒绝启动")
        def healthy_service_ready():
            result = _call_solve(lesson_dir, {"data_dir_writable": True, "dependency_healthy": True})
            assert result["readiness_status"] == 200 and result["liveness_status"] == 200, "依赖正常时两个探针均健康"
        cases += [_case("依赖故障影响就绪而非存活", readiness_fails_when_dependency_down), _case("数据目录不可写时启动拒绝", startup_requires_writable_data_dir), _case("依赖正常时探针健康", healthy_service_ready)]
    elif stage == 50:
        def bad_candidate_keeps_old_version():
            result = _call_solve(lesson_dir, {"active_version": "v1", "candidate": {"version": "v2", "quality": .2, "valid": False}})
            assert result["active_version"] == "v1" and result["released"] is False, "不合格候选版本不能覆盖当前版本"
        def valid_candidate_releases():
            result = _call_solve(lesson_dir, {"active_version": "v1", "candidate": {"version": "v2", "quality": .99, "valid": True}})
            assert result["active_version"] == "v2" and result["released"] is True, "验收通过后才更新活动版本"
        def existing_task_stays_pinned():
            result = _call_solve(lesson_dir, {"active_version": "v2", "task_version": "v1", "candidate": {"version": "v2", "quality": .99, "valid": True}})
            assert result["task_version"] == "v1", "运行中的任务绑定原版本"
        cases += [_case("候选版本失败保留旧版本", bad_candidate_keeps_old_version), _case("有效候选版本可以发布", valid_candidate_releases), _case("运行中任务保持原版本", existing_task_stays_pinned)]
    elif stage == 51:
        def tenant_buckets_separate():
            result = _call_solve(lesson_dir, {"events": [{"tenant": "a", "cost": 2, "time": 1}, {"tenant": "b", "cost": 3, "time": 1}]})
            assert result["by_tenant"] == {"a": 2, "b": 3}, "成本统计必须隔离租户"
        def reject_negative_cost():
            _raises(lambda: _call_solve(lesson_dir, {"events": [{"tenant": "a", "cost": -1, "time": 1}]}), "负成本不得进入计量")
        def percentile_is_computed():
            result = _call_solve(lesson_dir, {"latencies_ms": [10, 20, 30, 40]})
            assert result["p95_ms"] >= 30 and result["p95_ms"] <= 40, "p95需根据样本计算，不能取平均值冒充"
        cases += [_case("成本统计按租户隔离", tenant_buckets_separate), _case("负成本拒绝入账", reject_negative_cost), _case("延迟p95依据样本计算", percentile_is_computed)]
    elif stage == 52:
        def offline_restore_report_counts_and_states():
            result = _call_solve(lesson_dir, {"tasks": [{"id": "a", "state": "ready"}, {"id": "b", "state": "completed"}], "backup_valid": True})
            assert result["restored"] is True and result["task_count"] == 2 and result["states"]["ready"] == 1, "离线报告应核对给定任务快照中的数量和状态分布"
        def offline_invalid_backup_not_reported_as_restored():
            result = _call_solve(lesson_dir, {"tasks": [], "backup_valid": False})
            assert result["restored"] is False, "离线输入标记无效时不能声称恢复成功"
        def feedback_dedup_keeps_source_and_redacts_body():
            result = _call_solve(lesson_dir, {"backup_valid": True, "tasks": [], "feedback": [{"id": "f1", "source": "case-1", "body": "private"}, {"id": "f1", "source": "case-1", "body": "private"}]})
            assert len(result["feedback"]) == 1 and result["feedback"][0]["source"] == "case-1", "反馈去重保留来源"
            assert "private" not in str(result), "不能把反馈正文写进恢复报告"
        cases += [_case("离线恢复报告核对任务数量与状态", offline_restore_report_counts_and_states), _case("离线无效备份不标记恢复成功", offline_invalid_backup_not_reported_as_restored), _case("反馈按来源去重并脱敏", feedback_dedup_keeps_source_and_redacts_body)]
    elif stage == 53:
        def stale_sources_filtered_and_cited():
            result = _call_solve(lesson_dir, {"facts": [{"text": "A", "source": "new", "active": True}, {"text": "old", "source": "old", "active": False}]})
            assert len(result["facts"]) == 1 and result["facts"][0]["text"] == "A" and result["facts"][0]["source"] == "new", "过期来源过滤且每条事实保留引用"
        def missing_source_rejected():
            _raises(lambda: _call_solve(lesson_dir, {"facts": [{"text": "A", "active": True}]}), "无来源事实不能作为答案")
        def deduplicate_source_stably():
            result = _call_solve(lesson_dir, {"facts": [{"text": "A", "source": "s1", "active": True}, {"text": "A", "source": "s1", "active": True}]})
            assert len(result["facts"]) == 1, "重复来源按稳定标识去重"
        cases += [_case("有效事实保留引用来源", stale_sources_filtered_and_cited), _case("无来源事实拒绝输出", missing_source_rejected), _case("重复来源事实稳定去重", deduplicate_source_stably)]
    elif stage == 54:
        def reject_outside_workspace_and_stale_data():
            result = _call_solve(lesson_dir, {"workspace": "project", "path": "../outside.py", "current": "new", "reviewed": "old"})
            assert result["allowed"] is False and result["stale"] is True, "越界文件和过期审查结果都应阻止"
        def valid_diff_detected():
            result = _call_solve(lesson_dir, {"workspace": "project", "path": "project/app.py", "current": "new", "reviewed": "new"})
            assert result["allowed"] is True and result["diff"] is not None, "同一工作区内产生可审阅diff"
        def failing_tests_not_marked_fixed():
            result = _call_solve(lesson_dir, {"workspace": "project", "path": "project/app.py", "tests_passed": False, "claimed_fixed": True})
            assert result["status"] != "fixed", "失败测试不能被声明为已修复"
        cases += [_case("越界路径和过期审查均阻止", reject_outside_workspace_and_stale_data), _case("工作区内变更生成差异", valid_diff_detected), _case("测试失败不能标为修复", failing_tests_not_marked_fixed)]
    elif stage == 55:
        def same_idempotency_returns_same_ticket():
            module = _load_student(lesson_dir)
            function = getattr(module, "solve", None)
            if not callable(function):
                raise AssertionError("请实现solve(data)上传适配器")
            result = function({"key": "k1", "mime": "text/plain", "content": "申请", "approved": True})
            assert result["ticket_id"] and result["replayed"] is False
            replay = function({"key": "k1", "mime": "text/plain", "content": "申请", "approved": True})
            assert replay["ticket_id"] == result["ticket_id"] and replay["replayed"] is True, "幂等重放返回同一工单"
        def no_approval_and_bad_mime_rejected():
            for data in ({"key": "k2", "mime": "text/plain", "content": "x", "approved": False}, {"key": "k3", "mime": "application/octet-stream", "content": "x", "approved": True}):
                result = _call_solve(lesson_dir, data)
                assert result["accepted"] is False, "没有审批或MIME不允许时不能提交"
        def empty_or_oversize_rejected():
            for content in ("", "x" * 10000):
                result = _call_solve(lesson_dir, {"key": "k4", "mime": "text/plain", "content": content, "approved": True, "max_chars": 100})
                assert result["accepted"] is False, "空内容或超限内容应拒绝"
        cases += [_case("相同幂等请求复用工单编号", same_idempotency_returns_same_ticket), _case("上传必须审批且类型允许", no_approval_and_bad_mime_rejected), _case("空内容或超大内容拒绝", empty_or_oversize_rejected)]
    elif stage == 56:
        def approval_binds_to_unchanged_action():
            action = {"title": "新工单"}
            result = _call_solve(lesson_dir, {"action": action, "approved_action": action.copy(), "approved": True, "expires_at": 10, "now": 1})
            assert result["allowed"] is True, "有效审批与未改变动作匹配时可执行"
        def changed_expired_or_revoked_blocked():
            cases = [
                {"action": {"title": "changed"}, "approved_action": {"title": "old"}, "approved": True, "expires_at": 10, "now": 1},
                {"action": {"title": "x"}, "approved_action": {"title": "x"}, "approved": True, "expires_at": 1, "now": 1},
                {"action": {"title": "x"}, "approved_action": {"title": "x"}, "approved": False, "expires_at": 10, "now": 1},
            ]
            for data in cases:
                result = _call_solve(lesson_dir, data)
                assert result["allowed"] is False, "修改、撤销或过期审批必须重新审批"
        def offline_idempotency_record_loaded():
            result = _call_solve(lesson_dir, {"operations": [{"key": "k", "digest": "a", "result": "T1"}], "key": "k", "digest": "b", "restarted": True})
            assert result["status"] == "conflict" and result["recovered"] is True, "离线报告应加载给定操作记录并保留冲突结果"
        cases += [_case("审批与未修改动作匹配", approval_binds_to_unchanged_action), _case("修改撤销或过期审批均阻止", changed_expired_or_revoked_blocked), _case("离线操作记录加载后报告幂等冲突", offline_idempotency_record_loaded)]
    return cases


def _case(name, check):
    return name, check
