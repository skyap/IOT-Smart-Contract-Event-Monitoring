# Smart Contract Event Monitoring and Visualization Dashboard using Streamlit
Please note that this dashboard build from the perspective of data scientist and make no claims to be a software developer.

## Remove all docker container before and after running project
```bash
./kill_all.sh
```
## Remove databases create from the last run
```bash
sudo rm -rf /home/databases
```

## Build docker
```bash
docker build -t experiment .
```
## Start experiment
1. Run docker
```bash
docker run -v /var/run/docker.sock:/var/run/docker.sock --network="host" -it experiment
```
2. Start the experiment
```bash
cd home
./run_all.sh
```
3. Run all take 5 minute to start up. This is to ensure every process run steadyly before we start the next process

## Dashboard and databases
1. To access to dashboard, open browser and type http://localhost:8501/
2. To access to mongo-express, open browser and type http://localhost:8081/




