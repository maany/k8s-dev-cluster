VAGRANT_EXPERIMENTAL="disks"
NUM_INFRA_NODES=2 # nodes with label "role=infra"
NUM_WORKER_NODES=2 # nodes with label "role=worker"
NUM_STORAGE_NODES=1 # nodes with label "role=storage"
IP_NW="172.16.16."
IP_START=10

Vagrant.configure("2") do |config|
  config.vm.provision "shell", env: {"IP_NW" => IP_NW, "IP_START" => IP_START, "NUM_INFRA_NODES" => NUM_INFRA_NODES , "NUM_WORKER_NODES" => NUM_WORKER_NODES, "NUM_STORAGE_NODES" => NUM_STORAGE_NODES}, inline: <<-SHELL
      apt-get update -y
      echo "$IP_NW$((IP_START)) master-node" >> /etc/hosts
      for i in $(seq 1 $NUM_INFRA_NODES); do
        echo "$IP_NW$((IP_START+i)) infra-node${i}" >> /etc/hosts
      done
      for i in $(seq 1 $NUM_STORAGE_NODES); do
        echo "$IP_NW$((IP_START+NUM_INFRA_NODES+i)) storage-node${i}" >> /etc/hosts
      done
      for i in $(seq 1 $NUM_WORKER_NODES); do
        echo "$IP_NW$((IP_START+NUM_INFRA_NODES+NUM_STORAGE_NODES+i)) storage-node${i}" >> /etc/hosts
      done
  SHELL

  config.vm.box = "bento/ubuntu-22.04"
  config.vm.box_check_update = true

  config.vm.define "master" do |master|
    # master.vm.box = "bento/ubuntu-18.04"
    master.vm.hostname = "master-node"
    master.vm.network "private_network", ip: IP_NW + "#{IP_START}"
    master.vm.provider "virtualbox" do |vb|
        vb.memory = 4096
        vb.cpus = 2
    end
    master.vm.provision "shell", path: "scripts/common.sh"
    master.vm.provision "shell", path: "scripts/master.sh"
  end

  (1..NUM_INFRA_NODES).each do |i|

    config.vm.define "infra#{i}" do |node|
      node.vm.hostname = "infra-node#{i}"
      node.vm.network "private_network", ip: IP_NW + "#{IP_START + i}"
      node.vm.provider "virtualbox" do |vb|
          vb.memory = 4096
          vb.cpus = 2
      end
      node.vm.provision "shell", path: "scripts/common.sh"
      node.vm.provision "shell", path: "scripts/infra.sh"
    end
  end

  (1..NUM_STORAGE_NODES).each do |i|
    config.vm.define "storage#{i}" do |node|
      node.vm.hostname = "storage-node#{i}"
      node.vm.network "private_network", ip: IP_NW + "#{IP_START + NUM_INFRA_NODES + i}"
      node.vm.disk :disk, size: "5GB", primary: true, name: "storage#{i}"
      # node.vm.disksize.size = '5GB'
      node.vm.provider "virtualbox" do |vb|
        vb.memory = 4096
        vb.cpus = 2
      end
      node.vm.provision "shell", path: "scripts/common.sh"
      node.vm.provision "shell", path: "scripts/storage.sh"
    end
  end

  (1..NUM_WORKER_NODES).each do |i|
    config.vm.define "worker#{i}" do |node|
      node.vm.hostname = "worker-node#{i}"
      node.vm.network "private_network", ip: IP_NW + "#{IP_START + NUM_INFRA_NODES + NUM_STORAGE_NODES + i}"
      node.vm.provider "virtualbox" do |vb|
        vb.memory = 4096
        vb.cpus = 2
      end
      node.vm.provision "shell", path: "scripts/common.sh"
      node.vm.provision "shell", path: "scripts/worker.sh"
    end
  end    
end 
