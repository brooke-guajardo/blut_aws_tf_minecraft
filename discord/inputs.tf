data "terraform_remote_state" "local_ecs" {
    backend = "local"
        config = {
            path = "../ecs/terraform.tfstate"
        }
}