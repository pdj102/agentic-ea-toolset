# ADR Compliance Checker

A browser-based tool that evaluates Architecture Decision Records (ADRs) against a set of quality rules using Claude AI. Paste an ADR, click check, and get structured pass/fail results with actionable recommendations in under 30 seconds.

A video of the tool in action https://youtube.com/shorts/RwMD0coEITs?si=so8W_fCmc2DRmYCp

## Setup

**Requirements:** Node.js 18+

```bash
npm install

cp .env.example .env
# Edit .env and set VITE_ANTHROPIC_API_KEY=your-key-here

npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

## Usage

1. Paste your ADR into the text area (a sample ADR is pre-loaded)
2. Click **Run compliance check**
3. Review results grouped by category — each rule shows a colour-coded status badge plus evidence, explanation, and recommendation

To check a different document, click **← New document** to reset.

## Compliance Rules

12 rules across 5 categories. Rules marked **mandatory** must all pass for the document to meet minimum threshold.

| ID | Rule | Type |
|---|---|---|
| R01 | ADR has a clearly identified title | Mandatory |
| R02 | Problem context / question being decided is stated | Mandatory |
| R03 | Decision is documented as a clear affirmative action | Mandatory |
| R04 | Status field is present (Proposed / Accepted / Deprecated / Superseded) | Mandatory |
| R05 | Rationale / justification is documented | Mandatory |
| R06 | Alternatives considered and rejection reasons are documented | Advisory |
| R07 | Assumptions are identified | Advisory |
| R08 | Consequences, implications, and trade-offs are documented | Mandatory |
| R09 | Risks are identified with likelihood / impact ratings | Advisory |
| R10 | Related ADRs, requirements, or constraints are referenced | Advisory |
| R11 | Author / decision owner is identified | Mandatory |
| R12 | Document is understandable without programme context | Advisory |

Result statuses: **Pass** (green) · **Fail** (red) · **Partial** (yellow) · **Not applicable** (grey)

## Dev Mode

Append `?dev=true` to the URL to run against hardcoded sample results without making API calls — useful for UI development and testing.

## Building for Production

```bash
npm run build
```

Output is written to `dist/`. The Vite config proxies `/api/anthropic` to the Anthropic API, so the API key stays server-side and is never exposed to the browser in production.

## Known Limitations

- Rules are evaluated sequentially (one API call per rule) — a full check takes 15–30 seconds depending on API latency.
- The tool checks structural and content quality only; it does not validate whether the decision itself is technically sound.
- PDF input is not supported — paste plain text or Markdown.
