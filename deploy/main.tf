terraform {
  backend "s3" {
    bucket         = "patchbay-app-api-devops-tfstate"
    key            = "patchbay-app.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "patchbay-app-api-devops-tf-state-lock"
  }
}

provider "aws" {
  region = "us-east-1"
  version = "~> 2.50.0"
}
