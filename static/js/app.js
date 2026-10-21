/**
 * Lumina - Customer Support AI Copilot Application Controller
 */

// Application State
const state = {
  tickets: [],
  activeTicket: null,
  activeFilter: 'all',
  searchQuery: '',
  selectedTone: 'Empathetic & Professional',
  analyticsData: null,
  articles: [],
};

// DOM References
const elements = {
  // Header
  groqPill: document.getElementById('groq-pill'),
  groqLabel: document.getElementById('groq-label'),
  nvidiaPill: document.getElementById('nvidia-pill'),
  nvidiaLabel: document.getElementById('nvidia-label'),
  btnTriageAll: document.getElementById('btn-triage-all'),
  btnOpenKb: document.getElementById('btn-open-kb'),
  btnOpenAnalytics: document.getElementById('btn-open-analytics'),
  btnNewTicket: document.getElementById('btn-new-ticket'),
  btnOpenSettings: document.getElementById('btn-open-settings'),

  // Queue
  ticketCountBadge: document.getElementById('ticket-count-badge'),
  queueSearch: document.getElementById('queue-search'),
  filterPills: document.querySelectorAll('.filter-pill'),
  ticketListContainer: document.getElementById('ticket-list-container'),

  // Active Ticket
  activeTicketContainer: document.getElementById('active-ticket-container'),

  // Copilot
  sourcesListContainer: document.getElementById('sources-list-container'),
  aiDraftTextarea: document.getElementById('ai-draft-textarea'),
  draftConfidenceBadge: document.getElementById('draft-confidence-badge'),
  tonePills: document.querySelectorAll('.tone-pill'),
  btnCopyDraft: document.getElementById('btn-copy-draft'),
  btnRegenDraft: document.getElementById('btn-regen-draft'),
  btnSendDraft: document.getElementById('btn-send-draft'),
  kbQuickQuery: document.getElementById('kb-quick-query'),
  btnRunKbSearch: document.getElementById('btn-run-kb-search'),
  kbQuickResults: document.getElementById('kb-quick-results'),

  // Modals
  modalNewTicket: document.getElementById('modal-new-ticket'),
  modalAnalytics: document.getElementById('modal-analytics'),
  modalKb: document.getElementById('modal-kb'),
  modalSettings: document.getElementById('modal-settings'),
  toastContainer: document.getElementById('toast-container'),

  // Modal contents
  formNewTicket: document.getElementById('form-new-ticket'),
  formSettings: document.getElementById('form-settings'),
  btnTestConnection: document.getElementById('btn-test-connection'),
  testConnectionResult: document.getElementById('test-connection-result'),
  kbArticlesContainer: document.getElementById('kb-articles-container'),
  kbModalSearch: document.getElementById('kb-modal-search'),
  btnShowAddArticle: document.getElementById('btn-show-add-article'),
  addArticleContainer: document.getElementById('add-article-container'),
  formAddArticle: document.getElementById('form-add-article'),
  btnCancelAddArticle: document.getElementById('btn-cancel-add-article'),
};

// =============================================================================
// INITIALIZATION
// =============================================================================

document.addEventListener('DOMContentLoaded', async () => {
  setupEventListeners();
  await checkHealth();
  await loadTickets();
  
  // Auto-select first ticket if present
  if (state.tickets.length > 0) {
    selectTicket(state.tickets[0].id);
  }
});

