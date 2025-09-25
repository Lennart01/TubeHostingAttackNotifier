package discord

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"strconv"
	"strings"
	"tubehosting-attack-notifier/internal/tubehosting"
)

// Webhook for sending messages to discord
type Webhook struct {
	Content   string        `json:"content"`
	Embeds    []Embed       `json:"embeds"`
	Username  string        `json:"username"`
	AvatarURL string        `json:"avatar_url"`
	TTS       bool          `json:"tts"`
	File      string        `json:"file"`
	Payload   string        `json:"payload_json"`
	Allowed   Allowed       `json:"allowed_mentions"`
	MessageID string        `json:"message_id"`
	ChannelID string        `json:"channel_id"`
	Flags     int           `json:"flags"`
	Thread    Thread        `json:"thread_name"`
	Components []Component `json:"components"`
}

// Thread struct for webhook
type Thread struct {
	Name string `json:"thread_name"`
}

// Component for webhook
type Component struct {
	Type       int         `json:"type"`
	Style      int         `json:"style"`
	Label      string      `json:"label"`
	CustomID   string      `json:"custom_id"`
	URL        string      `json:"url"`
	Disabled   bool        `json:"disabled"`
	Components []Component `json:"components"`
}

// Allowed mentions for webhook
type Allowed struct {
	Parse []string `json:"parse"`
	Users []string `json:"users"`
	Roles []string `json:"roles"`
}

// Embed for webhook
type Embed struct {
	Title       string        `json:"title"`
	Description string        `json:"description"`
	URL         string        `json:"url"`
	Timestamp   string        `json:"timestamp"`
	Color       int           `json:"color"`
	Footer      Footer        `json:"footer"`
	Image       Image         `json:"image"`
	Thumbnail   Thumbnail     `json:"thumbnail"`
	Video       Video         `json:"video"`
	Provider    Provider      `json:"provider"`
	Author      Author        `json:"author"`
	Fields      []EmbedFields `json:"fields"`
}

// EmbedFields for webhook
type EmbedFields struct {
	Name   string `json:"name"`
	Value  string `json:"value"`
	Inline bool   `json:"inline"`
}

// Author for webhook
type Author struct {
	Name    string `json:"name"`
	URL     string `json:"url"`
	IconURL string `json:"icon_url"`
}

// Provider for webhook
type Provider struct {
	Name string `json:"name"`
	URL  string `json:"url"`
}

// Video for webhook
type Video struct {
	URL string `json:"url"`
}

// Thumbnail for webhook
type Thumbnail struct {
	URL string `json:"url"`
}

// Image for webhook
type Image struct {
	URL string `json:"url"`
}

// Footer for webhook
type Footer struct {
	Text    string `json:"text"`
	IconURL string `json:"icon_url"`
}

func prtIDToPrt(protocolID int) string {
	switch protocolID {
	case 1:
		return "ICMP"
	case 6:
		return "TCP"
	case 17:
		return "UDP"
	default:
		return strconv.Itoa(protocolID) + " (id)"
	}
}

func decSep(rawNumber string) string {
	n, err := strconv.ParseInt(rawNumber, 10, 64)
	if err != nil {
		return rawNumber
	}
	in := strconv.FormatInt(n, 10)
	out := make([]byte, len(in)+(len(in)-1)/3)
	if in[0] == '-' {
		in = in[1:]
		out[0] = '-'
	}

	for i, j, k := len(in)-1, len(out)-1, 0; ; i, j = i-1, j-1 {
		out[j] = in[i]
		if i == 0 {
			return string(out)
		}
		if k++; k == 3 {
			j, k = j-1, 0
			out[j] = '.'
		}
	}
}

