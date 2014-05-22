#启动rabbitmq

#后台启动
sudo rabbitmq-server -detached

#启动celery

celery -A insight  worker -l info

#启动django
sh startup.sh



#服务器端
#后端启动服务
celery -A insight  worker -l info --detach --pid=/home/mark/celery/insight.pid --logfile=/home/mark/celery/insight.log

