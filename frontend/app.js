const mockData = {
  server: {
    name: "notebooklm-mcp-server",
    version: "0.1.0",
    protocol_version: "2025-01-01",
  },
  compatibility: {
    compatible: true,
    summary: "11/11 checks OK",
    checks: {
      has_server_name: true,
      has_server_version: true,
      has_protocol_version: true,
      has_tools: true,
      resources_supported: true,
      prompts_supported: true,
      rbac_enabled: true,
      private_mode_enabled: true,
      api_key_supported: true,
      audit_enabled: true,
      audit_max_events_present: true,
    },
  },
  capabilities: {
    tools: { count: 17 },
    resources: { supported: true },
    prompts: { supported: true },
    security: { private_mode: true, api_key_enabled: false, audit: true },
  },
};

function fill() {
  const info = document.getElementById("server-info");
  const caps = document.getElementById("capabilities");
  const checks = document.getElementById("checks");
  const badge = document.getElementById("compatibility-badge");

  info.innerHTML = Object.entries(mockData.server)
    .map(([k, v]) => `<li><strong>${k}</strong>: ${v}</li>`)
    .join("");

  caps.innerHTML = [
    `<li>tools: ${mockData.capabilities.tools.count}</li>`,
    `<li>resources: ${mockData.capabilities.resources.supported}</li>`,
    `<li>prompts: ${mockData.capabilities.prompts.supported}</li>`,
    `<li>private_mode: ${mockData.capabilities.security.private_mode}</li>`,
    `<li>audit: ${mockData.capabilities.security.audit}</li>`,
  ].join("");

  checks.innerHTML = Object.entries(mockData.compatibility.checks)
    .map(([k, v]) => `<li>${v ? "✅" : "❌"} ${k}</li>`)
    .join("");

  badge.textContent = mockData.compatibility.summary;
}

fill();
