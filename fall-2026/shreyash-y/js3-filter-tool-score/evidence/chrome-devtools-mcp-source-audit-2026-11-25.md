# chrome-devtools-mcp: read-only source audit (2026-11-25, about 17:12 EST)

*The report of a Claude Code helper (a subagent) that read the installed package's files only. It ran no
Node, npm, npx or Chrome and wrote nothing. This is model output, copied here by Claude Code unchanged,
except that the home folder in paths is shown as `~` and the formatting is lightly cleaned. TOOLSERVER.md
section 3 relies on it. Its findings were then checked against the two live sessions
(`evidence/chrome-devtools-mcp-commands-2026-11-25.md`). The live `tools/list` shows **8** tools marked
`readOnlyHint: true`.*

Paths: NEW = `~/.npm/_npx/ba38acecdf97096f/node_modules/chrome-devtools-mcp`,
OLD = `~/.npm/_npx/15c61037b1978c83/node_modules/chrome-devtools-mcp`, S = `build/src`. Line numbers refer to
NEW unless marked OLD.

## 1. Package metadata

- **NEW** `package.json`: version 1.10.1 (line 3). `bin` (lines 6-9): `"chrome-devtools-mcp": "./build/src/bin/chrome-devtools-mcp.js"` and `"chrome-devtools": "./build/src/bin/chrome-devtools.js"`.
- **OLD** `package.json`: version 1.5.0 (line 3).
- **Both:** `"repository": "ChromeDevTools/chrome-devtools-mcp"` (NEW line 47), `"author": "Google LLC"` (NEW line 48), `"license": "Apache-2.0"` (NEW line 49).
- NEW also has `"mcpName": "io.github.ChromeDevTools/chrome-devtools-mcp"` (line 54).
- `~/.cache/chrome-devtools-mcp/latest.json` reads `{"version":"1.14.0"}`. That is the update-check cache (section 5).

## 2. CLI flags

Defined with yargs in NEW `S/config/mcp-options.js`, `S/config/browser-options.js` and `S/config/category-options.js`.

- `--headless` (boolean, default false, browser-options.js:81-85): "Whether to run in headless (no UI) mode."
- `--isolated` (:92-95): "If specified, creates a temporary user-data-dir that is automatically cleaned up after the browser is closed. Defaults to false."
- `--userDataDir` (:96-100): "Path to the user data directory for Chrome. Default is $HOME/.cache/chrome-devtools-mcp/chrome-profile$CHANNEL_SUFFIX_IF_NON_STABLE".
- `--executablePath` / `-e` (:86-91); `--browserUrl` / `-u` (:19-36); `--wsEndpoint` / `-w` (:37-60); `--wsHeaders` (:61-80); `--autoConnect` (default false, :7-18); `--channel` (:101-106); `--proxyServer` (:107-110); `--chromeArg` (:111-115); `--ignoreDefaultChromeArg` (:116-120).
- `--logFile` (mcp-options.js:15-18); `--viewport` (:19-35); `--acceptInsecureCerts` (:36-39).
- `--usageStatistics` (boolean, **default true**, :130-134): "Set to false to opt-out of usage statistics collection. Google collects usage data to improve the tool, handled under the Google Privacy Policy (https://policies.google.com/privacy). This is independent from Chrome browser metrics. Disabled if `CHROME_DEVTOOLS_MCP_NO_USAGE_STATISTICS` or `CI` env variables are set." The environment override is at :302-305.
- `--performanceCrux` (boolean, **default true**, :125-129): "Set to false to disable sending URLs from performance traces to CrUX API to get field performance data."
- `--javascriptEvaluation` (default true, :135-139).
- `--slim` (:204-207): "Exposes a "slim" set of 3 tools covering navigation, script execution and screenshots only."
- `--filesystemRoot` / `--workspace` (:227-234). The default is the OS temp dir (`DEFAULT_FILESYSTEM_ROOT = [os.tmpdir()]`, line 9).
- `--allowUnrestrictedPaths` (default false, deprecated, :218-226).
- `--blockedUrlPattern` and `--allowedUrlPattern` exist and conflict with each other.
- Hidden flags include `--clearcutEndpoint`.

## 3. When Chrome launches: lazily, not at start-up

- **Start-up** (`S/bin/chrome-devtools-mcp-main.js`) builds `new BrowserManager(args,{logFile})` (line 26) and `McpServer.from` (line 29), then connects stdio (lines 71-72). It does not call `ensureBrowser`.
- **The launch** is in `BrowserManager.ensureBrowser()` (`S/BrowserManager.js`:130). Its only caller is `McpServer.#getContext()` (`S/index.js`:155-156), which `ToolHandler.handle` (`S/ToolHandler.js`:224) calls on the first tool call.
- `#initBrowser` (`BrowserManager.js`:172-179) either connects to a browser, or launches one with `puppeteer.launch({... pipe:true, headless, userDataDir ...})` (:214-230).

