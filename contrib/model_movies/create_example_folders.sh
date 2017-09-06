#!/bin/sh
mkdir folder
mkdir folder/sub1
mkdir folder/sub2
cd folder
touch some_file
ln -s some_file link__some_file
ln -s /tmp link__tmp
ln -s sub1 link__sub1
ln -s /DOES-NOT-EXIST link__tononexisting
cd ..
ls -al folder
