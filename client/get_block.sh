#!/bin/bash
docker build -f Dockerfile -t blockchain_client:lastest ..
docker run --network=blockchain_net --env-file get_block_env.list blockchain_client:lastest python3 /get_block.py $1