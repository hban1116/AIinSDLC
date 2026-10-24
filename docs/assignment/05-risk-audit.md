# Deliverable 5 - Lethal-trifecta risk audit

The three legs: (1) access to private data, (2) exposure to untrusted content, (3) ability to communicate
externally or act. An agent with all three can be steered by untrusted content into leaking the private data or
taking a harmful action. Audit date: 2026-10-24.

## Scope and a discrepancy

The assignment says the agent setup is described at the end of `ops/README.md`. In this repository it is not: the
README ends with "No answers here" and has no agent section. So this audit covers what is actually configured
or described in the repo, and the one agent workflow the assignment centres on (incident investigation):

| Setup | Evidence |
|---|---|
| A. Coding agent with repo instructions | `AGENTS.md`, `CLAUDE.md` (imports `AGENTS.md`) |
| B. Playwright MCP server | `.mcp.json`: `npx @playwright/mcp@latest` (unpinned) |
| C. Incident-analysis agent (read-only evidence, human decides) | `ops/incidents/INC-2041`, `INC-2047` READMEs; planned, not configured as a tool anywhere |

No other MCP server, hooks, secrets file, or agent permissions file exists. If the team runs a setup not in the
repo, it is out of scope and must be audited separately.

## Legs per setup

| Setup | Private data | Untrusted content | External action / egress |
|---|---|---|---|
| A. Coding agent | Local source, any files in the working tree and shell env | Issue text, PR diffs, dependency READMEs, web pages, tool output | Shell, network, `git push` if the user's credentials are present |
| B. Playwright MCP | Browser session on the app (`sessionStorage` token), page content | Any page it browses, including user-entered invoice text | Can navigate anywhere and submit forms; runs code fetched by `npx ...@latest` |
| C. Incident agent | Production logs and invoice data (customer data, supplier names) | Log lines contain user-controlled strings (invoice names, error messages) | Only if it were allowed to run prod commands or post to chat/tickets |

Result: A and B each have all three legs available at once in a typical developer session. C, as specified (read-only
evidence), has legs 1 and 2 and deliberately lacks leg 3.

## Findings

1. **B has the full trifecta and an unpinned supply chain.** `@latest` means whatever the registry serves at that
   moment runs on the developer machine with browser control. Severity: high.
2. **A is the usual developer-agent exposure.** Prompt injection in a diff or dependency text could instruct it to
   read files and send them out via shell/network. Mitigation today relies on the user approving tool calls, not on
   any configured restriction in the repo.
3. **C is safe only while it stays read-only.** The moment someone gives it a "restart worker" or "post to Slack"
   tool, it has the third leg with customer data in context.
4. **Log lines are untrusted input.** An invoice name such as "ignore previous instructions ..." ends up in logs
   that agent C reads.
5. The repository itself contains only demo credentials (`ChangeMe123!`), no real secrets; checked by grep in the
   final secret scan.

## Decision (to be confirmed by the user)

| Setup | Decision | Rationale |
|---|---|---|
| B | **Redesign**: pin the version (`@playwright/mcp@<exact>`), use it only against `localhost` demo data, and do not run it in a session that also holds real credentials or reads untrusted web content | Removes the supply-chain leg and keeps private data (demo only) away |
| A | **Accept with controls**, in writing | Keep per-call approval for shell/network/push; never put production credentials or customer data in the agent's environment; review any diff the agent produces before it leaves the machine |
| C | **Accept at read-only, redesign if scope grows** | Keep to exported evidence files, no production tools, outputs are drafts for a named human; treat log text as data, never as instructions |

Revisit triggers: any new MCP server or tool with write/network capability; any agent given production or
customer-data access; a security incident or injected-content near-miss; or a change of the Playwright MCP version
pin. Review at least quarterly.

Not done here (and why): I did not change `.mcp.json` - the user should decide on the pin version and apply it;
the audit recommends it but pinning an unverified version number would be a guess.
