#!/usr/bin/env Rscript
#
# examples/r_meta_analysis_template.R
#
# ============================================================================
# VERIFICATION STATUS: NOT EXECUTED. R was not available in the
# environment this file was written in, so -- unlike every other
# example, script, and artifact in this repository -- this file's
# correctness has NOT been independently confirmed by actually running
# it. It is included because R is the dominant language for
# meta-analysis in biomedical research (metafor, meta packages) and a
# registry aimed at researchers should not be Python-only in its
# examples. Treat this as a reference starting point, not a verified
# tool: run it yourself, check the output against a small hand-checked
# subset, and open an issue or PR if anything here is wrong.
# ============================================================================
#
# Demonstrates loading the Dark Data Medicine dataset into R and
# preparing it for use with standard meta-analysis packages.
#
# Requires: install.packages(c("jsonlite", "dplyr", "purrr"))
# For actual meta-analysis on top of this: install.packages("metafor")

library(jsonlite)
library(dplyr)
library(purrr)

KNOWN_DOMAIN_DIRS <- c(
  "oncology", "neurology", "pharmacology", "cardiology",
  "psychiatry", "immunology", "infectious_disease", "endocrinology"
)

#' Load every JSON entry under data/<domain>/ into a single data.frame
load_entries <- function(data_dir = "data", domain_filter = NULL) {
  domain_dirs <- if (!is.null(domain_filter)) domain_filter else KNOWN_DOMAIN_DIRS

  rows <- map_dfr(domain_dirs, function(dd) {
    dir_path <- file.path(data_dir, dd)
    if (!dir.exists(dir_path)) return(NULL)

    files <- list.files(dir_path, pattern = "\\.json$", full.names = TRUE)
    map_dfr(files, function(f) {
      entry <- fromJSON(f, simplifyVector = TRUE)
      tibble(
        experiment_id        = entry$experiment_id,
        domain                = entry$domain,
        target_disease        = entry$target_disease,
        intervention_type     = entry$tested_intervention$type,
        intervention_name     = entry$tested_intervention$name,
        institution_type      = entry$institution_type,
        date_concluded         = entry$date_concluded,
        license                = entry$license,
        source_file            = f
      )
    })
  })

  rows
}

# --- Example usage ----------------------------------------------------

df <- load_entries("data")

cat(sprintf("Loaded %d entries\n\n", nrow(df)))

cat("=== Entries per domain ===\n")
print(df %>% count(domain, sort = TRUE))

cat("\n=== Entries per intervention type ===\n")
print(df %>% count(intervention_type, sort = TRUE))

# --- Evidentiary status reminder --------------------------------------
#
# As of this repository's v1.0.0 release, every entry loaded above is
# an illustrative seed example (see each entry's `keywords` field),
# not a curator-reviewed real-world submission. Do not feed this into
# metafor::rma() or any real meta-analytic model expecting genuine
# effect sizes -- there are none in the current dataset. See
# docs/FAQ.md and MANIFEST.md Section III for the project's own
# statement of its current evidentiary limits.
#
# Once entries carry the extended statistical fields proposed in the
# white paper's Part IV (sample_size, effect_size, confidence_interval,
# etc.), this script is the natural place to add a real
# metafor::rma() call, e.g.:
#
#   library(metafor)
#   res <- rma(yi = effect_size, sei = standard_error, data = df, method = "REML")
#   summary(res)
#   forest(res)
