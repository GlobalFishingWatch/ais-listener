# This code is compatible with Terraform 4.25.0 and versions that are backwards compatible to 4.25.0.
# For information about validating this Terraform code, see https://developer.hashicorp.com/terraform/tutorials/gcp-get-started/google-cloud-platform-build#format-and-validate-the-configuration

resource "google_compute_instance" "ais-listener-dev-2" {
  name = "ais-listener-dev-2"

  labels = {
    container-vm = "cos-stable-101-17162-40-20"
    environment  = var.environment
    goog-ec-src  = "vm_add-tf"
    responsible  = var.resource_creator
  }

  tags = ["nmea-udp-server"]
  zone = var.zone

  boot_disk {
    auto_delete = true
    device_name = "ais-listener-dev-2"

    initialize_params {
      image = "projects/cos-cloud/global/images/cos-stable-101-17162-40-20"
      size  = 50
      type  = "pd-balanced"
    }

    mode = "READ_WRITE"
  }

  can_ip_forward      = false
  deletion_protection = false
  enable_display      = false

  machine_type = "e2-medium"

  metadata = {
    gce-container-declaration = <<EOH
spec:
  containers:
    -
      name: ais-listener-dev-2
      image: gcr.io/world-fishing-827/github.com/globalfishingwatch/ais-listener/dev:latest
      args:
        - -v
        - receiver
        - --config_file=gs://gfw-raw-data-ais/ais-listener/ais-listener-sources.yaml
        - --gcs-dir=gs://scratch-paul-ttl100/ais-listener-dev2/
        - --shard-interval=60
      stdin: false
      tty: false
      restartPolicy: Always
EOH
  }

  network_interface {
    access_config {
      network_tier = "STANDARD"
    }

    network     = "projects/${var.project}/global/networks/default"
    queue_count = 0
    stack_type  = "IPV4_ONLY"
  }

  scheduling {
    automatic_restart   = true
    on_host_maintenance = "MIGRATE"
    preemptible         = false
    provisioning_model  = "STANDARD"
  }

  service_account {
    email  = "896869274290-compute@developer.gserviceaccount.com"
    scopes = [
      "https://www.googleapis.com/auth/devstorage.read_write",
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring.write",
      "https://www.googleapis.com/auth/service.management.readonly",
      "https://www.googleapis.com/auth/servicecontrol",
      "https://www.googleapis.com/auth/trace.append"
    ]
  }

  shielded_instance_config {
    enable_integrity_monitoring = true
    enable_secure_boot          = false
    enable_vtpm                 = true
  }
}
