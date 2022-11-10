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

There is a bug in the metallb helm charts, for which I have a pending PR
https://github.com/metallb/metallb/issues/1694 

If the PR is merged, you can use the command below to go through metallb installation

```
k8s_admin_setup_utils metallb install helm-chart
```

Otherwise, you need to install metallb manually. Assumin you are in the root folder of this repo,

```
git clone https://github.com/maany/metallb 
cd metallb/charts/metallb
helm install metallb . --create-namespace -n metallb-system --values ../../../tools/config/metallb-values.yaml
kubectl label namespace metallb-system pod-security.kubernetes.io/enforce=privileged pod-security.kubernetes.io/audit=privileged pod-security.kubernetes.io/warn=privileged
cd ../../../
rm -rf metallb
```

Wait for the Metallb Controller and Speaker Pods to become available

Once the pods are available, we need to configure MetalLb by creating `L2Advertisement` and `IPAddressPool` Custom Resources

```
k8s_admin_setup_utils metallb install custom-resources --help

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

Next, we need to create a `dashboard_secret`, `basic_auth_middleware` that references to this secret and a `IngressRoute` that defines the HostName that would resolve to the traefik dashboard. The `IngressRoute` will also apply the `basic_auth_middleware` to the traefik dashboard. The `ingress controller` will register this ingress route.

The list of steps is:
1. install_traefik_dashboard_secret,
1. install_traefik_dashboard_basic_auth_middleware,
1. install_traefik_dashboard_ingress_route,
1. add_dashboard_hostname_to_hosts_file,

**NOTE** the `/etc/hosts` file on your machine will be modified

```
k8s_admin_setup_utils traefik install dashboard -h traefik.devmaany.com -u maany
```

At this point, you can visit the `Traefik Dashboard` at the IP address to which TraefikService has been exposed to. You can find out the IP by running

```
k8s_admin_setup_utils traefik loadbalancer-ip
```

You can also access the dashboard by visitng the `hostname` specified during the install command.

## Install CertManager

If you visit the traefik dashboard, you will see that the certificate common name is "TRAEFIK DEFAULT CERT". Let's change that

Install the cert-manager helm chart by running

```
k8s_admin_setup_utils certmanager install helm-chart
```

### I have a backup of my certificates from a previous cluster

To restore your certificates, clusterissuer and secrets, run 

```
k8s_admin_setup_utils certmanager restore --dir /path/to/certmanager/backup
```

and then make sure that you have configured the restored secret `letsencrypt-production` or `letsencrypt-staging` and the `Certificate` resource in the `TLSStore` resource for `Traefik`



### I want to issue new certificates

We need to define `ClusterIssuer` and `Certificate` custom resources.

The `ClusterIssues` is a k8s wrapper around a Certificate Authority, which in our case is letsencrypt. 

The `ClusterIssuer` will use a `DNS-01` ACME Challenge to verify that you own the domain for which the certificate is being requested. Since the domain is managed by Cloudflare, the verification i.e. solving the ACME challenge can be automated. For this, we need to authorize the solver to be able to access information in our Cloudflare account and validate that we own the domain.

For the successful competion of ACME challenges we need to provide the an Access Token from Cloudflare.

To create a new token, login to your Cloudflare dashboard and

```
- Select Domain
- Click `Get your API token` link
- Click `Create Token`
- Click `Use Template` next to `Edit Zone DNS`
- In `Permissions` select the following
    - `Zone` - `DNS` - `Edit`
    - `Zone` - `Zone` - `Read`
- In `Zone Resources` select `All Zones`
- Enter a `Start Date` and `End Date`
- Click `Contine to summary`

- Review the details
- Click `Create Token`
- Click the `Copy` button to get your token and confirm it is working using the `curl` command provided on that screen,
```

Once you have the token, run the following command to 
1. create a secret that will store your cloudflare token
2. create a ClusterIssuer resource that will point to letsencrypt and also store information related to our Cloudflare account, which will be used to solve the DNS01 Challenges.

**NOTE** For testing backup and restore, use the staging environment

```
k8s_admin_setup_utils certmanager install cluster-issuer \
  --email imptodefeat@gmail.com
  --cloudflare-api-token <your_cloudflare_token> \
  --domain devmaany.com
  --letsencrypt-environment staging
```

Now we can create a `Certificate` resource. This resource will trigger the ACME challenge and solve the DNS01 challenge with the configured Cloudflare credentials. 

Once complete successfully, it will create a secret called `*-tls` in the specified namespace. This secret will contain `tls.key` and `tls.cert` keys which are the actual x509 certificates that will be used by the web services.

```
k8s_admin_setup_utils certmanager install certificate --namespace default --email imptodefeat@gmail.com --domain devmaany.com --letsencrypt-environment staging 
```
To monitor the progress and status, you can use k8s or Lens to:
1. Watch the `cert-manager` namespace for logs in the `Pods`
2. Watch the `kubectl get challenges` command in the namespace where the Certificate will be created
3. Watch the `kubectl get certificate` command in the namespace where the Certificate will be created


Verify that the certificate has been issued by running

```
kubectl get secret
```


### Backup letsencrypt certificates
In order to backup the certificates, clusterissuer and secrets, run 

```
k8s_admin_setup_utils certmanager backup -e staging --dir /path/to/certmanager/backup -n default
```


## Configure default certificate for traefik

Get the secret name for the certificate that was created in the previous step. Its name ends with `-tls`

```
kubectl get secret -n default
```

Then create a default tls store for traefik using that secret name

```
k8s_admin_setup_utils traefik install default-tls-store --cert-secret-name <secret-name>
```

## Expose web services and dashboards

Now we will create IngressRoutes for 
1. Grafana
1. Hubble UI (for cilium)
1. Longhorn Frontend

The command is:
```
Usage: k8s_admin_setup_utils traefik create-ingress-routes 
           [OPTIONS]

  Create IngressRoute for a Service

Options:
  -s, --service TEXT  Service to expose in the format
                      {namespace}/{service_name}:{port}  [required]
  --domain TEXT       Domain for TLS Cert. Ex: devmaany.com  [required]
  --help              Show this message and exit.
```

You can run it with the following options

```
k8s_admin_setup_utils traefik create-ingress-routes \
  -s monitoring/grafana:80 \
  -s kube-system/hubble-ui:80 \
  -s longhorn-system/longhorn-frontend:80 \
  --domain devmaany.com
```
```
## Configure Longhorn backups


## Configure Exposing to Internet