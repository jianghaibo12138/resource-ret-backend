# resource-ret-backend
The backend for resource-ret. https://github.com/jianghaibo12138/resource-ret

### 为 [resource-ret](https://github.com/jianghaibo12138/resource-ret, "resource-ret") 的后台服务 ###
- 项目介绍
    - 后台框架 [django](, "django")
    - restful框架 [django-restframework](, "django-restframework")
    - 异步组件框架 [celery](, "celery")
    - 消息中间件 [rabbitmq](, "rabbitmq")
    - 数据库 [mysql](, "mysql")
    - 数据缓存服务 [redis](, "redis")
    - 用户权限 [django-restframework.authtoken](, "django-restframework.authtoken")
    - websocket实现 [django channel](, "django channel")

- Todo
    - 项目docker化, 包括django, redis, mysql, rabbitmq等
    - 完善订单流程
    - 测试支付宝支付流程
    - 编写微信支付Api
    - 联调
    - supervisor + uwsgi + nginx 拉起整个项目

- 环境搭建&运行
    - 环境搭建
        - 使用pipenv
            - git clone && cd resource-ret-backend && pipenv --python=python3 && pipenv install 
        - 使用virtualenv
            - git clone && cd resource-ret-backend && virtualenv -p /usr/local/bin/python3 resource-ret-backend-env && pip install -r requirements.txt
        
    - 运行
        - django服务
            - python manage.py runserver 0.0.0.0:8080
            
        - celery服务
            - python manage.py celery worker -l info
    
- 部署
    - todo... 
    