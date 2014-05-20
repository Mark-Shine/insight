#启动rabbitmq

sudo nohup rabbitmq-server start > nohup.out& 

#启动celery

celery -A insight  worker -l info

#启动django
sh startup.sh