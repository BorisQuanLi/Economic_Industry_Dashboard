resource "google_firestore_database" "database" {
  project     = "superhost_api_gateway"
  name        = "(default)"
  location_id = "us-east1"
  type        = "FIRESTORE_NATIVE"
}

