cd ..
docker build -t rebellio .
docker stop rebellio
docker rm rebellio
docker run --network=host -id --restart=always --name="rebellio" rebellio
