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
# Kubernetes Admin Setup Utils
This is a python cli application to confiure Metallb, Traefik, Longhorn, Kube Prometheus Stack, Certmanager and letsencrypt certificates etc. for the Vagrant cluster

# Requirements
1. python3
2. helm3
3. kubectl
4. cilium CLI

Good to have:
1. k9s/ Lens


# Setup the CLI

Inside the directory containing this README file,

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Then install the CLI as a editable python package

```
pip install -e .
```

Test that you can access the CLI

```
$ k8s_admin_setup_utils 
Usage: k8s_admin_setup_utils [OPTIONS] COMMAND [ARGS]...

Options:
  -v, --verbosity  Verbosity level
  --help           Show this message and exit.

Commands:
  certmanager  Install or Configure cert manager on a Kubernetes Cluster
  dev-cluster  Configure the vagrant development cluster post launch
  longhorn     Install or Configure Longhorn Storage on a Kubernetes Cluster
  metallb      Install or Configure MetalLB on a Kubernetes Cluster
  monitoring   Install and Configure Kube Prometheus Stack
  traefik      Install or Configure Traefik on a Kubernetes Cluster
```

# Setup cluster resources

## Install Cilium
This command will perform the following steps
1. check_config,
1. add_helm_repo,
1. install_cilium,
1. wait_for_cilium_status,
1. restart_hubble,
1. wait_for_cilium_status

```
k8s_admin_setup_utils dev-cluster cilium install
```

## Reload coredns and metrics server
This is required for the coredns and metrics server pods to be assigned an IP address in the network range managed by `cilium`

```
k8s_admin_setup_utils dev-cluster reload
```

Now metrics should start showing up in `k9s` or `Lens`

## Install LongHorn
We use Longhorn for provisioning PersistentVolumes within the cluster. The `storage` nodes have a label `role: storage` and that's where all the Longhorn reources will be provisioned.

```
k8s_admin_setup_utils longhorn install
```

After running the command, use `k9s` to monitor the pods in the `longhorn-system` namespace and watch for events in the `longhorn-system` namespace.

```
k8s_admin_setup_utils  longhorn watch
```

Once everything has stabilized, you should see a `storageclass` by running
```
kubectl get sc
NAME                 PROVISIONER          RECLAIMPOLICY   VOLUMEBINDINGMODE   ALLOWVOLUMEEXPANSION   AGE
longhorn (default)   driver.longhorn.io   Delete          Immediate           true                   3m41s
```

## Install Metallb

Next, we install Metallb LoadBalancer so that we can expose our services later
The following steps are performed during the installation

1. add_metallb_helm_repo,
1. update_helm_repo,
1. install_metallb_helm_chart,
1. add_namespace_labels,

```
k8s_admin_setup_utils metallb install helm-chart
```

After this, we need to configure MetalLb by creating `L2Advertisement` and `IPAddressPool` Custom Resources

```
k8s_admin_setup_utils metallb install custom-resources --help

 _______   _______    ______   _______    ______         __         ______            
/       \ /       \  /      \ /       \  /      \       /  |       /      \           
$$$$$$$  |$$$$$$$  |/$$$$$$  |$$$$$$$  |/$$$$$$  |      $$ |   __ /$$$$$$  |  _______ 
$$ |__$$ |$$ |__$$ |$$ |__$$ |$$ |  $$ |$$ |__$$ |      $$ |  /  |$$ \__$$ | /       |
$$    $$/ $$    $$< $$    $$ |$$ |  $$ |$$    $$ |      $$ |_/$$/ $$    $$< /$$$$$$$/ 
$$$$$$$/  $$$$$$$  |$$$$$$$$ |$$ |  $$ |$$$$$$$$ |      $$   $$<   $$$$$$  |$$      \ 
$$ |      $$ |  $$ |$$ |  $$ |$$ |__$$ |$$ |  $$ |      $$$$$$  \ $$ \__$$ | $$$$$$  |
$$ |      $$ |  $$ |$$ |  $$ |$$    $$/ $$ |  $$ |      $$ | $$  |$$    $$/ /     $$/ 
$$/       $$/   $$/ $$/   $$/ $$$$$$$/  $$/   $$/       $$/   $$/  $$$$$$/  $$$$$$$/ 


Usage: k8s_admin_setup_utils metallb install custom-resources 
           [OPTIONS]

  Configure MetalLB L2Advertisement and AddressPool Custom Resources

Options:
  --pool-name TEXT         Name of the pool to use for MetalLB
  --start-ip IPV4 ADDRESS  Start IP of the pool to use for MetalLB
  --end-ip IPV4 ADDRESS    End IP of the pool to use for MetalLB
  --help                   Show this message and exit
```

Make sure that the `start-ip` and `end-ip` are in the range of the network interface shared by all of your nodes. If you created the nodes via the `Vagrantfile` in this repo, you can use the default values.

```
k8s_admin_setup_utils metallb install custom-resources
```


You can monitor the events in the metallb namespace using

```
k8s_admin_setup_utils metallb watch
```

Once the events stabilise and all pods are up in the metallb namespace, the installation is complete.