function setupEventListeners() {
  // Search input with debounce
  let searchTimeout = null;
  elements.queueSearch.addEventListener('input', (e) => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      state.searchQuery = e.target.value;
      filterAndRenderTickets();
    }, 200);
  });

  // Filter Pills
  elements.filterPills.forEach(pill => {
    pill.addEventListener('click', () => {
      elements.filterPills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      state.activeFilter = pill.dataset.filter;
      filterAndRenderTickets();
    });
  });

  // Tone selector pills
  elements.tonePills.forEach(pill => {
    pill.addEventListener('click', () => {
      elements.tonePills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      state.selectedTone = pill.dataset.tone;
      if (state.activeTicket) {
        regenerateDraftWithTone(state.selectedTone);
      }
    });
  });

  // Header buttons
  elements.btnTriageAll.addEventListener('click', handleTriageAll);
  elements.btnNewTicket.addEventListener('click', () => openModal('modal-new-ticket'));
  elements.btnOpenAnalytics.addEventListener('click', openAnalyticsModal);
  elements.btnOpenKb.addEventListener('click', openKbModal);
  elements.btnOpenSettings.addEventListener('click', openSettingsModal);

  // Copilot action buttons
  elements.btnCopyDraft.addEventListener('click', handleCopyDraft);
  elements.btnRegenDraft.addEventListener('click', () => {
    if (state.activeTicket) regenerateDraftWithTone(state.selectedTone);
  });
  elements.btnSendDraft.addEventListener('click', handleResolveActiveTicket);

  // KB quick search
  elements.btnRunKbSearch.addEventListener('click', handleKbQuickSearch);
  elements.kbQuickQuery.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleKbQuickSearch();
  });

  // Forms
  elements.formNewTicket.addEventListener('submit', handleCreateTicket);
  elements.formSettings.addEventListener('submit', handleSaveSettings);
  elements.btnTestConnection.addEventListener('click', handleTestConnection);

  // KB Modal Actions
  elements.kbModalSearch.addEventListener('input', handleKbModalSearch);
  elements.btnShowAddArticle.addEventListener('click', () => {
    elements.addArticleContainer.classList.remove('hidden');
  });
  elements.btnCancelAddArticle.addEventListener('click', () => {
    elements.addArticleContainer.classList.add('hidden');
  });
  elements.formAddArticle.addEventListener('submit', handleAddArticle);

  // Modal Closers
  document.querySelectorAll('[data-close]').forEach(btn => {
    btn.addEventListener('click', () => {
      const modalId = btn.getAttribute('data-close');
      closeModal(modalId);
    });
  });

  // Close modals on backdrop click
  document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
    backdrop.addEventListener('click', (e) => {
      if (e.target === backdrop) {
        backdrop.classList.remove('open');
      }
    });
  });
}

// =============================================================================
// HEALTH & ENGINE STATUS
// =============================================================================

async function checkHealth() {
  try {
    const health = await API.getHealth();
    if (health.groq_configured) {
      elements.groqPill.classList.remove('offline');
      elements.groqLabel.textContent = `Groq: ${health.groq_model || 'llama-3.3-70b'}`;
    } else {
      elements.groqPill.classList.add('offline');
      elements.groqLabel.textContent = `Groq: Demo Mode`;
    }

    if (health.using_nvidia_embeddings) {
      elements.nvidiaPill.classList.remove('offline');
      elements.nvidiaLabel.textContent = `NVIDIA NIM: Active`;
    } else {
      elements.nvidiaPill.classList.add('offline');
      elements.nvidiaLabel.textContent = `NVIDIA: Local Hybrid Mode`;
    }
  } catch (err) {
    console.warn('Health check warning:', err);
  }
}

// =============================================================================
// TICKETS MANAGEMENT & QUEUE
// =============================================================================

async function loadTickets() {
  try {
    elements.ticketListContainer.innerHTML = `
      <div class="loading-state">
        <div class="spinner"></div>
        <p>Loading tickets...</p>
      </div>`;
    
    state.tickets = await API.getTickets();
    filterAndRenderTickets();
  } catch (err) {
    elements.ticketListContainer.innerHTML = `<div class="empty-state"><p>Error loading tickets</p></div>`;
    showToast('Failed to load tickets', 'error');
  }
}

