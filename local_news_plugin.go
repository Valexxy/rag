package main

import (
	"encoding/xml"
	"fmt"
	"net/http"
	"net/url"
	"strings"
	"time"
)

// RSS XML Structs for Google News Geolocated Feed
type RSSFeed struct {
	Channel struct {
		Title string    `xml:"title"`
		Items []RSSItem `xml:"item"`
	} `xml:"channel"`
}

type RSSItem struct {
	Title   string `xml:"title"`
	Link    string `xml:"link"`
	PubDate string `xml:"pubDate"`
}

type LocalNewsPlugin struct{}

var globalLocalNewsPlugin = &LocalNewsPlugin{}

// Fetch Commerce & Logistics Relevant News for State / LGA
func (n *LocalNewsPlugin) GetLocalCommerceNews(stateOrCity string) string {
	if stateOrCity == "" {
		return ""
	}

	cleanQuery := strings.TrimSpace(stateOrCity)
	// Fetch Google News RSS for commerce/traffic/business in that region
	rssURL := fmt.Sprintf("https://news.google.com/rss/search?q=%s+traffic+OR+market+OR+business&hl=en-NG&gl=NG&ceid=NG:en", url.QueryEscape(cleanQuery))

	client := &http.Client{Timeout: 3 * time.Second}
	resp, err := client.Get(rssURL)
	if err != nil {
		return ""
	}
	defer resp.Body.Close()

	var feed RSSFeed
	if err := xml.NewDecoder(resp.Body).Decode(&feed); err != nil || len(feed.Channel.Items) == 0 {
		return ""
	}

	// Filter for relevant non-political headline
	for _, item := range feed.Channel.Items {
		title := item.Title
		titleLower := strings.ToLower(title)
		// Exclude political drama / sensationalism
		if !strings.Contains(titleLower, "election") && !strings.Contains(titleLower, "court") && !strings.Contains(titleLower, "police") && !strings.Contains(titleLower, "kill") {
			// Clean source prefix
			parts := strings.Split(title, " - ")
			cleanTitle := parts[0]
			if len(cleanTitle) > 90 {
				cleanTitle = cleanTitle[:90] + "..."
			}
			return fmt.Sprintf("📰 *[Local Update — %s]:* %s", cleanQuery, cleanTitle)
		}
	}

	return ""
}
