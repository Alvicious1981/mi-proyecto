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

const JSON_HEADERS = { Accept: "application/json" };

function renderDashboard(data, sourceLabel, statusText) {
  const info = document.getElementById("server-info");
  const caps = document.getElementById("capabilities");
  const checks = document.getElementById("checks");
  const badge = document.getElementById("compatibility-badge");
  const source = document.getElementById("data-source");
  const statusMessage = document.getElementById("status-message");

  info.innerHTML = Object.entries(data.server)
    .map(([k, v]) => `<li><strong>${k}</strong>: ${v}</li>`)
    .join("");

  caps.innerHTML = [
    `<li>tools: ${data.capabilities.tools.count}</li>`,
    `<li>resources: ${data.capabilities.resources.supported}</li>`,
    `<li>prompts: ${data.capabilities.prompts.supported}</li>`,
    `<li>private_mode: ${data.capabilities.security.private_mode}</li>`,
    `<li>audit: ${data.capabilities.security.audit}</li>`,
  ].join("");

  checks.innerHTML = Object.entries(data.compatibility.checks)
    .map(
      ([k, v]) => `<li class="${v ? "check-ok" : "check-fail"}">${v ? "✅" : "❌"} ${k}</li>`,
    )
    .join("");

  badge.textContent = data.compatibility.summary;
  badge.style.color = data.compatibility.compatible ? "var(--good)" : "var(--bad)";
  source.textContent = sourceLabel;
  statusMessage.textContent = statusText;
}

async function fetchJson(path) {
  const response = await fetch(path, { headers: JSON_HEADERS });
  if (!response.ok) {
    throw new Error(`${path} respondió ${response.status}`);
  }
  return response.json();
}

async function loadRealData() {
  const [compatibilityReport, descriptor] = await Promise.all([
    fetchJson("/artifacts/compatibility-report.json"),
    fetchJson("/artifacts/mcp-descriptor.json"),
  ]);

  return {
    server: {
      name: descriptor.server?.name ?? "unknown",
      version: descriptor.server?.version ?? "unknown",
      protocol_version: descriptor.protocol_version ?? "unknown",
    },
    compatibility: {
      compatible: compatibilityReport.compatible,
      summary: compatibilityReport.summary,
      checks: compatibilityReport.checks,
    },
    capabilities: {
      tools: { count: Array.isArray(descriptor.tools) ? descriptor.tools.length : 0 },
      resources: { supported: Boolean(descriptor.capabilities?.resources?.supported) },
      prompts: { supported: Boolean(descriptor.capabilities?.prompts?.supported) },
      security: {
        private_mode: Boolean(descriptor.capabilities?.security?.private_mode),
        api_key_enabled: Boolean(descriptor.capabilities?.security?.api_key_enabled),
        audit: Boolean(descriptor.capabilities?.security?.audit),
      },
    },
  };
}

async function refreshDashboard() {
  try {
    const realData = await loadRealData();
    renderDashboard(realData, "Datos reales (artifacts)", "Última actualización: correcta.");
  } catch (error) {
    renderDashboard(
      mockData,
      "Datos mock",
      `No se pudieron cargar artifacts reales (${error.message}). Mostrando fallback mock.`,
    );
  }
}

document.getElementById("refresh-btn").addEventListener("click", () => {
  refreshDashboard();
});

refreshDashboard();
