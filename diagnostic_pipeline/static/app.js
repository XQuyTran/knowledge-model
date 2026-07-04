const form = document.getElementById('diagnose-form');
const statusEl = document.getElementById('status');
const summaryEl = document.getElementById('summary');
const feedbackEl = document.getElementById('feedback');
const evidenceEl = document.getElementById('evidence');
const repairStepsEl = document.getElementById('repair-steps');
const clearOutputBtn = document.getElementById('clear-output');

function setStatus(text) { statusEl.textContent = text; }
function clearResult() { summaryEl.innerHTML=''; feedbackEl.textContent=''; evidenceEl.innerHTML=''; repairStepsEl.innerHTML=''; setStatus('Idle'); }
function renderResult(data) {
  summaryEl.innerHTML = `<div class="summary-item"><strong>Top bug:</strong> ${data.top_bug || 'None'}</div><div class="summary-item"><strong>Confidence:</strong> ${data.confidence ?? 'N/A'}</div>`;
  feedbackEl.textContent = data.feedback || '';
  evidenceEl.innerHTML = '';
  for (const item of data.evidence || []) {
    const div = document.createElement('div');
    div.className = 'evidence-item';
    const line = item.location && item.location.line_start ? `Line ${item.location.line_start}` : 'No line';
    div.innerHTML = `<strong>${item.evidence_id}</strong><br><span>${item.description}</span><br><small>${item.source} · ${line} · confidence ${item.confidence}</small>`;
    evidenceEl.appendChild(div);
  }
  repairStepsEl.innerHTML = '';
  const steps = data.repair_plan && data.repair_plan.steps ? data.repair_plan.steps : [];
  for (const step of steps) { const li = document.createElement('li'); li.textContent = step.description; repairStepsEl.appendChild(li); }
}
form.addEventListener('submit', async (event) => {
  event.preventDefault(); setStatus('Running...'); feedbackEl.textContent = 'Analyzing submission...'; evidenceEl.innerHTML=''; repairStepsEl.innerHTML='';
  const testCases = [];
  const inputData = document.getElementById('test_input').value;
  const expectedOutput = document.getElementById('expected_output').value;
  if (expectedOutput.trim() || inputData.trim()) testCases.push({ name:'sample', input_data:inputData, expected_output:expectedOutput, timeout_seconds:2.0 });
  try {
    const response = await fetch('/diagnose', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ problem_statement:document.getElementById('problem_statement').value, source_code:document.getElementById('source_code').value, language:'cpp', file_path:'main.cpp', enable_sanitizers:true, compiler_flags:[], test_cases:testCases }) });
    if (!response.ok) throw new Error(await response.text() || `HTTP ${response.status}`);
    renderResult(await response.json()); setStatus('Done');
  } catch (error) { setStatus('Failed'); feedbackEl.textContent = `Request failed: ${error.message}`; }
});
clearOutputBtn.addEventListener('click', clearResult);
