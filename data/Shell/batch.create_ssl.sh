#!/bin/sh

# 初回の場合は「renew」ではなく、「run」を使う
docker run --rm -v /home/ec2-user/ssl/.lego:/.lego goacme/lego --email="gao.lei@wisdom-technology.co.jp" --domains="works.wisdom-technology.co.jp" --http renew
docker run --rm -v /home/ec2-user/ssl/.lego:/.lego goacme/lego --email="gao.lei@wisdom-technology.co.jp" --domains="employees.wisdom-technology.co.jp" --http renew
docker run --rm -v /home/ec2-user/ssl/.lego:/.lego goacme/lego --email="gao.lei@wisdom-technology.co.jp" --domains="redmine.wisdom-technology.co.jp" --http renew
docker run --rm -v /home/ec2-user/ssl/.lego:/.lego goacme/lego --email="gao.lei@wisdom-technology.co.jp" --domains="sales.wisdom-technology.co.jp" --http renew
sudo nginx -s reload

# 作成した証明書をバックアップする
TODAY=`date +%Y%m%d`
DST_ROOT="/home/ec2-user/ssl/"
DST_DIR=certificates_$TODAY
DST_PATH=${DST_ROOT}${DST_DIR}

if [ ! -d "$DST_PATH" ]; then
  mkdir $DST_PATH
fi


SRC_PATH="/home/ec2-user/ssl/.lego/certificates/"
sudo cp ${SRC_PATH}* $DST_ROOT${DST_DIR}/
