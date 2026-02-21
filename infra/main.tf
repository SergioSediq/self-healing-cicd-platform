provider "kind" {}

resource "kind_cluster" "default" {
  name           = "self-healing-cluster"
  node_image     = "kindest/node:v1.27.3" # Pinned for stability
  wait_for_ready = true
}

provider "kubernetes" {
  host                   = kind_cluster.default.endpoint
  client_certificate     = kind_cluster.default.client_certificate
  client_key             = kind_cluster.default.client_key
  cluster_ca_certificate = kind_cluster.default.cluster_ca_certificate
}

resource "kubernetes_namespace" "target_ns" {
  metadata {
    name = "autopilot-target"
  }
}
