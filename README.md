# DevLab-ansible

## Overview
This is a part of repo [DevLab](https://github.com/JinlongWukong/DevLab)

## Installation

#### Build docker image
```
docker build -t deployer --build-arg https_proxy=xxxxxxx .
```
#### Run container
```
docker run -d --name devlab_deployer --net host --rm --env https_proxy=xxxx deployer
```