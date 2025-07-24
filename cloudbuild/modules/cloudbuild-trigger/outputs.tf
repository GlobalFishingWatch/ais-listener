output "trigger_id" {
  description = "Cloud Build trigger id"
  value       = google_cloudbuild_trigger.trigger.id
}