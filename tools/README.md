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
We use Longhorn for provisioning PersistentVolumes within the cluster. The `storage` nodes have a label `k8s.prada.io/role: storage` and that's where most of the longhorn reources will be provisioned.

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

## Install Kube Prometheus Stack
To enable cluster monitoring, run

```
k8s_admin_setup_utils monitoring install --help

 _______   _______    ______   _______    ______         __         ______            
/       \ /       \  /      \ /       \  /      \       /  |       /      \           
$$$$$$$  |$$$$$$$  |/$$$$$$  |$$$$$$$  |/$$$$$$  |      $$ |   __ /$$$$$$  |  _______ 
$$ |__$$ |$$ |__$$ |$$ |__$$ |$$ |  $$ |$$ |__$$ |      $$ |  /  |$$ \__$$ | /       |
$$    $$/ $$    $$< $$    $$ |$$ |  $$ |$$    $$ |      $$ |_/$$/ $$    $$< /$$$$$$$/ 
$$$$$$$/  $$$$$$$  |$$$$$$$$ |$$ |  $$ |$$$$$$$$ |      $$   $$<   $$$$$$  |$$      \ 
$$ |      $$ |  $$ |$$ |  $$ |$$ |__$$ |$$ |  $$ |      $$$$$$  \ $$ \__$$ | $$$$$$  |
$$ |      $$ |  $$ |$$ |  $$ |$$    $$/ $$ |  $$ |      $$ | $$  |$$    $$/ /     $$/ 
$$/       $$/   $$/ $$/   $$/ $$$$$$$/  $$/   $$/       $$/   $$/  $$$$$$/  $$$$$$$/ 


Usage: k8s_admin_setup_utils monitoring install [OPTIONS]

  Install Kube Prometheus Stack

Options:
  --kube-prometheus-values, --values PATH
                                  Path to Kube Prometheus Stack Helm values
                                  file
  --control-plane-nodes, --control-plane IPV4 ADDRESS
                                  Control Plane Node Names  [required]
  -u, --grafana-user TEXT         Grafana User Name
  -p, --grafana-password TEXT     Grafana Password
  --help                          Show this message and exit.
```

You can specify the `username` and `password` for `grafana` via the CLI.
Please also specify the IPv4 address of the master node ( 172.16.16.10 ) to update the `endpoints` for etcd, kube-controller-manager, kube-scheduler and kube-api-server.

```
k8s_admin_setup_utils monitoring install -u admin --control-plane-nodes 172.16.16.10
```
You will be prompted to enter a password, which will be used to create a secret in step 2 of the 3 steps executed by this command:
1. create_namespace,
1. create_grafana_secret,
1. install_helm_repo

Once installation completes, you will start seeing metrics in `Lens`.

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

## Install Traefik

Install the helm chart

```
k8s_admin_setup_utils traefik install helm-chart
```

Install the default headers for http middleware

```
k8s_admin_setup_utils traefik install default-headers
```

Next, we need to create a `dashboard_secret`, `basic_auth_middleware` that references to this secret and a `IngressRoute` that defines the HostName that points to the traefik dashboard.

The list of steps is:
1. install_traefik_dashboard_secret,
1. install_traefik_dashboard_basic_auth_middleware,
1. install_traefik_dashboard_ingress_route,
1. add_dashboard_hostname_to_hosts_file,

**NOTE** the `/et/hosts` file on your machine will be modified

```
k8s_admin_setup_utils traefik install dashboard -h devmaany.com
```

## Configure Longhorn backups

## Configure Exposing to Internet