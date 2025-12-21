"""
测试监控和报告系统 - 提供详细的测试报告和监控功能
"""
import time
import json
import os
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from django.test import TestCase
from django.conf import settings
import matplotlib.pyplot as plt
import pandas as pd

# 确保matplotlib使用非交互式后端
plt.switch_backend('Agg')


class TestMonitor:
    """测试监控器 - 收集和分析测试数据"""
    
    def __init__(self):
        self.test_results = []
        self.performance_data = []
        self.coverage_data = {}
        self.error_data = []
        self.start_time = None
        self.end_time = None
    
    def start_test_session(self):
        """开始测试会话"""
        self.start_time = datetime.now(timezone.utc)
        self.test_results = []
        self.performance_data = []
        self.error_data = []
    
    def end_test_session(self):
        """结束测试会话"""
        self.end_time = datetime.now(timezone.utc)
    
    def record_test_result(self, test_name: str, status: str, 
                         execution_time: float, error: Optional[str] = None):
        """记录测试结果"""
        result = {
            "test_name": test_name,
            "status": status,
            "execution_time": execution_time,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": error
        }
        self.test_results.append(result)
    
    def record_performance_data(self, test_name: str, metric_type: str, 
                             value: float, unit: str = "ms"):
        """记录性能数据"""
        data = {
            "test_name": test_name,
            "metric_type": metric_type,
            "value": value,
            "unit": unit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.performance_data.append(data)
    
    def record_error(self, test_name: str, error_type: str, 
                    error_message: str, traceback: str = ""):
        """记录错误信息"""
        error = {
            "test_name": test_name,
            "error_type": error_type,
            "error_message": error_message,
            "traceback": traceback,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.error_data.append(error)
    
    def get_test_summary(self) -> Dict[str, Any]:
        """获取测试摘要"""
        if not self.test_results:
            return {}
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASSED"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAILED"])
        skipped_tests = len([r for r in self.test_results if r["status"] == "SKIPPED"])
        
        execution_times = [r["execution_time"] for r in self.test_results]
        avg_execution_time = sum(execution_times) / len(execution_times)
        max_execution_time = max(execution_times)
        min_execution_time = min(execution_times)
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "skipped_tests": skipped_tests,
            "success_rate": passed_tests / total_tests * 100 if total_tests > 0 else 0,
            "avg_execution_time": avg_execution_time,
            "max_execution_time": max_execution_time,
            "min_execution_time": min_execution_time,
            "total_execution_time": sum(execution_times),
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": (self.end_time - self.start_time).total_seconds() if self.start_time and self.end_time else None
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        if not self.performance_data:
            return {}
        
        # 按指标类型分组
        metrics_by_type = {}
        for data in self.performance_data:
            metric_type = data["metric_type"]
            if metric_type not in metrics_by_type:
                metrics_by_type[metric_type] = []
            metrics_by_type[metric_type].append(data["value"])
        
        summary = {}
        for metric_type, values in metrics_by_type.items():
            summary[metric_type] = {
                "avg": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "count": len(values),
                "unit": self.performance_data[0]["unit"]  # 假设单位一致
            }
        
        return summary


