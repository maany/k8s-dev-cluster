```
 _______   _______    ______   _______    ______         __         ______            
/       \ /       \  /      \ /       \  /      \       /  |       /      \           
$$$$$$$  |$$$$$$$  |/$$$$$$  |$$$$$$$  |/$$$$$$  |      $$ |   __ /$$$$$$  |  _______ 
$$ |__$$ |$$ |__$$ |$$ |__$$ |$$ |  $$ |$$ |__$$ |      $$ |  /  |$$ \__$$ | /       |
$$    $$/ $$    $$< $$    $$ |$$ |  $$ |$$    $$ |      $$ |_/$$/ $$    $$< /$$$$$$$/ 
$$$$$$$/  $$$$$$$  |$$$$$$$$ |$$ |  $$ |$$$$$$$$ |      $$   $$<   $$$$$$  |$$      \ 
$$ |      $$ |  $$ |$$ |  $$ |$$ |__$$ |$$ |  $$ |      $$$$$$  \ $$ \__$$ | $$$$$$  |
$$ |      $$ |  $$ |$$ |  $$ |$$    $$/ $$ |  $$ |      $$ | $$  |$$    $$/ /     $$/ 
$$/       $$/   $$/ $$/   $$/ $$$$$$$/  $$/   $$/       $$/   $$/  $$$$$$/  $$$$$$$/ 

```

# Vagrantfile, Scripts and a Python CLI to Automate Kubernetes Setup using Kubeadm
- Code for the Python CLI is under the `tools` directory
- Scripts for configuring the guests created by Vagrant are in the `scripts` directory

# Documentation

## What this does?
This vagrant file can spin up the following types of VMs
1. master: K8s Control Plane
2. worker: Run business workloads ( taint `k8s.prada.io/workload=app:NoSchedule`)
3. storage: runs Longhorn
4. infra: runs in-cluster utilities like Metallb, CertManager, Traefik, Longhorn, ...

You can modify the number of each type of VMs (except master) that you would like to bring up.

No CNI plugin is installed. `Cilium` will be used as the CNI Network Plugin. It can be configured later using the CLI. 
** This is since cilium requires all nodes in a k8s cluster to be available and we did not go the route of running a post processor in Vagrant.
## Prerequisites

1. Working Vagrant setup
2. 16 Gig + RAM workstation with 8+ cores and 20GB+ storage

## For MAC/Linux Users

Latest version of Virtualbox for Mac/Linux can cause issues because you have to create/edit the /etc/vbox/networks.conf file and add:
<pre>* 0.0.0.0/0 ::/0</pre>

or run below commands

```shell
sudo mkdir -p /etc/vbox/
echo "* 0.0.0.0/0 ::/0" | sudo tee -a /etc/vbox/networks.conf
```

So that the host only networks can be in any range, not just 192.168.56.0/21 as described here:
https://discuss.hashicorp.com/t/vagrant-2-2-18-osx-11-6-cannot-create-private-network/30984/23

## Usage/Examples

To provision the cluster, execute the following commands.

```shell
vagrant up
```

## Set Kubeconfig file variable

```shell
cd configs
export KUBECONFIG=$(pwd)/config
```

or you can copy the config file to .kube directory.

```shell
cp configs/config ~/.kube/
```

## To shutdown the cluster,

```shell
vagrant halt
```

## To restart the cluster,

```shell
vagrant up
```

## To destroy the cluster,

```shell
vagrant destroy -f
```

## Further configuration with the CLI
To provision the cluster with Metallb, Longhorn, Kube Prometheus Stack, Traefik, Certmanager, .. please follow the instructions [here](./tools/README.md)
