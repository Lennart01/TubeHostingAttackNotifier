package tubehosting

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"strings"
	"time"
)

const (
	apiBaseURL = "https://api.tube-hosting.com"
)

// AuthResponse represents the response from the login endpoint
type AuthResponse struct {
	Token string `json:"token"`
}

// Attack represents a single DDoS attack incident
type Attack struct {
	ID            int      `json:"id"`
	IP            string   `json:"ip"`
	Time          string   `json:"time"`
	Type          string   `json:"type"`
	Traffic       float64  `json:"traffic"`
	PPS           int      `json:"pps"`
	AvgPacketSize int      `json:"avgPacketSize"`
	Samples       []Sample `json:"samples"`
}

// Sample represents a sample of attack traffic
type Sample struct {
	SrcIP      string `json:"srcIP"`
	DstPort    int    `json:"dstPort"`
	IPProtocol int    `json:"ipProtocol"`
}

// GetAuthToken retrieves an authentication token from the Tube-Hosting API
func GetAuthToken(email, password string) (string, error) {
	postData, _ := json.Marshal(map[string]string{
		"mail":     email,
		"password": password,
	})

	resp, err := http.Post(fmt.Sprintf("%s/login", apiBaseURL), "application/json", bytes.NewBuffer(postData))
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("failed to authenticate, status code: %d", resp.StatusCode)
	}

	body, _ := ioutil.ReadAll(resp.Body)
	var authResponse AuthResponse
	if err := json.Unmarshal(body, &authResponse); err != nil {
		return "", err
	}

	return authResponse.Token, nil
}

// GetLastAttackTimestamp retrieves the timestamp of the last attack for each IP
func GetLastAttackTimestamp(authToken string, ipList []string) (map[string]time.Time, error) {
	lastAttackTime := make(map[string]time.Time)
	header := http.Header{}
	header.Set("Authorization", "Bearer "+authToken)

	client := &http.Client{}

	for _, ip := range ipList {
		req, _ := http.NewRequest("GET", fmt.Sprintf("%s/ips/%s/ddos/incidents", apiBaseURL, ip), nil)
		req.Header = header
		resp, err := client.Do(req)
		if err != nil {
			return nil, err
		}
		defer resp.Body.Close()

		if resp.StatusCode != http.StatusOK {
			fmt.Printf("Error fetching incidents for IP %s: %s\n", ip, resp.Status)
			continue
		}

		body, _ := ioutil.ReadAll(resp.Body)
		if len(body) < 3 {
			lastAttackTime[ip] = time.Time{} // Zero value for time
			continue
		}

		var attacks []Attack
		if err := json.Unmarshal(body, &attacks); err != nil {
			fmt.Printf("Error unmarshalling attacks for IP %s: %v\n", ip, err)
			continue
		}

		if len(attacks) > 0 {
			lastAttack := attacks[len(attacks)-1]
			parsedTime, err := parseAttackTime(lastAttack.Time)
			if err != nil {
				fmt.Printf("Error parsing time for IP %s: %v\n", ip, err)
				lastAttackTime[ip] = time.Time{}
			} else {
				lastAttackTime[ip] = parsedTime
			}
		} else {
			lastAttackTime[ip] = time.Time{}
		}
	}
	return lastAttackTime, nil
}

// CheckForNewAttacks checks for new DDoS attacks and returns new attacks
func CheckForNewAttacks(authToken string, ipList []string, lastAttackTimes map[string]time.Time) ([]Attack, map[string]time.Time, error) {
	var newAttacks []Attack
	header := http.Header{}
	header.Set("Authorization", "Bearer "+authToken)
	client := &http.Client{}

	for _, ip := range ipList {
		req, _ := http.NewRequest("GET", fmt.Sprintf("%s/ips/%s/ddos/incidents", apiBaseURL, ip), nil)
		req.Header = header
		resp, err := client.Do(req)
		if err != nil {
			return nil, lastAttackTimes, err
		}
		defer resp.Body.Close()

		if resp.StatusCode != http.StatusOK {
			fmt.Printf("Error fetching incidents for IP %s: %s\n", ip, resp.Status)
			continue
		}

		body, _ := ioutil.ReadAll(resp.Body)
		if len(body) < 3 {
			continue
		}

		var attacks []Attack
		if err := json.Unmarshal(body, &attacks); err != nil {
			fmt.Printf("Error unmarshalling attacks for IP %s: %v\n", ip, err)
			continue
		}

		if len(attacks) > 0 {
			lastAttack := attacks[len(attacks)-1]
			parsedTime, err := parseAttackTime(lastAttack.Time)
			if err != nil {
				fmt.Printf("Error parsing time for IP %s: %v\n", ip, err)
				continue
			}

			if lastAttackTimes[ip].IsZero() || parsedTime.After(lastAttackTimes[ip]) {
				newAttacks = append(newAttacks, lastAttack)
				lastAttackTimes[ip] = parsedTime
			}
		}
	}
	return newAttacks, lastAttackTimes, nil
}

func parseAttackTime(timeStr string) (time.Time, error) {
	// The python script uses a weird way to compare timestamps.
	// It removes separators and compares as a float.
	// `2023-12-07T12:34:56Z` -> `20231207123456.0`
	// A better way is to parse it as a proper time object.
	// The format looks like RFC3339.
	// Let's try to parse it.
	layout := "2006-01-02T15:04:05Z"
	// The timestamps in the example have fractional seconds.
	layout_frac := "2006-01-02T15:04:05.999999Z"

	t, err := time.Parse(layout, timeStr)
	if err != nil {
		t, err = time.Parse(layout_frac, timeStr)
		if err != nil {
			// fallback to python's way if proper parsing fails
			replacer := strings.NewReplacer("-", "", "T", "", ":", "", "Z", "")
			timeStr := replacer.Replace(timeStr)
			// This is not ideal, but we're trying to replicate the python script's behavior
			// Since we can't convert to float, let's just use string comparison which should work for this format.
			// A better approach is to use proper time parsing. Assuming RFC3339 format.
			return time.Time{}, fmt.Errorf("could not parse time: %s", timeStr)
		}
	}
	return t, nil
}