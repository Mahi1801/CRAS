const AGENT_URL = "http://127.0.0.1:8765/browser";

async function sendTabs() {
  try {
    const tabs = await chrome.tabs.query({});
    const activeTabs = await chrome.tabs.query({ active: true, currentWindow: true });

    const payload = {
      timestamp: new Date().toISOString(),
      active: activeTabs[0] ? {
        title: activeTabs[0].title || "",
        url: activeTabs[0].url || ""
      } : null,
      tabs: tabs.map(t => ({
        title: t.title || "",
        url: t.url || "",
        active: t.active
      }))
    };

    await fetch(AGENT_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
  } catch (e) {
    // Agent not running – ignore
  }
}

// Send every 5 seconds
chrome.alarms.create("sendTabs", { periodInMinutes: 0.08 });
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === "sendTabs") sendTabs();
});

// Also send on tab change
chrome.tabs.onActivated.addListener(sendTabs);
chrome.tabs.onUpdated.addListener(sendTabs);

sendTabs();