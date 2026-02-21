terraform {
  required_providers {
    kind = {
      source = "tehcyx/kind"
      version = "0.7.0"
    }
    kubernetes = {
      source = "hashicorp/kubernetes"
      version = "2.35.1"
    }
  }
}