class TestReporter:
    """测试报告生成器 - 生成各种格式的测试报告"""
    
    def __init__(self, monitor: TestMonitor):
        self.monitor = monitor
        self.report_dir = "test_reports"
        os.makedirs(self.report_dir, exist_ok=True)
    
    def generate_html_report(self) -> str:
        """生成HTML格式的测试报告"""
        summary = self.monitor.get_test_summary()
        performance_summary = self.monitor.get_performance_summary()
        
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PolyMetric API 测试报告</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            border-left: 4px solid #3498db;
            padding-left: 15px;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .summary-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        .summary-card h3 {{
            margin: 0 0 10px 0;
            font-size: 2em;
        }}
        .summary-card p {{
            margin: 0;
            opacity: 0.9;
        }}
        .status-passed {{ background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }}
        .status-failed {{ background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%); }}
        .status-skipped {{ background: linear-gradient(135deg, #ffd89b 0%, #19547b 100%); }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background-color: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .test-passed {{ color: #27ae60; font-weight: bold; }}
        .test-failed {{ color: #e74c3c; font-weight: bold; }}
        .test-skipped {{ color: #f39c12; font-weight: bold; }}
        .chart-container {{
            margin: 30px 0;
            text-align: center;
        }}
        .error-details {{
            background-color: #fdf2f2;
            border-left: 4px solid #e74c3c;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
        }}
        .performance-metric {{
            background-color: #e8f4f8;
            border-left: 4px solid #3498db;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #7f8c8d;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>PolyMetric API 测试报告</h1>
        
        <h2>测试摘要</h2>
        <div class="summary-grid">
            <div class="summary-card">
                <h3>{summary.get('total_tests', 0)}</h3>
                <p>总测试数</p>
            </div>
            <div class="summary-card status-passed">
                <h3>{summary.get('passed_tests', 0)}</h3>
                <p>通过测试</p>
            </div>
            <div class="summary-card status-failed">
                <h3>{summary.get('failed_tests', 0)}</h3>
                <p>失败测试</p>
            </div>
            <div class="summary-card status-skipped">
                <h3>{summary.get('skipped_tests', 0)}</h3>
                <p>跳过测试</p>
            </div>
            <div class="summary-card">
                <h3>{summary.get('success_rate', 0):.1f}%</h3>
                <p>成功率</p>
            </div>
            <div class="summary-card">
                <h3>{summary.get('total_execution_time', 0):.2f}s</h3>
                <p>总执行时间</p>
            </div>
        </div>
        
        <h2>性能摘要</h2>
        {self._generate_performance_html(performance_summary)}
        
        <h2>测试结果详情</h2>
        <table>
            <thead>
                <tr>
                    <th>测试名称</th>
                    <th>状态</th>
                    <th>执行时间 (秒)</th>
                    <th>时间戳</th>
                    <th>错误信息</th>
                </tr>
            </thead>
            <tbody>
                {self._generate_test_results_html()}
            </tbody>
        </table>
        
        {self._generate_error_details_html()}
        
        <div class="footer">
            <p>报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>PolyMetric API 测试系统</p>
        </div>
    </div>
</body>
</html>
        """
        
        report_path = os.path.join(self.report_dir, f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return report_path
    
    def _generate_performance_html(self, performance_summary: Dict[str, Any]) -> str:
        """生成性能摘要HTML"""
        if not performance_summary:
            return "<p>暂无性能数据</p>"
        
        html = ""
        for metric_type, data in performance_summary.items():
            html += f"""
            <div class="performance-metric">
                <h4>{metric_type}</h4>
                <p>平均值: {data['avg']:.2f} {data['unit']}</p>
                <p>最小值: {data['min']:.2f} {data['unit']}</p>
                <p>最大值: {data['max']:.2f} {data['unit']}</p>
                <p>样本数: {data['count']}</p>
            </div>
            """
        
        return html
    
    def _generate_test_results_html(self) -> str:
        """生成测试结果HTML表格"""
        html = ""
        for result in self.monitor.test_results:
            status_class = f"test-{result['status'].lower()}"
            error_info = result.get('error', '')[:100] + '...' if result.get('error') and len(result.get('error', '')) > 100 else result.get('error', '')
            
            html += f"""
            <tr>
                <td>{result['test_name']}</td>
                <td class="{status_class}">{result['status']}</td>
                <td>{result['execution_time']:.3f}</td>
                <td>{result['timestamp']}</td>
                <td>{error_info}</td>
            </tr>
            """
        
        return html
    
    def _generate_error_details_html(self) -> str:
        """生成错误详情HTML"""
        if not self.monitor.error_data:
            return ""
        
        html = "<h2>错误详情</h2>"
        for error in self.monitor.error_data:
            html += f"""
            <div class="error-details">
                <h4>{error['test_name']} - {error['error_type']}</h4>
                <p><strong>错误信息:</strong> {error['error_message']}</p>
                {f"<p><strong>堆栈跟踪:</strong> <pre>{error['traceback']}</pre></p>" if error.get('traceback') else ""}
                <p><strong>时间:</strong> {error['timestamp']}</p>
            </div>
            """
        
        return html
    
    def generate_json_report(self) -> str:
        """生成JSON格式的测试报告"""
        report_data = {
            "test_summary": self.monitor.get_test_summary(),
            "performance_summary": self.monitor.get_performance_summary(),
            "test_results": self.monitor.test_results,
            "performance_data": self.monitor.performance_data,
            "error_data": self.monitor.error_data,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
        report_path = os.path.join(self.report_dir, f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        return report_path
    
    def generate_performance_charts(self) -> List[str]:
        """生成性能图表"""
        if not self.monitor.performance_data:
            return []
        
        chart_paths = []
        
        # 按指标类型分组
        metrics_by_type = {}
        for data in self.monitor.performance_data:
            metric_type = data["metric_type"]
            if metric_type not in metrics_by_type:
                metrics_by_type[metric_type] = []
            metrics_by_type[metric_type].append(data)
        
        # 为每种指标类型生成图表
        for metric_type, data_list in metrics_by_type.items():
            plt.figure(figsize=(12, 6))
            
            # 提取数据
            values = [d["value"] for d in data_list]
            timestamps = [datetime.fromisoformat(d["timestamp"]) for d in data_list]
            
            # 绘制时间序列图
            plt.plot(timestamps, values, marker='o', linewidth=2, markersize=6)
            plt.title(f'{metric_type} 性能趋势')
            plt.xlabel('时间')
            plt.ylabel(f'{metric_type} ({data_list[0]["unit"]})')
            plt.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # 保存图表
            chart_path = os.path.join(self.report_dir, f'performance_{metric_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            chart_paths.append(chart_path)
        
        return chart_paths
    
    def generate_coverage_report(self, coverage_data: Dict[str, Any]) -> str:
        """生成覆盖率报告"""
        if not coverage_data:
            return ""
        
        html = """
        <h2>代码覆盖率报告</h2>
        <div class="summary-grid">
        """
        
        for module, data in coverage_data.items():
            coverage_percent = data.get('percent_covered', 0)
            color_class = "status-passed" if coverage_percent >= 80 else "status-failed" if coverage_percent < 60 else "status-skipped"
            
            html += f"""
            <div class="summary-card {color_class}">
                <h3>{coverage_percent:.1f}%</h3>
                <p>{module}</p>
            </div>
            """
        
        html += "</div>"
        
        return html


class TestAlertSystem:
    """测试警报系统 - 监控测试结果并发送警报"""
    
    def __init__(self, monitor: TestMonitor):
        self.monitor = monitor
        self.alert_thresholds = {
            "success_rate": 90.0,  # 成功率低于90%警报
            "avg_execution_time": 5.0,  # 平均执行时间超过5秒警报
            "failed_tests": 5,  # 失败测试数超过5个警报
        }
    
    def check_alerts(self) -> List[Dict[str, Any]]:
        """检查警报条件"""
        alerts = []
        summary = self.monitor.get_test_summary()
        
        # 检查成功率
        if summary.get('success_rate', 100) < self.alert_thresholds["success_rate"]:
            alerts.append({
                "type": "LOW_SUCCESS_RATE",
                "message": f"测试成功率 {summary.get('success_rate', 0):.1f}% 低于阈值 {self.alert_thresholds['success_rate']}%",
                "severity": "HIGH"
            })
        
        # 检查平均执行时间
        if summary.get('avg_execution_time', 0) > self.alert_thresholds["avg_execution_time"]:
            alerts.append({
                "type": "SLOW_EXECUTION",
                "message": f"平均执行时间 {summary.get('avg_execution_time', 0):.2f}s 超过阈值 {self.alert_thresholds['avg_execution_time']}s",
                "severity": "MEDIUM"
            })
        
        # 检查失败测试数
        if summary.get('failed_tests', 0) > self.alert_thresholds["failed_tests"]:
            alerts.append({
                "type": "MANY_FAILURES",
                "message": f"失败测试数 {summary.get('failed_tests', 0)} 超过阈值 {self.alert_thresholds['failed_tests']}",
                "severity": "HIGH"
            })
        
        return alerts
    
    def send_alerts(self, alerts: List[Dict[str, Any]]):
        """发送警报"""
        for alert in alerts:
            self._log_alert(alert)
            # 这里可以添加其他警报发送方式，如邮件、Slack等
    
    def _log_alert(self, alert: Dict[str, Any]):
        """记录警报到日志"""
        logger = logging.getLogger('test_alerts')
        logger.warning(
            f"测试警报: {alert['type']} - {alert['message']} (严重程度: {alert['severity']})"
        )


class TestMonitoringTestCase(TestCase):
    """测试监控测试用例"""
    
    def setUp(self):
        super().setUp()
        self.monitor = TestMonitor()
        self.reporter = TestReporter(self.monitor)
        self.alert_system = TestAlertSystem(self.monitor)
    
    def test_monitoring_system(self):
        """测试监控系统功能"""
        # 开始测试会话
        self.monitor.start_test_session()
        
        # 模拟一些测试结果
        self.monitor.record_test_result("test_user_registration", "PASSED", 0.5)
        self.monitor.record_test_result("test_user_login", "PASSED", 0.3)
        self.monitor.record_test_result("test_dataset_creation", "FAILED", 2.1, "Validation error")
        self.monitor.record_test_result("test_model_list", "PASSED", 0.8)
        
        # 模拟性能数据
        self.monitor.record_performance_data("test_user_registration", "response_time", 500, "ms")
        self.monitor.record_performance_data("test_user_login", "response_time", 300, "ms")
        self.monitor.record_performance_data("test_dataset_creation", "response_time", 2100, "ms")
        
        # 模拟错误数据
        self.monitor.record_error(
            "test_dataset_creation", 
            "ValidationError", 
            "Invalid file format",
            "Traceback..."
        )
        
        # 结束测试会话
        self.monitor.end_test_session()
        
        # 生成报告
        html_report = self.reporter.generate_html_report()
        json_report = self.reporter.generate_json_report()
        charts = self.reporter.generate_performance_charts()
        
        # 验证报告文件已生成
        self.assertTrue(os.path.exists(html_report))
        self.assertTrue(os.path.exists(json_report))
        self.assertGreater(len(charts), 0)
        
        # 检查警报
        alerts = self.alert_system.check_alerts()
        if alerts:
            self.alert_system.send_alerts(alerts)
        
        # 验证监控数据
        summary = self.monitor.get_test_summary()
        self.assertEqual(summary['total_tests'], 4)
        self.assertEqual(summary['passed_tests'], 3)
        self.assertEqual(summary['failed_tests'], 1)
        self.assertEqual(summary['success_rate'], 75.0)
        
        performance_summary = self.monitor.get_performance_summary()
        self.assertIn('response_time', performance_summary)


# 全局监控器实例
_global_monitor = None
_global_reporter = None
_global_alert_system = None


def get_monitor():
    """获取全局监控器实例"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = TestMonitor()
    return _global_monitor


def get_reporter():
    """获取全局报告器实例"""
    global _global_reporter
    if _global_reporter is None:
        _global_reporter = TestReporter(get_monitor())
    return _global_reporter


def get_alert_system():
    """获取全局警报系统实例"""
    global _global_alert_system
    if _global_alert_system is None:
        _global_alert_system = TestAlertSystem(get_monitor())
    return _global_alert_system


def start_test_monitoring():
    """开始测试监控"""
    monitor = get_monitor()
    monitor.start_test_session()


def end_test_monitoring():
    """结束测试监控并生成报告"""
    monitor = get_monitor()
    reporter = get_reporter()
    alert_system = get_alert_system()
    
    monitor.end_test_session()
    
    # 生成报告
    html_report = reporter.generate_html_report()
    json_report = reporter.generate_json_report()
    charts = reporter.generate_performance_charts()
    
    print(f"测试报告已生成:")
    print(f"HTML报告: {html_report}")
    print(f"JSON报告: {json_report}")
    print(f"性能图表: {len(charts)} 个")
    
    # 检查警报
    alerts = alert_system.check_alerts()
    if alerts:
        print(f"发现 {len(alerts)} 个警报:")
        for alert in alerts:
            print(f"  - {alert['type']}: {alert['message']}")
        alert_system.send_alerts(alerts)
    else:
        print("没有发现警报")