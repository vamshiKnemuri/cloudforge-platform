variable "name" {
  type = string
}

variable "kubernetes_version" {
  type = string
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "public_access_cidrs" {
  type = list(string)
}

variable "node_instance_types" {
  type = list(string)
}

variable "node_desired_size" {
  type = number
}
