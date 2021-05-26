#!/bin/bash
docker-compose down
sudo rm -rf storage_manager/blockchain_files/*
sudo rm -rf blockchain/blockchain_components/mined_counter/mined_per_miner_files/*