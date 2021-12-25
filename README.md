# TubeHostingAttackNotifier

TubeHostingAttackNotifier is a Python project for reporting DDoS attacks on your tubehosting server to a Discord webhook.

## Dependencies
```bash
pip3 install datetime requests
```

## Installation

### Using Docker
* ! to run this script using Docker, you already need a Docker installation !

* keep this in mind, when you execute the following commands
   * replace "your@email.tld" with the mail address of your tube-hosting.com account
   * replace "your@Password123" with the password of your tube-hosting.com account
   * replace "https://discord.com/yourWebhookUrl" with the URL of your Discord webhook
   
```bash
git clone https://github.com/Lennart01/TubeHostingAttackNotifier

cd TubeHostingAttackNotifier

docker build -t thacknotir. 

docker run -d -e mail=your@email.tld -e passwd=your@Password123 -e url=https://discord.com/yourWebhookUrl thacknotir
```

Now you should have the script running in a Docker container 🎉

### Without Docker
```bash
git clone https://github.com/Lennart01/TubeHostingAttackNotifier

cd TubeHostingAttackNotifier

screen -S TubeHostingAttackNotifier python3 main.py
```
Enter your login credentials and Discord webhook when prompted.
press [ctrl + a]  [ctrl + d] to detach from the screen. 
