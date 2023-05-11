provider "aws" {
  region = "${var.region}"
}

terraform {
  backend "s3" {
    bucket = "bucket-backend-terraform-caioruiz"
    key    = "backend-get-cart/terraform.tfstate"
    region = "sa-east-1"
  }
}