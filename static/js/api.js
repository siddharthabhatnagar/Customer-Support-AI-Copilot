/**
 * API Client for Customer Support AI Copilot
 */
const API = {
  async getHealth() {
    const res = await fetch('/api/health');
    return res.json();
  },

  async getTickets(filters = {}) {
    const params = new URLSearchParams();
    if (filters.status) params.append('status', filters.status);
    if (filters.priority) params.append('priority', filters.priority);
    if (filters.category) params.append('category', filters.category);
    if (filters.search) params.append('search', filters.search);
    
    const url = `/api/tickets${params.toString() ? '?' + params.toString() : ''}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to load tickets');
    return res.json();
  },

  async getTicket(ticketId) {
    const res = await fetch(`/api/tickets/${ticketId}`);
    if (!res.ok) throw new Error('Failed to load ticket details');
    return res.json();
  },

  async createTicket(payload) {
    const res = await fetch('/api/tickets', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Failed to create ticket');
    return res.json();
  },

  async triageTicket(ticketId) {
    const res = await fetch(`/api/tickets/${ticketId}/triage`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error('Failed to triage ticket');
    return res.json();
  },

  async triageAllTickets() {
    const res = await fetch('/api/tickets/triage-all', {
      method: 'POST'
    });
    if (!res.ok) throw new Error('Failed to triage all tickets');
    return res.json();
  },

  async resolveTicket(ticketId) {
    const res = await fetch(`/api/tickets/${ticketId}/resolve`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error('Failed to resolve ticket');
    return res.json();
  },

  async generateDraftReply(ticketId, tone) {
    const res = await fetch(`/api/tickets/${ticketId}/draft-reply`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tone })
    });
    if (!res.ok) throw new Error('Failed to generate draft reply');
    return res.json();
  },

  async getKnowledgeBase() {
    const res = await fetch('/api/knowledge-base');
    if (!res.ok) throw new Error('Failed to load knowledge base');
    return res.json();
  },

  async addKnowledgeArticle(payload) {
    const res = await fetch('/api/knowledge-base', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Failed to add article');
    return res.json();
  },

  async searchKnowledgeBase(query) {
    const res = await fetch(`/api/knowledge-base/search?q=${encodeURIComponent(query)}`);
    if (!res.ok) throw new Error('Failed to query knowledge base');
    return res.json();
  },

  async getAnalytics() {
    const res = await fetch('/api/analytics');
    if (!res.ok) throw new Error('Failed to fetch analytics');
    return res.json();
  },

  async updateSettings(payload) {
    const res = await fetch('/api/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Failed to update settings');
    return res.json();
  },

  async testConnections(payload) {
    const res = await fetch('/api/settings/test', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Connection test failed');
    return res.json();
  }
};