## 4. Default profile

- `BrowserManager.js`:182-191: without `--isolated` or `--userDataDir`, the profile is `~/.cache/chrome-devtools-mcp/chrome-profile`. This is a separate, persistent profile, not Chrome's normal one, so cookies and logins persist across runs of the server.
- On this Mac that folder exists (created Nov 6).
- `--autoConnect`, `--browserUrl` and `--wsEndpoint` attach to a running Chrome instead, and its real tabs.

## 5. Network requests the server itself makes

- **(a) Update check, on by default.**
  - `S/utils/check-for-updates.js` and `S/bin/check-latest-version.js`, called at start-up (main.js:17).
  - If `latest.json` is older than 24 hours, the server spawns a detached `node check-latest-version.js` (check-for-updates.js:41-69). That runs `execSync('npm config get registry')` and then `fetch(<registry>/chrome-devtools-mcp/latest)`.
  - The opt-out is the environment variable `CHROME_DEVTOOLS_MCP_NO_UPDATE_CHECKS` (line 23). There is no flag.
- **(b) Usage statistics ("Clearcut"), on by default.**
  - The `McpServer` constructor (`S/index.js`:43-52) calls `ClearcutLogger.initialize`, which spawns a detached `node S/telemetry/watchdog/main.js` (`S/telemetry/WatchdogClient.js`:12-36).
  - The endpoint is `S/telemetry/watchdog/ClearcutSender.js`:9, `DEFAULT_CLEARCUT_ENDPOINT = 'https://play.googleapis.com/log?format=json_proto'`, with `LOG_SOURCE = 2839` (:11). The POST is at :155.
  - **Events** (ClearcutLogger.js): `server_start` with flag usage (:168-177); `daily_active` (:178-198), with state in `~/Library/Application Support/chrome-devtools-mcp/telemetry_state.json`; `tool_invocation` with tool name, success, bucketed latency and sanitized parameters (:142-167; called from ToolHandler.js:302); and the MCP client's name.
  - Strings are sent as bucketed lengths. The page URL is not sent (transformation.js `buildContext`).
- **(c) CrUX field data, on by default.** `S/tools/performance.js`:186-206 sends trace URLs to `https://chromeuxreport.googleapis.com/v1/records:queryRecord?key=…`, during `performance_stop_trace` only.
- **(d) Not audited:** the bundled DevTools frontend, `third_party/index.js` (about 200,000 lines).

## 6. Tools declared (NEW)

- **Registration:** tools are registered with `annotations: tool.annotations` (`S/index.js`:197-201).
- **Server identity:** `name:'chrome_devtools'`, `title:'Chrome DevTools MCP server'` (index.js:53-57). The bundled SDK's `LATEST_PROTOCOL_VERSION` is `"2025-11-25"`; in the live session the server answered `2025-06-18` to the client's request.
- **Tools that change state:**
  - Input: `click`, `hover`, `fill`, `fill_form`, `type_text`, `drag`, `press_key`, `upload_file` (reads local `filePaths` and hands them to the page; input.js:546-597) and `handle_dialog`.
  - Navigation: `new_page` and `navigate_page` (its `initScript` runs JavaScript), and `close_page`.
  - Emulation: `emulate` (including `extraHttpHeaders`) and `resize_page`.
  - `evaluate_script` (runs JavaScript in the page).
  - `get_network_request` (exposes Cookie and Set-Cookie headers).
  - Performance traces, `lighthouse_audit` and `take_heapsnapshot`.
- **Marked read-only** in the live `tools/list`: `get_console_message`, `get_css_styles`, `list_console_messages`, `list_network_requests`, `list_pages`, `performance_analyze_insight`, `select_page` and `wait_for`.
- **The URL guard** (`utils/url.js`) blocks `javascript:`, `data:` and `vbscript:` only with `--no-javascript-evaluation`. By default there is no domain allow-list.

## 7. Files written

- The Chrome profile (persistent by default; temporary with `--isolated`).
- `~/.cache/chrome-devtools-mcp/latest.json`.
- `telemetry_state.json`, when statistics are on.
- `--logFile`.
- Tool outputs at paths inside `--filesystemRoot` (default: the temp dir), checked by `McpContext.js`:144-197 `validatePath`.

## 8. Chrome installed

`/Applications/Google Chrome.app`, `CFBundleShortVersionString` 157.0.8103.79.
