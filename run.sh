#!/bin/bash

##
## Run fishing_hours operation in test mode.  Should print a formatted query and exit
##

 docker compose run --rm pipeline \
  -v --test \
  --start_date=2016-01-01 \
  --end_date=2016-12-31 \
  --dest_fishing_hours_flag_table=world-fishing-827.scratch_public_ttl120.example_fishing_hours_by_flag \
  fishing_hours \
  --source_fishing_effort_table=global-fishing-watch.global_footprint_of_fisheries.fishing_effort \



##
## Run fishing_hours operation.  Should create/update the dest table in bigquery
##

#docker compose run --rm pipeline \
#  -v \
#  --dest_fishing_hours_flag_table=world-fishing-827.scratch_public_ttl120.example_fishing_hours_by_flag \
#  --start_date=2016-01-01 \
#  --end_date=2016-12-31 \
#  fishing_hours \
#  --source_fishing_effort_table=global-fishing-watch.global_footprint_of_fisheries.fishing_effort \
#  --table_description="Example table from pipe-python-prototype-template.  Ok to delete"

##
## Run the validation operation in test mode.  Should print a formatted query and exit
##

#docker compose run --rm pipeline \
#  --test \
#  --start_date=2016-01-01 \
#  --end_date=2016-12-31 \
#  --dest_fishing_hours_flag_table=world-fishing-827.scratch_public_ttl120.example_fishing_hours_by_flag \
#  validate \


##
## Run the validation operation.  Should indicate success if the fishing_hours table is present and populated with data
##

#docker compose run --rm pipeline \
#  --start_date=2016-01-01 \
#  --end_date=2016-12-31 \
#  --dest_fishing_hours_flag_table=world-fishing-827.scratch_public_ttl120.example_fishing_hours_by_flag \
#  validate