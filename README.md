# resource-ret-backend
The backend for resource-ret. https://github.com/jianghaibo12138/resource-ret

### 为 [resource-ret](https://github.com/jianghaibo12138/resource-ret, "resource-ret") 的后台服务 ###
- 项目介绍
    - 后台框架 [django](https://docs.djangoproject.com/zh-hans/2.1/, "django")
    - restful框架 [django-restframework](https://www.django-rest-framework.org/, "django-restframework")
    - 异步组件框架 [celery](http://docs.jinkan.org/docs/celery/, "celery")
    - 消息中间件 [rabbitmq](https://www.rabbitmq.com/getstarted.html, "rabbitmq")
    - 数据库 [mysql](https://www.mysql.com/cn/, "mysql"), 并支持读写分离
    - 数据缓存服务 [redis](https://django-redis-chs.readthedocs.io/zh_CN/latest/, "redis")
    - 用户权限 [django-restframework.authtoken](https://www.django-rest-framework.org/tutorial/4-authentication-and-permissions/, "django-restframework.authtoken")
    - websocket实现 [django channel](https://channels.readthedocs.io/en/latest/, "django channel")

- Todo(√: 已经完成)
    - fix 由django-celery []()引起的 TypeError: can only concatenate tuple (not "NoneType") to tuple 错误导致celery无法启动 √
    - 系统派单模块 and 权重计算模块
    - 项目docker化, 包括django, redis, mysql, rabbitmq等 √
    - docker-compose 配置文件区分production和development √
    - 项目启动时load admin用户进入db 
    - 完善订单流程
    - 测试支付宝支付流程
    - 编写微信支付Api
    - 联调
    - supervisor + uwsgi + nginx 拉起整个项目

- 环境搭建&运行
    - 虚拟环境
        - 环境搭建
            - 使用 [pipenv](https://github.com/pypa/pipenv, "pipenv")
                - git clone && cd resource-ret-backend && pipenv --python=python3 && pipenv install 
            - 使用 [virtualenv](https://virtualenv.pypa.io/en/latest/, "virtualenv")
                - git clone && cd resource-ret-backend && virtualenv -p /usr/local/bin/python3 resource-ret-backend-env && pip install -r requirements.txt
            
        - 运行
            - django服务
                - python manage.py runserver 0.0.0.0:8080
                
            - celery服务
                - python manage.py celery worker -l info
    - docker
        - 工具 [docker-compose](https://docs.docker.com/compose/, "docker compose")
            ```bash
              pip install docker-compose or sudo pip install docker-compose
            ``` 
        - 构建
            ```bash
              docker-compose build 
            ```
        - 运行
            ```bash
              docker-compose up
            ```
            
            
- 部署
    - todo... 
    