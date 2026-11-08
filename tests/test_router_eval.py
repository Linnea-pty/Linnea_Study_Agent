"""路由准确率评估测试。"""

from linnea_agent.evaluation.router_eval import evaluate_router


def test_router_accuracy_threshold():
    accuracy, errors = evaluate_router()
    assert accuracy >= 0.9, f"路由准确率过低：{accuracy}，错误用例：{errors}"
