#!/bin/bash

screen -d -m -S process1 ./01_start_ganache_cli.sh
sleep 60
screen -d -m -S process2 ./02_start_databases.sh
sleep 60
screen -d -m -S process3 ./03_deploy_contract.sh
sleep 60
screen -d -m -S process4 ./04_eventetl.sh
sleep 60
screen -d -m -S process5 ./05_random_data_generator.sh
sleep 60
screen -d -m -S process6 ./06_dashboard.sh
