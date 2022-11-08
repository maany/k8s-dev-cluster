# Kubernetes Admin Setup Utils
This is a python cli application to confiure Metallb, Traefik, Longhorn, Kube Prometheus Stack, Certmanager and letsencrypt certificates etc. for the Vagrant cluster

# Requirements
1. python3
2. helm3
3. kubectl

Good to have:
1. k9s/ Lens
1. cilium CLI


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
This command will install `cilium`, `hubble`
```
k8s_admin_setup_utils dev-cluster cilium install
```
## port forward 
## Reload coredns and metrics server
This is required for the coredns and metrics server pods to be assigned an IP address in the network range managed by `cilium`

```
k8s_admin_setup_utils dev-cluster reload
```