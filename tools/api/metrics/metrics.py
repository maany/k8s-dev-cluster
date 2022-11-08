from api.core.base_configuration import BaseConfiguration


class InstallKubePrometheusStack(BaseConfiguration):
    def __init__(self, kubeconfig: str, values: str):
        super().__init__()
        self.kubeconfig = kubeconfig
        self.values = values

        self.steps = [

        ]



class UninstallKubePrometheusStack(BaseConfiguration):
    def __init__(self, kubeconfig: str):
        super().__init__()
        self.kubeconfig = kubeconfig

        self.steps = [

        ]