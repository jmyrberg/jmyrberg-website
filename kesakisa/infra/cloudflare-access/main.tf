terraform {
  required_version = ">= 1.6.0"

  required_providers {
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 5.19"
    }
  }
}

provider "cloudflare" {}

locals {
  player_access_emails = distinct(concat(var.player_emails, var.admin_emails))

  access_apps = {
    player_root = {
      name        = "Kesakisa 2026"
      domain      = "${var.hostname}/kesakisa"
      policy_name = "Kesakisa 2026 osallistujat"
      emails      = local.player_access_emails
    }
    player_wildcard = {
      name        = "Kesakisa 2026 polut"
      domain      = "${var.hostname}/kesakisa/*"
      policy_name = "Kesakisa 2026 osallistujat"
      emails      = local.player_access_emails
    }
    admin_root = {
      name        = "Kesakisa 2026 jarjestaja"
      domain      = "${var.hostname}/kesakisa/admin"
      policy_name = "Kesakisa 2026 jarjestajat"
      emails      = var.admin_emails
    }
    admin_wildcard = {
      name        = "Kesakisa 2026 jarjestaja polut"
      domain      = "${var.hostname}/kesakisa/admin/*"
      policy_name = "Kesakisa 2026 jarjestajat"
      emails      = var.admin_emails
    }
  }
}

resource "cloudflare_zero_trust_access_application" "kesakisa" {
  for_each = local.access_apps

  zone_id              = var.cloudflare_zone_id
  name                 = each.value.name
  domain               = each.value.domain
  type                 = "self_hosted"
  session_duration     = var.session_duration
  app_launcher_visible = false

  policies = [{
    name       = each.value.policy_name
    decision   = "allow"
    precedence = 1

    include = [
      for email in each.value.emails : {
        email = {
          email = email
        }
      }
    ]
  }]
}
