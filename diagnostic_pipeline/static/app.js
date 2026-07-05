document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('diagnose-form');
  const status = document.getElementById('status');
  const summary = document.getElementById('summary');
  const feedback = document.getElementById('feedback');
  const evidence = document.getElementById('evidence');
  const repairSteps = document.getElementById('repair-steps');
  const problemInfo = document.getElementById('problem-info');
  const problemSelector = document.getElementById('problem_selector');
  const problemStatement = document.getElementById('problem_statement');
  const sourceCode = document.getElementById('source_code');
  const testInput = document.getElementById('test_input');
  const expectedOutput = document.getElementById('expected_output');
  const clearBtn = document.getElementById('clear-output');

  fetch('/exercises')
    .then(r => r.json())
    .then(exercises => {
      const grouped = {};
      exercises.forEach(ex => {
        const cat = ex.category || 'Khác';
        if (!grouped[cat]) grouped[cat] = [];
        grouped[cat].push(ex);
      });
      Object.keys(grouped).sort().forEach(cat => {
        const optGroup = document.createElement('optgroup');
        optGroup.label = `📁 ${cat}`;
        grouped[cat].forEach(ex => {
          const opt = document.createElement('option');
          opt.value = ex.problem_id;
          opt.textContent = `${ex.title} [${ex.difficulty}]`;
          opt.title = ex.source;
          optGroup.appendChild(opt);
        });
        problemSelector.appendChild(optGroup);
      });
    })
    .catch(() => {});

  problemSelector.addEventListener('change', () => {
    const pid = problemSelector.value;
    if (!pid) return;
    fetch(`/exercises/${pid}`)
      .then(r => r.json())
      .then(ex => {
        if (!ex) return;
        problemStatement.value = ex.description;
        sourceCode.value = ex.correct_code;
        expectedOutput.value = ex.expected_output;
      })
      .catch(() => {});
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    status.textContent = '⏳ Đang chẩn đoán...';
    status.className = 'status busy';
    summary.innerHTML = '';
    feedback.textContent = '';
    evidence.innerHTML = '';
    repairSteps.innerHTML = '';
    problemInfo.innerHTML = '';
    const payload = {
      problem_statement: problemStatement.value,
      source_code: sourceCode.value,
      problem_id: problemSelector.value || null,
      test_cases: [],
    };
    if (testInput.value || expectedOutput.value) {
      payload.test_cases.push({
        name: 'user_test',
        input_data: testInput.value,
        expected_output: expectedOutput.value,
      });
    }
    try {
      const res = await fetch('/diagnose', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      renderResult(data);
      status.textContent = data.top_bug ? '⚠ Phát hiện lỗi' : '✅ Không phát hiện lỗi';
      status.className = data.top_bug ? 'status done' : 'status done';
    } catch (err) {
      status.textContent = '❌ Lỗi kết nối';
      status.className = 'status error';
      feedback.textContent = `Error: ${err.message}`;
    }
  });

  clearBtn.addEventListener('click', () => {
    summary.innerHTML = '';
    feedback.textContent = '';
    evidence.innerHTML = '';
    repairSteps.innerHTML = '';
    problemInfo.innerHTML = '';
    status.textContent = 'Sẵn sàng';
    status.className = 'status';
  });

  function renderResult(data) {
    if (data.top_bug) {
      summary.innerHTML = `
        <div style="display:flex;align-items:center;gap:1rem;flex-wrap:wrap;">
          <span style="background:#ef4444;color:#fff;padding:0.25rem 0.8rem;border-radius:999px;font-weight:700;font-size:0.85rem;">
            🐛 ${data.top_bug}
          </span>
          <span style="background:#f59e0b;color:#000;padding:0.25rem 0.8rem;border-radius:999px;font-weight:700;font-size:0.85rem;">
            ${(data.confidence * 100).toFixed(1)}%
          </span>
          ${data.alternatives && data.alternatives.length ? `
            <span style="color:var(--text-dim);font-size:0.8rem;">
              Candidates: ${data.alternatives.map(a => `${a.bug_id} (${(a.score*100).toFixed(0)}%)`).join(', ')}
            </span>
          ` : ''}
        </div>
      `;
      if (data.repair_plan) {
        summary.innerHTML += `
          <div style="margin-top:0.5rem;font-size:0.8rem;color:var(--text-dim);">
            Repair plan: <strong>${data.repair_plan.name}</strong> (${data.repair_plan.steps.length} steps)
          </div>
        `;
      }
    } else {
      summary.innerHTML = `<span style="color:var(--green);font-weight:700;">✅ No high-confidence bug detected.</span>`;
    }

    if (data.matched_problems && data.matched_problems.length) {
      let html = '<div class="section-title">📚 Bài toán phù hợp từ CSDL tri thức</div>';
      data.matched_problems.forEach(p => {
        html += `<div class="problem-info" style="margin-bottom:0.3rem;">
          <div class="row"><span class="label">📌</span> <strong>${p.title}</strong> <span style="color:var(--text-dim);font-size:0.75rem;">(${p.difficulty})</span></div>
          <div class="row"><span class="label">📂</span> ${p.category} · <span class="label">Thuật toán:</span> ${p.algorithm} · <span class="label">CTDL:</span> ${(p.data_structures || []).join(', ')}</div>
          <div class="row"><span class="label">📖</span> ${p.source}</div>
        </div>`;
      });
      problemInfo.innerHTML = html;
    }

    feedback.textContent = data.feedback || '(no feedback)';

    if (data.evidence && data.evidence.length) {
      evidence.innerHTML = data.evidence.map(e => `
        <div class="evidence-item">
          <div>
            <span class="eid">${e.evidence_id}</span>
            <span class="conf">${(e.confidence * 100).toFixed(0)}%</span>
            <span class="src">[${e.source}]${e.location && e.location.line_start ? ` line ${e.location.line_start}` : ''}</span>
          </div>
          <div style="margin-top:0.15rem;">${e.description}</div>
        </div>
      `).join('');
    }

    if (data.repair_plan && data.repair_plan.steps) {
      repairSteps.innerHTML = data.repair_plan.steps
        .sort((a, b) => a.order - b.order)
        .map(s => `<li>${s.description}${s.location && s.location.line_start ? ` <span style="color:var(--text-dim);font-size:0.75rem;">(line ${s.location.line_start})</span>` : ''}</li>`)
        .join('');
    }

    if (data.semantic_notes && data.semantic_notes.length) {
      const snHtml = data.semantic_notes.map(n =>
        `<div style="background:var(--bg);border-radius:6px;padding:0.4rem 0.7rem;border-left:3px solid var(--purple);font-size:0.8rem;margin-top:0.3rem;">
          <span style="color:var(--purple);font-weight:700;">🔬 ${(n.confidence * 100).toFixed(0)}%</span> ${n.claim}
          ${n.causal_chain && n.causal_chain.length ? `<div style="color:var(--text-dim);font-size:0.75rem;margin-top:0.2rem;">Chain: ${n.causal_chain.join(' → ')}</div>` : ''}
        </div>`
      ).join('');
      const snDiv = document.createElement('div');
      snDiv.innerHTML = `<div class="section-title">🧠 Phân tích ngữ nghĩa</div>${snHtml}`;
      repairSteps.parentNode.insertBefore(snDiv, repairSteps);
    }
  }
});
