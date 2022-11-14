#!/bin/bash
mkdir -p $(pwd)/databases/mongodb/
cd $(pwd)/databases/mongodb/

# sudo rm -rf db
# docker stop test express
# docker system prune -f
# docker container prune -f

# docker run -d -v $(pwd)/db:/data/db -p 27017:27017 --name test --network="host" mongo
#docker run -d -p 8081:8081 --link test:mongo --name express --network="host" mongo-express

docker run -d -v $(pwd)/db:/data/db --name test --network="host" mongo
docker run -d --name express --network="host" -e ME_CONFIG_MONGODB_SERVER="127.0.0.1" mongo-express

# trap ctrl_c INT

# function ctrl_c () {
#         echo "Stop Databases with CTRL-C"
# }

# sudo rm -rf db
# docker stop test express
# docker system prune
# docker container prune
