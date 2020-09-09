MYIP="0.0.0.0"
VOLTA_VERSION="v1.0.12"
docker stop rebellio
docker rm rebellio
docker run --network=host -id --restart=always --name="rebellio" rebellio