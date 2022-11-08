#!/bin/bash
#
# Setup for Node servers

set -euxo pipefail

/bin/bash /vagrant/configs/join.sh -v

sudo -i -u vagrant bash << EOF
whoami
mkdir -p /home/vagrant/.kube
sudo cp -i /vagrant/configs/config /home/vagrant/.kube/
sudo chown 1000:1000 /home/vagrant/.kube/config
NODENAME=$(hostname -s)
kubectl label node $(hostname -s) node-role.kubernetes.io/worker=worker
kubectl label node $(hostname -s) role=worker
kubectl taint nodes $(hostname -s) workload=prada:NoSchedule-
EOF
