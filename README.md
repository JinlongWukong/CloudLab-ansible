# CloudLab-ansible-vm

## Overview
This is a part of repo [CloudLab](https://github.com/JinlongWukong/CloudLab)

## Installation

#### Build docker image
```
docker build -t deployer --build-arg https_proxy=xxxxxxx .
```
#### Run container
```
docker run --net host --rm --env https_proxy=xxxx deployer
```