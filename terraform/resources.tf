# This code is compatible with Terraform 4.25.0 and versions that are backwards compatible to 4.25.0.
# For information about validating this Terraform code, see https://developer.hashicorp.com/terraform/tutorials/gcp-get-started/google-cloud-platform-build#format-and-validate-the-configuration

resource "google_compute_instance" "ais-listener-dev-20240602-223403" {
  boot_disk {
    auto_delete = true
    device_name = "ais-listener-dev"

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

  labels = {
    container-vm = "cos-stable-101-17162-40-20"
    environment  = "dev"
    goog-ec-src  = "vm_add-tf"
    responsible  = "paul"
  }

  machine_type = "e2-medium"

  metadata = {
    gce-container-declaration = "spec:\n  containers:\n  - name: ais-listener-dev-20240602-223403\n    image: gcr.io/world-fishing-827/github.com/globalfishingwatch/ais-listener:latest\n    args:\n    - -v\n    - server\n    - --udp-port-range\n    - '10110'\n    - '10119'\n    - --source-port-map=gs://gfw-raw-data-ais/ais-listener/ais-listener-source-port-map.yaml\n    - --gcs-dir=gs://gfw-raw-data-ais/ais-listener/udp/\n    stdin: false\n    tty: false\n  restartPolicy: Always\n# This container declaration format is not public API and may change without notice. Please\n# use gcloud command-line tool or Google Cloud Console to run Containers on Google Compute Engine."
  }

  name = "ais-listener-dev-20240602-223403"

  network_interface {
    access_config {
      network_tier = "STANDARD"
    }

    network     = "projects/skytruth-pelagos-production/global/networks/default"
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
    scopes = ["https://www.googleapis.com/auth/devstorage.read_write", "https://www.googleapis.com/auth/logging.write", "https://www.googleapis.com/auth/monitoring.write", "https://www.googleapis.com/auth/service.management.readonly", "https://www.googleapis.com/auth/servicecontrol", "https://www.googleapis.com/auth/trace.append"]
  }

  shielded_instance_config {
    enable_integrity_monitoring = true
    enable_secure_boot          = false
    enable_vtpm                 = true
  }

  tags = ["nmea-udp-server"]
  zone = "us-central1-f"
}
