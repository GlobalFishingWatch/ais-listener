resource "google_cloudbuild_trigger" "trigger" {
  name        = "${var.repo_name}-${var.trigger_suffix}"
  location    = var.trigger_location
  description = var.trigger_description
  project     = var.infra_project

  github {
    name  = var.repo_name
    owner = var.repo_owner

    push {
      branch       = var.branch
      tag          = var.tag
      invert_regex = var.invert_regex
    }
  }

  service_account = local.service_account

  substitutions = {
    _IMAGE_NAME = "${local.image_registry_url}/${var.repo_name}"
  }

  build {
    step {
      id   = "docker build"
      name = "gcr.io/cloud-builders/docker"
      args = [
        "build",
        "-t", "$$_IMAGE_NAME:$$TAG_NAME",
        "-f", "Dockerfile",
        "--target", "prod",
        "."
      ]
    }
    step {
      id   = "docker push tag"
      name = "gcr.io/cloud-builders/docker"
      args = [
        "push", "$$_IMAGE_NAME:$$TAG_NAME"
      ]
    }

    images = [
      "$$_IMAGE_NAME:$$TAG_NAME",
    ]

    timeout = "600s"

    options {
      logging                = "CLOUD_LOGGING_ONLY"
      dynamic_substitutions  = true
    }
  }
}