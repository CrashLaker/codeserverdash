

svc=app

restart:
	systemctl restart $(svc)
    
start:
	systemctl start $(svc)

stop:
	systemctl stop $(svc)

status:
	systemctl status $(svc)
    
edit:
	vim /usr/lib/systemd/system/$(svc).service