// Send sends the webhook
func Send(webhookURL string, message tubehosting.Attack) {
	var bandwidth string
	if message.Traffic < 10000 {
		bandwidth = fmt.Sprintf("%s Mbit/s", decSep(fmt.Sprintf("%.0f", message.Traffic)))
	} else {
		bandwidth = fmt.Sprintf("~%s Gbit/s", decSep(fmt.Sprintf("%.0f", message.Traffic/1000)))
	}

	data := Webhook{
		Username:  "DDoS-Alert",
		AvatarURL: "https://resources.tube-hosting.com/logo/app_icon.png",
		Embeds: []Embed{
			{
				Title:       "New attack detected",
				Description: strconv.Itoa(message.ID),
				URL:         "https://cp.tube-hosting.com",
				Color:       10751,
				Fields: []EmbedFields{
					{
						Name:   "⠀",
						Value:  fmt.Sprintf("> *IP under attack*:\n> **%s**\n⠀", message.IP),
						Inline: true,
					},
					{
						Name:   "⠀",
						Value:  fmt.Sprintf("> *time:*\n> **%s**\n⠀", strings.Replace(message.Time, "T", " ", 1)),
						Inline: true,
					},
					{
						Name:   "⠀",
						Value:  fmt.Sprintf("> *type:*\n> **%s**\n⠀", message.Type),
						Inline: true,
					},
					{
						Name:   "⠀",
						Value:  fmt.Sprintf("> *initital bandwith*:\n> **%s**\n⠀", bandwidth),
						Inline: true,
					},
					{
						Name:   "⠀",
						Value:  fmt.Sprintf("> *Initial Packets per second:*\n> **%s Packets/s**\n⠀", decSep(strconv.Itoa(message.PPS))),
						Inline: true,
					},
					{
						Name:   "⠀",
						Value:  fmt.Sprintf("> *avg. packet size:*\n> **%d**\n⠀", message.AvgPacketSize),
						Inline: true,
					},
				},
				Footer: Footer{
					Text: "tubehosting ddos alert made with <3 by Lennart01",
				},
				Timestamp: strings.Replace(message.Time, "T", " ", 1)[:len(message.Time)-5],
			},
		},
	}
	sendWebhook(webhookURL, data)

	var samplesFirst, samplesSecond string
	sampleCount := len(message.Samples)
	for i := 0; i < sampleCount/2; i++ {
		sample := message.Samples[i]
		samplesFirst += fmt.Sprintf("> src. IP: **%s** ⠀|⠀target port: **%d** ⠀|⠀protocol: **%s**\n", sample.SrcIP, sample.DstPort, prtIDToPrt(sample.IPProtocol))
	}

	for i := sampleCount / 2; i < sampleCount; i++ {
		sample := message.Samples[i]
		samplesSecond += fmt.Sprintf("> src. IP: **%s** ⠀|⠀target port: **%d** ⠀|⠀protocol: **%s**\n", sample.SrcIP, sample.DstPort, prtIDToPrt(sample.IPProtocol))
	}

	data = Webhook{
		Username:  "DDoS-Alert",
		AvatarURL: "https://resources.tube-hosting.com/logo/app_icon.png",
		Embeds: []Embed{
			{
				Title: "DDos Samples",
				Color: 10751,
				Fields: []EmbedFields{
					{
						Name:  "⠀",
						Value: samplesFirst,
					},
					{
						Name:  "⠀",
						Value: samplesSecond,
					},
				},
				Footer: Footer{
					Text: "tubehosting ddos alert made with <3 by Lennart01",
				},
				Timestamp: strings.Replace(message.Time, "T", " ", 1)[:len(message.Time)-5],
			},
		},
	}
	sendWebhook(webhookURL, data)
}

func sendWebhook(webhookURL string, data Webhook) {
	payload, err := json.Marshal(data)
	if err != nil {
		fmt.Println("error marshalling webhook payload:", err)
		return
	}

	resp, err := http.Post(webhookURL, "application/json", bytes.NewBuffer(payload))
	if err != nil {
		fmt.Println("error sending webhook:", err)
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusNoContent && resp.StatusCode != http.StatusOK {
		fmt.Printf("webhook returned non-204 status code: %d\n", resp.StatusCode)
	}
}

// SendTest sends a test message to the webhook
func SendTest(webhookURL string) error {
	data := Webhook{
		Username:  "DDoS-Alert",
		AvatarURL: "https://resources.tube-hosting.com/logo/app_icon.png",
		Embeds: []Embed{
			{
				Title:       "This is a test Message",
				Description: "Your webhook works",
				Color:       10751,
				Footer: Footer{
					Text: "tubehosting ddos alert\nmade with <3 by Lennart01",
				},
			},
		},
	}

	payload, err := json.Marshal(data)
	if err != nil {
		return err
	}

	resp, err := http.Post(webhookURL, "application/json", bytes.NewBuffer(payload))
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusNoContent {
		return fmt.Errorf("webhook returned non-204 status code: %d", resp.StatusCode)
	}
	return nil
}