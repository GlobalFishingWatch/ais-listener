variable "basename" {
  type    = string
  default = "pipe-hourly-prototype"
}

variable "environment" {
  type    = string
  default = "test"
}

variable "blame" {
  type    = string
  default = "paul"
}

variable "resource_creator" {
  type    = string
  default = "paul"
}

variable "project" {
  type    = string
  default = "world-fishing-827"
}

variable "region" {
  type    = string
  default = "us-east1"
}

variable "gcs_temp_location" {
  type    = string
  default = "gs://pipe_nmea_temp_ttl3/"
}

variable "gfw_project_name" {
  type = string
  default = "pipe-hourly-prototype"
}

data "google_project" "project" {
}

data "google_storage_project_service_account" "gcs_account" {
}