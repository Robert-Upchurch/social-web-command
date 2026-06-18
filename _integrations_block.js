// ----- AI VIDEO / AUDIO TOOL INTEGRATIONS -----
const INTEGRATIONS = {
  frameio:    { label:'Frame.io',    tokenUrl:'https://developer.frame.io/app/tokens',         launchUrl:'https://app.frame.io/',           tokenHint:'fio-u-...',     desc:'Frame.io (Adobe) hosts past YouTube masters, promo edits, and archived footage.' },
  synthesia:  { label:'Synthesia',   tokenUrl:'https://app.synthesia.io/account/api',          launchUrl:'https://app.synthesia.io/',       tokenHint:'API key (paste later)', desc:'Synthesia generates AI avatar videos for training and social.' },
  heygen:     { label:'HeyGen',      tokenUrl:'https://app.heygen.com/settings/api',           launchUrl:'https://app.heygen.com/',         tokenHint:'API key (paste later)', desc:'HeyGen generates multilingual AI avatar videos.' },
  higgsfield: { label:'Higgsfield',  tokenUrl:'https://higgsfield.ai/account',                 launchUrl:'https://higgsfield.ai/',          tokenHint:'API key (paste later)', desc:'Higgsfield generates cinematic and product b-roll for social and ads.' },
  elevenlabs: { label:'ElevenLabs',  tokenUrl:'https://elevenlabs.io/app/settings/api-keys',   launchUrl:'https://elevenlabs.io/app/',      tokenHint:'sk_... (paste later)',  desc:'ElevenLabs generates AI voiceovers and dubbing for video.' },
  suno:       { label:'Suno',        tokenUrl:'https://suno.com/account',                      launchUrl:'https://suno.com/',               tokenHint:'API key (paste later)', desc:'Suno generates AI music and soundtracks.' },
};
function renderIntegrationRow(key, label, desc){
  const cfg = (state.integrations && state.integrations[key]) || {};
  const hasToken = !!cfg.token;
  const hasAccount = !!cfg.account;
  const dot = hasToken ? 'g' : (hasAccount ? 'b' : 'a');
  let status;
  if(hasToken)        status = 'Connected &middot; ' + escapeHtml(cfg.tokenMask || '');
  else if(hasAccount) status = 'Configured &middot; awaiting API key';
  else                status = escapeHtml(desc);
  const btnLabel = hasToken ? 'Manage' : (hasAccount ? 'Add Key' : 'Connect');
  return `
    <div class="rail-item" id="intg_${key}">
      <div class="inbox-meta" style="display:flex; justify-content:space-between; align-items:center; gap:8px">
        <span style="flex:1; min-width:0"><span class="dot ${dot}"></span><strong>${label}</strong> &middot; <span style="color:var(--muted)">${status}</span></span>
        <button class="btn" style="padding:4px 10px; font-size:11px" onclick="openIntegrationModal('${key}')">${btnLabel}</button>
      </div>
    </div>`;
}
function openIntegrationModal(key){
  const def = INTEGRATIONS[key];
  if(!def){ alert('Unknown integration: '+key); return; }
  const cfg = (state.integrations && state.integrations[key]) || {};
  document.getElementById('modalTitle').textContent = 'Connect ' + def.label;
  document.getElementById('modalBody').innerHTML = `
    <div style="font-size:12px; color:var(--muted); margin-bottom:10px; line-height:1.5">
      ${def.desc} You can save the account now and paste the API key later. The key field can stay empty.
      Get a key from <a href="${def.tokenUrl}" target="_blank" style="color:var(--blue)">${def.tokenUrl.replace(/^https?:\/\//,'')}</a>.
    </div>
    <div class="form-row"><label>Account / Workspace</label><input id="intg_account" placeholder="e.g. CTI Group Worldwide" value="${escapeHtml(cfg.account||'')}"></div>
    <div class="form-row"><label>API Key (optional, paste later)</label><input id="intg_token" type="password" placeholder="${cfg.tokenMask ? cfg.tokenMask : def.tokenHint}" autocomplete="off"></div>
    <div class="form-row"><label>Notes (optional)</label><input id="intg_notes" placeholder="e.g. shared with marketing team" value="${escapeHtml(cfg.notes||'')}"></div>
    <div style="font-size:11px; color:var(--muted); margin-top:6px">Keys are stored only in your browser local storage. For production sync, route via Perplexity secure credential vault.</div>
  `;
  document.getElementById('modalFooter').innerHTML = `
    <button class="btn" onclick="closeModal()">Cancel</button>
    ${cfg.token || cfg.account ? `<button class="btn" onclick="disconnectIntegration('${key}')" style="color:var(--accent)">Disconnect</button>` : ''}
    <button class="btn primary" onclick="saveIntegration('${key}')">Save</button>
  `;
  document.getElementById('modalOverlay').classList.add('open');
}
function saveIntegration(key){
  const account = document.getElementById('intg_account').value.trim();
  const token   = document.getElementById('intg_token').value.trim();
  const notes   = document.getElementById('intg_notes').value.trim();
  if(!account){ alert('Account / Workspace required.'); return; }
  state.integrations = state.integrations || {};
  const prev = state.integrations[key] || {};
  state.integrations[key] = {
    account, notes,
    token: token || prev.token || '',
    tokenMask: token ? ('**** ' + token.slice(-4)) : (prev.tokenMask || ''),
    connectedAt: new Date().toISOString(),
  };
  saveState();
  closeModal();
  renderPage();
}
function disconnectIntegration(key){
  if(!confirm('Disconnect this integration? Saved account and key will be cleared from this browser.')) return;
  if(state.integrations && state.integrations[key]) delete state.integrations[key];
  saveState();
  closeModal();
  renderPage();
}
function openFrameIoModal(){ openIntegrationModal('frameio'); }
