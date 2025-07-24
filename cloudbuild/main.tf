module "trigger_push_to_prod_tag" {
  source              = "./modules/cloudbuild-trigger"
  trigger_suffix      = "push-to-tag"
  trigger_description = "A docker image is published every time a tag is created."
  repo_name           = "ais-listener"
  tag                 = ".*"
  registry_artifact   = "pipeline-core"
}