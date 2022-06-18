# TubeHostingAttackNotifier
TubeHostingAttackNotifier is a Python project for reporting DDoS attacks on your [Tube-Hosing.com](https://tube-hosting.com) server to a Discord webhook.

## Installation

### Without Docker

```bash
pip3 install datetime requests

git clone https://github.com/Lennart01/TubeHostingAttackNotifier

cd TubeHostingAttackNotifier

screen -S TubeHostingAttackNotifier python3 main.py
```
Enter your login credentials and Discord webhook when prompted.
press [ctrl + a]  [ctrl + d] to detach from the screen. 

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

docker run -d --name TubeHostingAttackNotifier -e mail=your@email.tld -e passwd=your@Password123 -e url=https://discord.com/yourWebhookUrl -e ips=ip1,ip2,ip3,ip4 thacknoti
```

Now you should have the script running in a Docker container 🎉
