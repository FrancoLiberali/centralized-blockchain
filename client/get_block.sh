#!/bin/bash
docker build -f Dockerfile -t blockchain_client:lastest ..
docker run --network=blockchain_net --volume `pwd`/blockchain_files:/blockchain_files blockchain_client:lastest python3 /get_block.py $1