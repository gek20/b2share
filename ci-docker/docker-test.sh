#!/bin/bash
mkdir -p logs
docker-compose -f docker-compose.test.yml up -d
sleep 60

docker ps -a

while docker ps | grep 'tests'
do
    printf "\n"
    echo "Waiting for tests to complete, please be patient. Status:"
    docker-compose -f docker-compose.test.yml logs --tail=2 b2share-test
    sleep 60
done

echo "Tests has completed"

docker logs -t tests > ../logs.log

docker-compose -f docker-compose.test.yml down

cat ../logs.log

if grep -q "[1-9]\d* failed" ../logs.log
then
    echo "We have fails!"
    grep "[1-9]\d* failed" ../logs.log
    exit 1
else
    echo "No failures!"
fi