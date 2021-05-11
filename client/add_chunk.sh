#!/bin/bash
docker build -f Dockerfile -t blockchain_client:lastest ..
docker run --network=blockchain_net blockchain_client:lastest python3 /main.py /$1