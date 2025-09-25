# TubeHostingAttackNotifier-Go

TubeHostingAttackNotifier-Go is a Go project for reporting DDoS attacks on your [Tube-Hosting.com](https://tube-hosting.com) server to a Discord webhook. This is a rewrite of the original Python project.

## Installation

### Using Docker
* ! to run this script using Docker, you already need a Docker installation !

* keep this in mind, when you execute the following commands
   * replace "your@email.tld" with the mail address of your tube-hosting.com account
   * replace "your@Password123" with the password of your tube-hosting.com account
   * replace "https://discord.com/yourWebhookUrl" with the URL of your Discord webhook
   * replace "ip1,ip2,ip3,ip4" with the IP addresses of your tube-hosting.com server
   
```bash
git clone https://github.com/Lennart01/TubeHostingAttackNotifier

cd TubeHostingAttackNotifier

docker build -t thacknoti . 

docker run -d --restart unless-stopped --name TubeHostingAttackNotifier -e mail=your@email.tld -e passwd=your@Password123 -e url=https://discord.com/yourWebhookUrl -e ips=ip1,ip2,ip3,ip4 thacknoti
```

Now you should have the script running in a Docker container 🎉

## Updating
```bash
cd TubeHostingAttackNotifier
git pull
docker build -t thacknoti .
# You will need to stop and remove the old container before running a new one
docker stop TubeHostingAttackNotifier
docker rm TubeHostingAttackNotifier
# Then run the docker run command again
```