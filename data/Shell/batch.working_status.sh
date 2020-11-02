#!/bin/sh

docker run --rm --link mysql:mysql -v /home/ec2-user/workspace/sales/:/sales yangwanjun/sales python /sales/manage.py working_status
