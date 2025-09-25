package main

import (
	"bufio"
	"fmt"
	"os"
	"strings"
	"time"

	"tubehosting-attack-notifier/internal/discord"
	"tubehosting-attack-notifier/internal/tubehosting"
)

func main() {
	email := os.Getenv("mail")
	password := os.Getenv("passwd")
	webhookURL := os.Getenv("url")
	ipListStr := os.Getenv("ips")
	var ipList []string

	if ipListStr != "" {
		ipList = strings.Split(ipListStr, ",")
	}

	reader := bufio.NewReader(os.Stdin)

	if email == "" {
		fmt.Print("Enter your email: ")
		email, _ = reader.ReadString('\n')
		email = strings.TrimSpace(email)
	}

	if password == "" {
		fmt.Print("Enter your password: ")
		password, _ = reader.ReadString('\n')
		password = strings.TrimSpace(password)
	}

	if webhookURL == "" {
		fmt.Print("Enter your Webhook: ")
		webhookURL, _ = reader.ReadString('\n')
		webhookURL = strings.TrimSpace(webhookURL)
	}

	if len(ipList) == 0 {
		fmt.Println("Please enter the IPs to monitor.")
		fmt.Println("Only enter one IP at a time.")
		fmt.Println("Simply press enter once you are done.")
		for {
			fmt.Print("ip: ")
			ip, _ := reader.ReadString('\n')
			ip = strings.TrimSpace(ip)
			if ip == "" {
				break
			}
			ipList = append(ipList, ip)
		}
	}

	// Validate input
	authToken, err := tubehosting.GetAuthToken(email, password)
	if err != nil {
		fmt.Println("Wrong login data")
		fmt.Println("Shutting down")
		time.Sleep(5 * time.Second)
		os.Exit(1)
	}

	err = discord.SendTest(webhookURL)
	if err != nil {
		fmt.Println("Webhook is incorrect")
		fmt.Println("Shutting down")
		time.Sleep(5 * time.Second)
		os.Exit(1)
	}

	fmt.Println("script started successfully")

	lastAttackTimes, err := tubehosting.GetLastAttackTimestamp(authToken, ipList)
	if err != nil {
		fmt.Printf("Error getting initial last attack timestamp: %v\n", err)
		// Decide if we should exit or continue with zero values
	}

	controller(email, password, webhookURL, ipList, lastAttackTimes)
}

func controller(email, password, webhookURL string, ipList []string, lastAttackTimes map[string]time.Time) {
	for {
		// Get auth_token from api
		authToken, err := tubehosting.GetAuthToken(email, password)
		if err != nil {
			fmt.Printf("Error getting auth token: %v\n", err)
			time.Sleep(20 * time.Second)
			continue
		}

		// Check for attacks
		newAttacks, updatedAttackTimes, err := tubehosting.CheckForNewAttacks(authToken, ipList, lastAttackTimes)
		if err != nil {
			fmt.Printf("Error checking for attacks: %v\n", err)
		} else {
			lastAttackTimes = updatedAttackTimes
			for _, attack := range newAttacks {
				fmt.Printf("New attack detected: %v\n", attack)
				discord.Send(webhookURL, attack)
			}
		}

		// sleeping the process for 20 seconds
		time.Sleep(20 * time.Second)
	}
}