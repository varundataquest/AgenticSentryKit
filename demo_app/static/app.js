const appRoot = document.getElementById("sk-app");
const scenarioGrid = document.getElementById("scenario-grid");
const resultsPlaceholder = document.getElementById("results-placeholder");
const resultsCard = document.getElementById("results-card");
const resultTitle = document.getElementById("result-title");
const resultStatus = document.getElementById("result-status");
const resultReason = document.getElementById("result-reason");
const resultScore = document.getElementById("result-score");
const resultFindings = document.getElementById("result-findings");
const resultReport = document.getElementById("result-report");

const scenarios = JSON.parse(appRoot.dataset.scenarios || "[]");

function makeElement(tag, className, textContent) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (textContent) element.textContent = textContent;
    return element;
}

function setButtonBusy(button, busy) {
    if (busy) {
        button.dataset.originalText = button.innerHTML;
        button.innerHTML = "Evaluating…";
        button.setAttribute("disabled", "true");
    } else {
        if (button.dataset.originalText) {
            button.innerHTML = button.dataset.originalText;
        }
        button.removeAttribute("disabled");
    }
}

async function runScenarioVariant(scenarioId, variantKey, button) {
    try {
        setButtonBusy(button, true);
        const response = await fetch("/evaluate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ scenario_id: scenarioId, variant_key: variantKey }),
        });
        if (!response.ok) {
            throw new Error(`Request failed: ${response.status}`);
        }
        const data = await response.json();
        renderResults(data);
    } catch (error) {
        console.error(error);
        renderError(error.message);
    } finally {
        setButtonBusy(button, false);
    }
}

function renderError(message) {
    resultsPlaceholder.classList.add("hidden");
    resultsCard.classList.remove("hidden");
    resultTitle.textContent = "Evaluation failed";
    resultStatus.className = "sk-badge sk-badge--fail";
    resultStatus.textContent = "Error";
    resultReason.textContent = message;
    resultScore.textContent = "";
    resultFindings.innerHTML = "";
    resultReport.innerHTML = "";
}

function renderFindings(findings) {
    if (!findings.length) {
        const empty = makeElement("p", "sk-finding-details", "No findings. Guard passed.");
        resultFindings.appendChild(empty);
        return;
    }
    findings.forEach((finding) => {
        const card = makeElement("div", "sk-finding");
        const header = makeElement("h3");
        header.textContent = `${finding.kind} · ${finding.severity.toUpperCase()}`;
        const details = makeElement("p", "sk-finding-details", finding.details);
        card.appendChild(header);
        card.appendChild(details);

        const evidenceLines = Object.entries(finding.evidence || {}).map(
            ([key, value]) => `${key}: ${JSON.stringify(value)}`
        );
        if (evidenceLines.length) {
            const meta = makeElement("p", "sk-finding-meta");
            meta.innerHTML = evidenceLines.join("<br>");
            card.appendChild(meta);
        }
        resultFindings.appendChild(card);
    });
}

function renderResults(data) {
    resultsPlaceholder.classList.add("hidden");
    resultsCard.classList.remove("hidden");

    resultTitle.textContent = `${data.scenario.title} · ${data.scenario.variant}`;
    const statusClass = data.blocked ? "sk-badge sk-badge--fail" : "sk-badge sk-badge--pass";
    const statusLabel = data.blocked ? "Blocked" : "Allowed";
    resultStatus.className = statusClass;
    resultStatus.textContent = statusLabel;
    resultReason.textContent = data.reason;
    resultScore.textContent = `Risk score: ${data.score.toFixed(2)}`;
    resultFindings.innerHTML = "";
    renderFindings(data.findings || []);

    if (data.report_url) {
        resultReport.innerHTML = `<a href="${data.report_url}" target="_blank" rel="noopener">Open full report →</a>`;
    } else {
        resultReport.innerHTML = "";
    }
}

function buildScenarioCard(scenario) {
    const card = makeElement("article", "sk-card");
    const title = makeElement("h3", null, scenario.title);
    const summary = makeElement("p", null, scenario.summary);
    card.appendChild(title);
    card.appendChild(summary);

    const variantsContainer = makeElement("div", "sk-variants");

    scenario.variants.forEach((variant) => {
        const button = makeElement("button", "sk-variant-button");
        const label = makeElement("span", null, variant.label);
        const secondary = makeElement("span", "sk-variant-desc", variant.description);

        button.appendChild(label);
        button.appendChild(secondary);
        button.addEventListener("click", () => runScenarioVariant(scenario.id, variant.key, button));
        variantsContainer.appendChild(button);
    });

    card.appendChild(variantsContainer);
    return card;
}

function bootstrap() {
    scenarios.forEach((scenario) => {
        const card = buildScenarioCard(scenario);
        scenarioGrid.appendChild(card);
    });
}

bootstrap();
