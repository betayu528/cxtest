# Django 测试平台

一个基于 Django 4.1 的测试平台骨架，覆盖以下模块：

- 用户与角色授权：测试、开发、产品、运营、管理员
- 项目树与环境管理
- 测试用例管理：自动化/非自动化、附件上传、Postman/Pytest 来源字段
- API 测试集合、接口定义与 HTTP/TCP/WebSocket 协议调试
- 异步任务执行与 CI 回调接口
- Mock 服务管理：HTTP/TCP/UDP/WebSocket 协议配置
- 测试数据管理
- 历史 Bug 论坛
- 知识沉淀文章与评论
- 通知中心

## 快速启动

```bash
python3 manage.py migrate
python3 manage.py seed_demo
python3 manage.py runserver
```

另开一个终端启动 Celery worker：

```bash
PYTHONPATH="$HOME/Library/Python/3.9/lib/python/site-packages:$PYTHONPATH" \
python3 -m celery -A test_platform worker -l info --pool solo
```

访问地址：

- 首页: `http://127.0.0.1:8000/`
- 后台: `http://127.0.0.1:8000/admin/`
- HTTP Mock 示例: `http://127.0.0.1:8000/mock/http/demo/login/`
- CI 触发示例: `POST http://127.0.0.1:8000/tasks/trigger/<integration_id>/`
- 任务动作地址: `POST http://127.0.0.1:8000/tasks/action/<task_id>/`

异步任务回调示例：

```bash
curl -X POST http://127.0.0.1:8000/tasks/callback/demo-callback-token/ \
  -H "Content-Type: application/json" \
  -d '{"status":"SUCCESS","report_url":"https://ci.example.com/job/1"}'
```

启动 TCP / UDP / WebSocket Mock 运行器：

```bash
python3 manage.py run_mock_workers
```

协议测试示例：

```bash
printf 'ping' | nc 127.0.0.1 9101
printf 'status' | nc -u 127.0.0.1 9102
```

## 当前实现说明

- 已完成平台级数据模型、后台管理、基础页面、角色权限组初始化、任务回调入口、Jenkins / GitLab CI 真实触发器和 HTTP/TCP/UDP/WebSocket Mock 运行器。
- 已集成 Celery 文件型 broker。任务从界面点击“开始”后进入 `QUEUED`，worker 消费后进入 `RUNNING`，界面可显示进度和当前状态。
- Jenkins 支持 `buildWithParameters`、可选 Crumb、Basic Auth；GitLab 支持 trigger pipeline 与变量透传。
- “暂停”当前实现为协作式暂停请求：已排队或执行中的 Celery 任务会在执行检查点停下并标记为 `PAUSED`。
- API 调试台现已支持 HTTP/HTTPS 自动注入平台鉴权头、TCP 发包回包、WebSocket 收发，以及二进制回包十六进制展示。
- API 自动运行、Postman 导入解析、Pytest/CI 深度结果解析仍适合下一阶段继续补执行器与报告汇总。
