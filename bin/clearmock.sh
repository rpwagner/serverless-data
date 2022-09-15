#!/bin/bash

collection=325399ca-8600-447c-a6b6-928a68782f79
index=bb0b9165-872a-4959-96d2-910f73fd2f76

for i in Kyle Rick Phil Angelica
do
    echo $i
    globus rm -r $collection:/dev/mock/$i
done

for i in `globus search query -q "*" bb0b9165-872a-4959-96d2-910f73fd2f76`
do
    echo $i
    globus search subject delete $index $i
done
