#!/bin/bash
for i in Kyle Rick Phil Angelica
do
    echo $i
    globus mkdir 325399ca-8600-447c-a6b6-928a68782f79:/dev/mock/$i
done
