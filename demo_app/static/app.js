// Simple Demo App

// Get elements
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

// Load scenarios
const scenarios = JSON.parse(appRoot.dataset.scenarios || "[]");

// Helper functions
function makeElement(tag, className, textContent) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (textContent) element.textContent = textContent;
    return element;
}

function setButtonBusy(button, busy) {
    if (busy) {
        button.dataset.originalText = button.innerHTML;
        button.innerHTML = '⏳ Testing...';
        button.setAttribute("disabled", "true");
    } else {
        if (button.dataset.originalText) {
            button.innerHTML = button.dataset.originalText;
        }
        button.removeAttribute("disabled");
    }
}

// Run evaluation
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
        showResults(data);
    } catch (error) {
        console.error(error);
        showError(error.message);
    } finally {
        setButtonBusy(button, false);
    }
}

// Show error
function showError(message) {
    resultsPlaceholder.classList.add("hidden");
    resultsCard.classList.remove("hidden");
    resultTitle.textContent = "Error";
    resultStatus.className = "sk-badge sk-badge--fail";
    resultStatus.textContent = "Error";
    resultReason.textContent = message;
    resultScore.textContent = "";
    resultFindings.innerHTML = "";
    resultReport.innerHTML = "";
}

// Show results
function showResults(data) {
    // Hide placeholder, show card
    resultsPlaceholder.classList.add("hidden");
    resultsCard.classList.remove("hidden");
    
    // Set title
    resultTitle.textContent = data.scenario.title;
    
    // Set status badge
    if (data.blocked) {
        resultStatus.className = "sk-badge sk-badge--fail";
        resultStatus.textContent = "🚫 BLOCKED";
    } else {
        resultStatus.className = "sk-badge sk-badge--pass";
        resultStatus.textContent = "✓ ALLOWED";
    }
    
    // Set reason
    resultReason.textContent = data.reason;
    
    // Set score
    const score = data.score;
    let scoreText = `Risk Score: ${score.toFixed(2)}`;
    if (score > 0.5) {
        scoreText += " (HIGH)";
    } else if (score > 0.2) {
        scoreText += " (MEDIUM)";
    } else {
        scoreText += " (LOW)";
    }
    resultScore.textContent = scoreText;
    
    // Show findings
    showFindings(data.findings || []);
    
    // Report link
    if (data.report_url) {
        resultReport.innerHTML = `<a href="${data.report_url}" target="_blank">📄 View Full Report</a>`;
    } else {
        resultReport.innerHTML = "";
    }
}

// Show findings
function showFindings(findings) {
    resultFindings.innerHTML = "";
    
    if (!findings.length) {
        const msg = makeElement("p", "sk-finding-details", "✓ No security issues detected");
        msg.style.color = "#22c55e";
        msg.style.fontWeight = "600";
        resultFindings.appendChild(msg);
        return;
    }
    
    findings.forEach((finding) => {
        const card = makeElement("div", "sk-finding");
        
        const header = makeElement("h3");
        header.textContent = `${finding.kind} (${finding.severity.toUpperCase()})`;
        
        const details = makeElement("p", "sk-finding-details", finding.details);
        
        card.appendChild(header);
        card.appendChild(details);
        
        // Evidence
        const evidence = Object.entries(finding.evidence || {});
        if (evidence.length) {
            const meta = makeElement("div", "sk-finding-meta");
            meta.innerHTML = evidence.map(([key, value]) => 
                `${key}: ${JSON.stringify(value)}`
            ).join("<br>");
            card.appendChild(meta);
        }
        
        resultFindings.appendChild(card);
    });
}

// Build scenario card
function buildScenarioCard(scenario) {
    const card = makeElement("article", "sk-card");
    
    const title = makeElement("h3", null, scenario.title);
    const summary = makeElement("p", null, scenario.summary);
    
    card.appendChild(title);
    card.appendChild(summary);
    
    const variantsContainer = makeElement("div", "sk-variants");
    
    scenario.variants.forEach((variant) => {
        const button = makeElement("button", "sk-variant-button");
        
        const label = makeElement("span");
        label.textContent = variant.label;
        
        const desc = makeElement("span", "sk-variant-desc", variant.description);
        
        button.appendChild(label);
        button.appendChild(desc);
        
        button.addEventListener("click", () => {
            runScenarioVariant(scenario.id, variant.key, button);
        });
        
        variantsContainer.appendChild(button);
    });
    
    card.appendChild(variantsContainer);
    return card;
}

// Initialize
function init() {
    scenarios.forEach((scenario) => {
        const card = buildScenarioCard(scenario);
        scenarioGrid.appendChild(card);
    });
}

init();
