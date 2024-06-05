provider "google" {
  project = var.project
  region  = var.region
  default_labels = {
    env = var.environment
    blame = var.blame
    resource_creator = var.resource_creator
    project = var.gfw_project_name
  }
}
