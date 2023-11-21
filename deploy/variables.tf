variable "prefix" {
  default = "patchbay"
}

variable "project" {
  default = "patchbay-app-api-devops"
}

variable "contact" {
  default = "knavyada@gmail.com"
}

variable "db_username" {
  description = "Username for the RDS Postgres instance"
}

variable "db_password" {
  description = "Password for the RDS postgres instance"
}

variable "bastion_key_name" {
  default = "patchbay-app-api-devops-bastion"
}
