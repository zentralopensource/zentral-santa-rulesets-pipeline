# Jenkins test deployment

## Jenkins via `docker compose`

Use docker compose.

Start with:

```
docker compose up -d
```

Access the instance: [http://localhost:8080](http://localhost:8080).

To get the admin password:

```
docker compose exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Install suggested plugins

Create First Admin User

Set the hostname. For the hostname, and to make the container accessible from the outside, we will use a Cloudflare tunnel.

## Cloudflare Tunnel

See [Cloudflare documentation](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/tunnel-guide).

In order to make the test instance accessible from the outside, we will use cloudflared.

```
brew install cloudflare/cloudflare/cloudflared
```

Login

```
cloudflared tunnel login
```

Tunnel credentials will be saved in `$HOME/.cloudflared/cert.pem`

```
cloudflared tunnel create username-usermachine-dev
```

Tunnel will be created, write down the UUID. The credentials will be saved in `$HOME/.cloudflared/$TUNNEL_UUID.json`

Verify the new tunnel is there:

```
cloudflared tunnel list
```

Create a `cf_tunnel_config.yml` based on `cf_tunnel_config.example.yml`.

Route the traffic to the hostname used in the config:

```
cloudflared tunnel route dns $TUNNEL_UUID $HOSTNAME
```

Run the tunnel

```
cloudflared tunnel --config cf_tunnel_config.yml run
```

Delete the admin credentials if necessary

```
rm "$HOME/.cloudflared/cert.pem"
```

## Github app

Create the app.
See [docs](https://docs.cloudbees.com/docs/cloudbees-ci/latest/cloud-admin-guide/github-app-auth#_creating_the_github_app) & [video](https://www.youtube.com/watch?v=aDmeeVDrp0o).

URL:

```https://$HOSTNAME```

Webhooks URL:

```https://$HOSTNAME/github-webhook/```

Permissions:

* **Administration**: Read-only
* **Contents**: Read-only (to read the Jenkinsfile and the repository content during git fetch).
* **Metadata**: Read-only
* **Pull requests**: Read-only
* **Commit statuses**: Read & write

Subscribe to events:

* Check run
* Check suite
* Pull request
* Push
* Repository


Generate a private key for the app, download it, convert it.

```
openssl pkcs8 -topk8 -inform PEM -outform PEM \
        -in key-in-your-downloads-folder.pem \
        -out converted-github-app.pem \
        -nocrypt
```

Install the app in the org. (Transfer the app ownership to the org before if needed). Restrict it to some repositories.

Create Jenkins credentials using the converted private key. Test the credentials.

## Jenkins Job

Dashboard, New multibranch pipeline, GitHub branch discovery, select the credentials, add https repository URL, scan, save.

Add Zentral API token as secret txt credentials for this job, with `zentral-api-token` as ID.