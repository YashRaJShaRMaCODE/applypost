export function safeLeadHubOrigin(value) {
  try {
    const url = new URL(value);
    if (url.protocol !== "https:" || url.username || url.password || url.pathname !== "/" || url.search || url.hash) return "";
    return url.origin;
  } catch {
    return "";
  }
}

export function initializeLeadHub(doc, rawUrl) {
  const panel = doc.querySelector("#portfolio-updates");
  const configured = safeLeadHubOrigin(rawUrl);
  if (!panel || !configured) return false;
  const script = doc.createElement("script");
  script.src = `${configured}/embed.js`;
  script.defer = true;
  script.onload = () => { panel.hidden = false; };
  script.onerror = () => { panel.hidden = true; };
  doc.head.append(script);
  return true;
}

if (typeof document !== "undefined") {
  initializeLeadHub(document, document.querySelector('meta[name="leadhub-url"]')?.content);
}
