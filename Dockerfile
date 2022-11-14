FROM ubuntu:20.04


RUN apt-get update
RUN apt install git -y
RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install tzdata
RUN apt-get install cmake curl sudo nano screen -y
RUN curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
RUN sudo apt-get install -y nodejs
RUN npm install -g ganache-cli
RUN sudo apt-get install python3-pip -y
RUN pip3 install cython
RUN pip3 install web3 multipledispatch py-solc-x pymongo numpy streamlit pandas plotly altair matplotlib 
RUN pip3 install streamlit-timeline
RUN curl -sSL https://get.docker.com/ | sh

COPY 00_utils /home/00_utils
COPY 01_ganache_cli /home/01_ganache_cli
COPY 02_contracts /home/02_contracts
COPY 03_etl /home/03_etl
COPY 04_dashboard /home/04_dashboard

COPY 01_start_ganache_cli.sh /home/
COPY 02_start_databases.sh /home/
COPY 03_deploy_contract.sh /home/
COPY 04_eventetl.sh /home/
COPY 05_random_data_generator.sh /home/
COPY 06_dashboard.sh /home/ 

COPY run_all.sh /home/