function filterAndRenderTickets() {
  let filtered = [...state.tickets];

  // Category / Priority filter
  if (state.activeFilter !== 'all') {
    if (state.activeFilter === 'urgent') {
      filtered = filtered.filter(t => t.priority.toLowerCase() === 'urgent');
    } else {
      filtered = filtered.filter(t => 
        (t.category || '').toLowerCase().includes(state.activeFilter.toLowerCase()) ||
        (t.subject + ' ' + t.body).toLowerCase().includes(state.activeFilter.toLowerCase())
      );
    }
  }

  // Text search
  if (state.searchQuery.trim()) {
    const q = state.searchQuery.toLowerCase().trim();
    filtered = filtered.filter(t => 
      t.id.toLowerCase().includes(q) ||
      t.subject.toLowerCase().includes(q) ||
      t.customer_name.toLowerCase().includes(q) ||
      t.company.toLowerCase().includes(q) ||
      t.body.toLowerCase().includes(q)
    );
  }

  elements.ticketCountBadge.textContent = `${filtered.length} Ticket${filtered.length === 1 ? '' : 's'}`;

  if (filtered.length === 0) {
    elements.ticketListContainer.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">🔍</div>
        <p>No tickets match your filter criteria.</p>
      </div>`;
    return;
  }

  elements.ticketListContainer.innerHTML = filtered.map(t => {
    const isActive = state.activeTicket && state.activeTicket.id === t.id;
    const priClass = `priority-${t.priority.toLowerCase()}`;
    const slaTarget = t.summary ? (t.priority === 'Urgent' ? 'SLA: 15m' : 'SLA: 2h') : 'SLA: 4h';
    
    let sentimentIcon = '😐';
    if (t.sentiment === 'Angry') sentimentIcon = '😡';
    else if (t.sentiment === 'Frustrated') sentimentIcon = '⚠️';
    else if (t.sentiment === 'Satisfied' || t.sentiment === 'Appreciative') sentimentIcon = '😊';

    const statusBadge = t.status === 'Resolved' 
      ? `<span class="badge badge-resolved">Resolved</span>` 
      : (t.status === 'Escalated' 
          ? `<span class="badge badge-escalated">Escalated</span>` 
          : (t.is_triaged ? `<span class="badge badge-pink">Triaged</span>` : `<span class="badge badge-open">New</span>`));

    return `
      <div class="ticket-card ${priClass} ${isActive ? 'active' : ''}" onclick="selectTicket('${t.id}')">
        <div class="card-top-meta">
          <span class="ticket-id">${t.id}</span>
          <div class="ticket-badges">
            <span class="badge badge-${t.priority.toLowerCase()}">${t.priority}</span>
            ${statusBadge}
          </div>
        </div>
        <div class="ticket-subject">${escapeHtml(t.subject)}</div>
        <div class="card-footer-meta">
          <div class="customer-info">
            <span>${sentimentIcon}</span>
            <span>${escapeHtml(t.customer_name)} &bull; ${escapeHtml(t.company)}</span>
          </div>
          <span class="sla-badge">${slaTarget}</span>
        </div>
      </div>
    `;
  }).join('');
}

async function selectTicket(ticketId) {
  try {
    // Find ticket in local cache or fetch fresh
    let ticket = state.tickets.find(t => t.id === ticketId);
    if (!ticket || !ticket.summary) {
      ticket = await API.getTicket(ticketId);
      // Update in cache
      const idx = state.tickets.findIndex(t => t.id === ticketId);
      if (idx !== -1) state.tickets[idx] = ticket;
    }

    state.activeTicket = ticket;
    renderActiveTicket(ticket);
    renderCopilotPanel(ticket);
    filterAndRenderTickets(); // updates active highlight
  } catch (err) {
    showToast('Failed to load ticket details', 'error');
  }
}

// =============================================================================
// ACTIVE TICKET & AI TRIAGE INSPECTOR RENDERER
// =============================================================================

function renderActiveTicket(t) {
  if (!t) return;

  const initials = t.customer_name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
  const dateStr = new Date(t.created_at).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' });
  const isTriaged = t.is_triaged && t.summary;

  let triageContentHtml = '';

  if (isTriaged) {
    const summary = t.summary;
    const escalation = t.escalation || { escalate: false, target_tier: 'Tier 1 Helpdesk', target_department: 'Support Ops', justification: 'Standard workflow', pre_escalation_checklist: [] };
    const urgencyScore = t.sentiment_score ? (100 - t.sentiment_score) : 75;
    const sentimentType = (t.sentiment || 'Neutral').toLowerCase();

    triageContentHtml = `
      <div class="triage-section-title">
        <h3><span>⚡</span> AI Copilot Automated Triage</h3>
        <span class="badge badge-pink">Processed & Grounded</span>
      </div>

      <!-- Triage Grid -->
      <div class="triage-grid">
        <!-- Classification Card -->
        <div class="glass-card">
          <div class="card-title-row">
            <h4><span class="card-icon">🏷️</span> Category & SLA Routing</h4>
          </div>
          <div class="meta-field-row">
            <span class="meta-label">Category:</span>
            <span class="meta-val">${escapeHtml(t.category || 'General')}</span>
          </div>
          <div class="meta-field-row">
            <span class="meta-label">Subcategory:</span>
            <span class="meta-val">${escapeHtml(t.subcategory || 'Standard Inquiry')}</span>
          </div>
          <div class="meta-field-row">
            <span class="meta-label">Priority:</span>
            <span class="badge badge-${t.priority.toLowerCase()}">${t.priority}</span>
          </div>
          <div class="meta-field-row">
            <span class="meta-label">Target SLA:</span>
            <span class="meta-val text-pink">${t.priority === 'Urgent' ? '15 minutes' : '1 hour'}</span>
          </div>
          <div class="emotional-triggers">
            ${(t.tags || []).map(tag => `<span class="trigger-tag">#${escapeHtml(tag)}</span>`).join('')}
          </div>
        </div>

        <!-- Sentiment & Churn Risk Card -->
        <div class="glass-card">
          <div class="card-title-row">
            <h4><span class="card-icon">🎭</span> Sentiment & Churn Risk</h4>
            <span class="badge badge-pink">Urgency: ${urgencyScore}/100</span>
          </div>
          <div class="sentiment-badge-row">
            <span class="sentiment-chip sentiment-${sentimentType}">
              ${t.sentiment === 'Angry' ? '😡' : (t.sentiment === 'Frustrated' ? '⚠️' : '😐')}
              ${t.sentiment || 'Neutral'}
            </span>
            <span class="meta-label">Risk:</span>
            <span class="meta-val text-${t.churn_risk === 'Severe' || t.churn_risk === 'High' ? 'urgent' : 'success'}">${t.churn_risk || 'Low'}</span>
          </div>
          <div class="urgency-bar-container">
            <div class="urgency-bar-track">
              <div class="urgency-bar-fill" style="width: ${urgencyScore}%"></div>
            </div>
          </div>
          <div style="margin-top: 10px;">
            <span class="meta-label" style="font-size: 0.72rem;">Observed Emotion Triggers:</span>
            <div class="emotional-triggers">
              <span class="trigger-tag">Account Risk</span>
              <span class="trigger-tag">Production Blocker</span>
              <span class="trigger-tag">Direct Escalation</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Structured Summary Card -->
      <div class="glass-card">
        <div class="card-title-row">
          <h4><span class="card-icon">📋</span> Structured Technical Summary</h4>
        </div>
        <div class="summary-block">
          <div class="summary-block-title">Core Customer Goal</div>
          <p>${escapeHtml(summary.customer_goal)}</p>
        </div>
        <div class="summary-block">
          <div class="summary-block-title">Observed Symptoms & Error Indicators</div>
          <ul>
            ${(summary.observed_symptoms || []).map(s => `<li>${escapeHtml(s)}</li>`).join('')}
          </ul>
        </div>
        <div class="summary-block">
          <div class="summary-block-title">Actions Attempted by Customer</div>
          <p>${escapeHtml(summary.customer_attempts || 'None reported before outreach.')}</p>
        </div>
        <div class="summary-block">
          <div class="summary-block-title">Probable Root Cause Hypothesis</div>
          <p>${escapeHtml(summary.root_cause_hypothesis || 'Underlying configuration or parameter mismatch.')}</p>
        </div>
        <div class="summary-block" style="margin-bottom: 0;">
          <div class="summary-block-title">Recommended Agent Operational Actions</div>
          <ul>
            ${(summary.action_items || []).map(a => `<li>${escapeHtml(a)}</li>`).join('')}
          </ul>
        </div>
      </div>

      <!-- Escalation Advisory Card -->
      <div class="glass-card escalation-card ${escalation.escalate ? '' : 'escalate-no'}">
        <div class="card-title-row">
          <h4><span class="card-icon">🚨</span> Escalation Advisory</h4>
          <span class="escalation-status-badge ${escalation.escalate ? 'escalate-yes-badge' : 'escalate-no-badge'}">
            ${escalation.escalate ? '⚠️ Escalation Recommended' : '✅ Tier 1 Resolvable'}
          </span>
        </div>
        <div class="meta-field-row">
          <span class="meta-label">Routing Destination:</span>
          <span class="meta-val text-pink">${escapeHtml(escalation.target_tier)} (${escapeHtml(escalation.target_department)})</span>
        </div>
        <div style="margin: 8px 0;">
          <p style="font-size: 0.8rem; color: var(--text-sub); line-height: 1.45;"><strong>Rationale:</strong> ${escapeHtml(escalation.justification)}</p>
        </div>
        <div style="margin-top: 8px;">
          <span class="summary-block-title">Pre-Handover Verification Checklist</span>
          <div style="margin-top: 6px;">
            ${(escalation.pre_escalation_checklist || []).map((check, i) => `
              <label class="checklist-item">
                <input type="checkbox" id="check-${i}" ${i === 0 ? 'checked' : ''}>
                <span>${escapeHtml(check)}</span>
              </label>
            `).join('')}
          </div>
        </div>
      </div>
    `;
  } else {
    // Untriaged ticket state with single-click triage button
    triageContentHtml = `
      <div class="glass-card" style="text-align: center; padding: 24px;">
        <h4 style="margin-bottom: 8px;">⚡ Ticket Not Triaged Yet</h4>
        <p style="font-size: 0.82rem; color: var(--text-muted); margin-bottom: 14px;">
          Execute AI copilot classification, structured extraction, sentiment scoring, and RAG resolution.
        </p>
        <button class="btn btn-primary" onclick="triageCurrentTicket()">
          <span>⚡ Triage This Ticket Now</span>
        </button>
      </div>
    `;
  }

  elements.activeTicketContainer.innerHTML = `
    <!-- Customer Hero Card -->
    <div class="customer-hero-card">
      <div class="customer-identity">
        <div class="customer-avatar">${initials}</div>
        <div class="customer-names">
          <h3>
            <span>${escapeHtml(t.customer_name)}</span>
            <span class="customer-tier-badge">${escapeHtml(t.customer_tier || 'Standard')}</span>
          </h3>
          <div class="customer-email">${escapeHtml(t.customer_email)} &bull; ${escapeHtml(t.company)}</div>
        </div>
      </div>
      <div>
        <span class="badge badge-${t.status.toLowerCase()}">${t.status}</span>
      </div>
    </div>

    <!-- Original Message Card -->
    <div class="ticket-message-card">
      <div class="message-header">
        <h2>${escapeHtml(t.subject)}</h2>
        <span class="message-timestamp">${dateStr}</span>
      </div>
      <div class="message-body">${escapeHtml(t.body)}</div>
    </div>

    <!-- AI Triage Content Section -->
    ${triageContentHtml}
  `;
}

// =============================================================================
// RAG COPILOT & RESPONSE DRAFT RENDERER
// =============================================================================

function renderCopilotPanel(t) {
  if (!t) return;

  const draft = t.resolution_draft;

  // Grounding Sources List
  if (draft && draft.citations && draft.citations.length > 0) {
    elements.sourcesListContainer.innerHTML = draft.citations.map(c => `
      <div class="source-item">
        <div class="source-top">
          <span class="source-doc-id">[${c.doc_id}]</span>
          <span class="source-relevance">${Math.round(c.relevance_score * 100)}% Match</span>
        </div>
        <div class="source-title">${escapeHtml(c.title)}</div>
        <div class="source-snippet">${escapeHtml(c.snippet)}</div>
      </div>
    `).join('');
  } else {
    elements.sourcesListContainer.innerHTML = `
      <div class="source-placeholder">No grounding sources retrieved yet. Triage ticket to fetch knowledge base matches.</div>
    `;
  }

  // AI Draft textarea
  if (draft && draft.draft_reply) {
    elements.aiDraftTextarea.value = draft.draft_reply;
    elements.draftConfidenceBadge.textContent = `${Math.round((draft.confidence || 0.94) * 100)}% Grounded`;
  } else {
    elements.aiDraftTextarea.value = '';
    elements.draftConfidenceBadge.textContent = 'Pending Triage';
  }
}

// =============================================================================
// ACTIONS (TRIAGE, REGENERATE, RESOLVE, CREATE)
// =============================================================================

async function triageCurrentTicket() {
  if (!state.activeTicket) return;
  try {
    showToast(`Triaging ${state.activeTicket.id} with Groq & NVIDIA NIM...`, 'info');
    const result = await API.triageTicket(state.activeTicket.id);
    
    // Update local ticket model
    state.activeTicket.summary = result.summary;
    state.activeTicket.classification = result.classification;
    state.activeTicket.sentiment = result.sentiment.sentiment;
    state.activeTicket.sentiment_score = result.sentiment.score;
    state.activeTicket.churn_risk = result.sentiment.churn_risk;
    state.activeTicket.category = result.classification.category;
    state.activeTicket.priority = result.classification.priority;
    state.activeTicket.escalation = result.escalation;
    state.activeTicket.resolution_draft = result.rag_draft;
    state.activeTicket.is_triaged = true;

    renderActiveTicket(state.activeTicket);
    renderCopilotPanel(state.activeTicket);
    filterAndRenderTickets();

    showToast(`Ticket ${state.activeTicket.id} triaged successfully!`, 'success');
  } catch (err) {
    showToast('Failed to triage ticket', 'error');
  }
}

async function handleTriageAll() {
  try {
    elements.btnTriageAll.disabled = true;
    elements.btnTriageAll.innerHTML = `<span class="spinner" style="width:14px;height:14px;border-width:2px;"></span> Triaging...`;
    showToast('Batch triaging all tickets...', 'info');

    const res = await API.triageAllTickets();
    await loadTickets();
    
    if (state.activeTicket) {
      selectTicket(state.activeTicket.id);
    }

    elements.btnTriageAll.disabled = false;
    elements.btnTriageAll.innerHTML = `<span class="btn-icon">⚡</span><span>Auto-Triage All</span>`;
    showToast(`Batch triage complete! (${res.triaged_count} tickets processed)`, 'success');
  } catch (err) {
    elements.btnTriageAll.disabled = false;
    elements.btnTriageAll.innerHTML = `<span class="btn-icon">⚡</span><span>Auto-Triage All</span>`;
    showToast('Batch triage encountered an error', 'error');
  }
}

async function regenerateDraftWithTone(tone) {
  if (!state.activeTicket) return;
  try {
    elements.aiDraftTextarea.value = "Regenerating response with " + tone + " tone...";
    elements.draftConfidenceBadge.textContent = "Synthesizing...";
    
    const draft = await API.generateDraftReply(state.activeTicket.id, tone);
    state.activeTicket.resolution_draft = draft;
    renderCopilotPanel(state.activeTicket);
    showToast(`Draft updated with ${tone} tone`, 'success');
  } catch (err) {
    showToast('Failed to regenerate draft', 'error');
  }
}

async function handleResolveActiveTicket() {
  if (!state.activeTicket) return;
  try {
    await API.resolveTicket(state.activeTicket.id);
    state.activeTicket.status = "Resolved";
    renderActiveTicket(state.activeTicket);
    filterAndRenderTickets();
    showToast(`Ticket ${state.activeTicket.id} marked as Resolved!`, 'success');
  } catch (err) {
    showToast('Failed to resolve ticket', 'error');
  }
}

function handleCopyDraft() {
  const text = elements.aiDraftTextarea.value;
  if (!text) {
    showToast('No draft text to copy', 'error');
    return;
  }
  navigator.clipboard.writeText(text);
  showToast('Copied draft reply to clipboard!', 'success');
}

async function handleCreateTicket(e) {
  e.preventDefault();
  const payload = {
    customer_name: document.getElementById('nt-name').value,
    customer_email: document.getElementById('nt-email').value,
    company: document.getElementById('nt-company').value,
    customer_tier: document.getElementById('nt-tier').value,
    priority: document.getElementById('nt-priority').value,
    subject: document.getElementById('nt-subject').value,
    body: document.getElementById('nt-body').value
  };

  try {
    showToast('Creating and triaging ticket...', 'info');
    const newTicket = await API.createTicket(payload);
    closeModal('modal-new-ticket');
    elements.formNewTicket.reset();

    // Reload tickets and auto-select newly created ticket
    await loadTickets();
    selectTicket(newTicket.id);
    showToast(`Ticket ${newTicket.id} created & auto-triaged!`, 'success');
  } catch (err) {
    showToast('Failed to create ticket', 'error');
  }
}

// =============================================================================
// KNOWLEDGE BASE MODAL & SEARCH
// =============================================================================

async function openKbModal() {
  openModal('modal-kb');
  try {
    state.articles = await API.getKnowledgeBase();
    renderKbArticles(state.articles);
  } catch (err) {
    showToast('Failed to load knowledge base', 'error');
  }
}

function renderKbArticles(articles) {
  if (!articles || articles.length === 0) {
    elements.kbArticlesContainer.innerHTML = '<p class="empty-state">No articles found.</p>';
    return;
  }

  elements.kbArticlesContainer.innerHTML = articles.map(a => `
    <div class="kb-card">
      <div class="kb-card-top">
        <span class="source-doc-id">${a.id}</span>
        <span class="badge badge-pink">${escapeHtml(a.category)}</span>
      </div>
      <div class="kb-card-title">${escapeHtml(a.title)}</div>
      <div class="kb-card-snippet">${escapeHtml(a.content.substring(0, 220))}...</div>
      <div class="emotional-triggers" style="margin-top: 8px;">
        ${(a.tags || []).map(t => `<span class="trigger-tag">#${escapeHtml(t)}</span>`).join('')}
      </div>
    </div>
  `).join('');
}

function handleKbModalSearch(e) {
  const q = e.target.value.toLowerCase().trim();
  if (!q) {
    renderKbArticles(state.articles);
    return;
  }
  const filtered = state.articles.filter(a => 
    a.title.toLowerCase().includes(q) ||
    a.content.toLowerCase().includes(q) ||
    a.category.toLowerCase().includes(q) ||
    (a.tags || []).some(t => t.toLowerCase().includes(q))
  );
  renderKbArticles(filtered);
}

async function handleAddArticle(e) {
  e.preventDefault();
  const tagsStr = document.getElementById('new-art-tags').value;
  const tags = tagsStr ? tagsStr.split(',').map(t => t.trim()).filter(Boolean) : [];
  
  const payload = {
    title: document.getElementById('new-art-title').value,
    category: document.getElementById('new-art-category').value,
    content: document.getElementById('new-art-content').value,
    tags: tags
  };

  try {
    showToast('Indexing article into vector store...', 'info');
    await API.addKnowledgeArticle(payload);
    elements.formAddArticle.reset();
    elements.addArticleContainer.classList.add('hidden');
    state.articles = await API.getKnowledgeBase();
    renderKbArticles(state.articles);
    showToast('Article indexed into knowledge base!', 'success');
  } catch (err) {
    showToast('Failed to add article', 'error');
  }
}

async function handleKbQuickSearch() {
  const q = elements.kbQuickQuery.value.trim();
  if (!q) return;

  try {
    elements.kbQuickResults.innerHTML = '<div class="loading-state"><div class="spinner"></div></div>';
    const data = await API.searchKnowledgeBase(q);
    
    if (!data.results || data.results.length === 0) {
      elements.kbQuickResults.innerHTML = '<div style="color:var(--text-muted);padding:8px;">No matching articles.</div>';
      return;
    }

    elements.kbQuickResults.innerHTML = data.results.map(r => `
      <div class="source-item">
        <div class="source-top">
          <span class="source-doc-id">[${r.doc_id}]</span>
          <span class="source-relevance">${Math.round(r.relevance_score * 100)}% Relevance</span>
        </div>
        <div class="source-title">${escapeHtml(r.title)}</div>
        <div class="source-snippet">${escapeHtml(r.snippet)}</div>
      </div>
    `).join('');
  } catch (err) {
    elements.kbQuickResults.innerHTML = '<div style="color:#ff3366;padding:8px;">Error querying knowledge base.</div>';
  }
}

// =============================================================================
// ANALYTICS & ROI METRICS
// =============================================================================

async function openAnalyticsModal() {
  openModal('modal-analytics');
  try {
    const data = await API.getAnalytics();
    state.analyticsData = data;
    renderAnalytics(data);
  } catch (err) {
    showToast('Failed to load analytics', 'error');
  }
}

function renderAnalytics(data) {
  document.getElementById('kpi-hours-saved').textContent = `${data.estimated_hours_saved} hrs`;
  document.getElementById('kpi-deflection-rate').textContent = `${data.deflection_rate_pct}%`;
  document.getElementById('kpi-response-time').textContent = `${data.avg_first_response_time_min} min`;
  document.getElementById('kpi-escalation-rate').textContent = `${data.escalation_rate_pct}%`;

  // Render Category distribution bars
  const catContainer = document.getElementById('dist-categories');
  const catEntries = Object.entries(data.category_distribution);
  const maxCat = Math.max(...catEntries.map(e => e[1]), 1);

  catContainer.innerHTML = catEntries.map(([cat, count]) => {
    const pct = Math.round((count / maxCat) * 100);
    return `
      <div class="dist-row">
        <div class="dist-labels">
          <span>${escapeHtml(cat)}</span>
          <span style="font-weight:700;">${count}</span>
        </div>
        <div class="dist-track">
          <div class="dist-fill" style="width: ${pct}%"></div>
        </div>
      </div>
    `;
  }).join('');

  // Render Sentiment distribution bars
  const sentContainer = document.getElementById('dist-sentiments');
  const sentEntries = Object.entries(data.sentiment_distribution);
  const maxSent = Math.max(...sentEntries.map(e => e[1]), 1);

  sentContainer.innerHTML = sentEntries.map(([sent, count]) => {
    const pct = Math.round((count / maxSent) * 100);
    return `
      <div class="dist-row">
        <div class="dist-labels">
          <span>${escapeHtml(sent)}</span>
          <span style="font-weight:700;">${count}</span>
        </div>
        <div class="dist-track">
          <div class="dist-fill" style="width: ${pct}%; background: linear-gradient(90deg, #34d399, #ff2d75);"></div>
        </div>
      </div>
    `;
  }).join('');
}

// =============================================================================
// SETTINGS & CONNECTION TEST
// =============================================================================

function openSettingsModal() {
  openModal('modal-settings');
  elements.testConnectionResult.classList.add('hidden');
}

async function handleTestConnection() {
  const groqKey = document.getElementById('cfg-groq-key').value;
  const nvidiaKey = document.getElementById('cfg-nvidia-key').value;

  elements.testConnectionResult.classList.remove('hidden');
  elements.testConnectionResult.innerHTML = `
    <div style="display:flex;align-items:center;gap:8px;">
      <div class="spinner" style="width:16px;height:16px;border-width:2px;"></div>
      <span>Pinging Groq LLM API and NVIDIA NIM Embeddings endpoints...</span>
    </div>
  `;

  try {
    const res = await API.testConnections({
      groq_api_key: groqKey || undefined,
      nvidia_api_key: nvidiaKey || undefined
    });

    const groqIcon = res.groq_connected ? '✅' : '⚠️';
    const nvidiaIcon = res.nvidia_connected ? '✅' : 'ℹ️';

    elements.testConnectionResult.innerHTML = `
      <div style="display:flex;flex-direction:column;gap:6px;">
        <div>${groqIcon} <strong>Groq (${res.groq_model || 'LLM'}):</strong> ${res.groq_message} ${res.groq_latency_ms ? `<em>(${res.groq_latency_ms}ms)</em>` : ''}</div>
        <div>${nvidiaIcon} <strong>NVIDIA NIM (${res.nvidia_model || 'Embeddings'}):</strong> ${res.nvidia_message} ${res.nvidia_latency_ms ? `<em>(${res.nvidia_latency_ms}ms)</em>` : ''}</div>
      </div>
    `;
  } catch (err) {
    elements.testConnectionResult.innerHTML = `<span style="color:#ff3366;">Connection test failed: ${err.message}</span>`;
  }
}

async function handleSaveSettings(e) {
  e.preventDefault();
  const groqKey = document.getElementById('cfg-groq-key').value;
  const groqModel = document.getElementById('cfg-groq-model').value;
  const nvidiaKey = document.getElementById('cfg-nvidia-key').value;
  const nvidiaModel = document.getElementById('cfg-nvidia-model').value;

  try {
    showToast('Saving API configuration...', 'info');
    await API.updateSettings({
      groq_api_key: groqKey || undefined,
      groq_model: groqModel || undefined,
      nvidia_api_key: nvidiaKey || undefined,
      nvidia_embedding_model: nvidiaModel || undefined
    });
    
    closeModal('modal-settings');
    await checkHealth();
    showToast('Settings updated successfully!', 'success');
  } catch (err) {
    showToast('Failed to save settings', 'error');
  }
}

// =============================================================================
// MODAL & TOAST HELPERS
// =============================================================================

function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.classList.add('open');
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.classList.remove('open');
}

function showToast(message, type = 'info') {
  const toast = document.createElement('div');
  toast.className = 'toast';
  const icon = type === 'success' ? '✅' : (type === 'error' ? '❌' : '⚡');
  toast.innerHTML = `<span>${icon}</span><span>${escapeHtml(message)}</span>`;
  
  elements.toastContainer.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
