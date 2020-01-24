#! /bin/sh

for demo in $(ls); do
  cd $demo
  echo "Demo number $demo"
  sleep 2
  python3 ../../main.py
  cd ..
done

