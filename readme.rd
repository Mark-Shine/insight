




系统的启动操作步骤：
#启动rabbitmq

#后台启动
sudo rabbitmq-server -detached

#启动celery

celery -A insight  worker -l info

#启动django
sh startup.sh

#启动redis
nohup redis-server &

#服务器端
#后端启动服务 —— 这个服务必须用非root账户登陆
celery -A insight  worker -l info --detach --pid=/home/mark/celery/insight.pid --logfile=/home/mark/celery/insight.log



#注意 后期 将alarmrecord 的word字段改为外键，大部分bug已经修复