variable "cloudflare_zone_id" {
  type        = string
  description = "Cloudflare zone ID for jmyrberg.com."
  default     = "66c9f9bc5ea30bf426a8668d775cae5b"
}

variable "hostname" {
  type        = string
  description = "Hostname without protocol."
  default     = "jmyrberg.com"
}

variable "player_emails" {
  type        = list(string)
  description = "Emails allowed to access the player app."
  default     = []
}

variable "admin_emails" {
  type        = list(string)
  description = "Emails allowed to access the admin app."
}

variable "session_duration" {
  type        = string
  description = "How long users stay logged in."
  default     = "168h"
}
