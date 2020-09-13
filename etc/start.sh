REBELLIO_VERSION = "v0.0.2"
docker stop rebellio
docker rm rebellio
docker run --network=host -id --restart=always --name="rebellio" rebellio:${REBELLIO_VERSION}