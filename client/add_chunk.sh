#!/bin/bash
docker build -f Dockerfile -t blockchain_client:lastest ..
docker run --network=blockchain_net --env-file add_chunk_env.list blockchain_client:lastest python3 /add_chunk.py $1