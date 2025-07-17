locals {
  image_registry_url = "${var.registry_location}-docker.pkg.dev/${var.infra_project}/${var.registry_artifact}"
  service_account    = "projects/${var.infra_project}/serviceAccounts/cloudbuild@${var.infra_project}.iam.gserviceaccount.com"
}