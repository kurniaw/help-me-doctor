<template>
  <div class="auth-shell">
    <!-- Left: Brand panel (desktop only) -->
    <aside class="auth-panel">
      <div class="panel-inner">
        <div class="panel-logo">
          <div class="logo-mark">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
            </svg>
          </div>
          <span class="logo-name">Help Me Doctor</span>
          <span class="logo-badge">SG</span>
        </div>

        <div class="panel-hero">
          <h1 class="panel-headline">The right care,<br>at the right time.</h1>
          <p class="panel-sub">
            AI-powered triage connecting you with the right Singapore healthcare provider — instantly.
          </p>
        </div>

        <ul class="panel-features">
          <li>
            <span class="feature-icon">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            </span>
            <div>
              <strong>Instant urgency assessment</strong>
              <p>CRITICAL · HIGH · MEDIUM · LOW triage in seconds</p>
            </div>
          </li>
          <li>
            <span class="feature-icon">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
            </span>
            <div>
              <strong>CHAS clinic &amp; hospital matching</strong>
              <p>Nearest subsidised clinic or specialist referral</p>
            </div>
          </li>
          <li>
            <span class="feature-icon">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
            </span>
            <div>
              <strong>Medical &amp; legal guidance</strong>
              <p>Workplace injuries, forensic cases &amp; more</p>
            </div>
          </li>
        </ul>

        <div class="panel-emergency">
          <span class="emergency-label">Singapore Emergency Lines</span>
          <div class="emergency-numbers">
            <span>🚑 Ambulance: 995</span>
            <span>🚔 Police: 999</span>
            <span>SingHealth: 6222 3322</span>
          </div>
        </div>
      </div>
    </aside>

    <!-- Right: Form -->
    <main class="auth-form-panel">
      <div class="form-panel-inner">
        <slot />
      </div>
      <Toast position="top-right" />
    </main>
  </div>
</template>

<style scoped>
.auth-shell {
  min-height: 100vh;
  display: flex;
  background: var(--hmd-surface);
}

/* ── Left brand panel ── */
.auth-panel {
  display: none;
  width: 400px;
  flex-shrink: 0;
  background: linear-gradient(160deg, #1e3a8a 0%, #2563eb 65%, #3b82f6 100%);
  position: relative;
  overflow: hidden;
}

.auth-panel::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 70% 50% at 75% 15%, rgba(255,255,255,0.1) 0%, transparent 55%),
    radial-gradient(ellipse 50% 70% at 15% 85%, rgba(30,58,138,0.6) 0%, transparent 60%);
  pointer-events: none;
}

.panel-inner {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 2.25rem 2rem;
  gap: 2.25rem;
  color: white;
}

.panel-logo {
  display: flex;
  align-items: center;
  gap: 0.625rem;
}

.logo-mark {
  width: 34px;
  height: 34px;
  background: rgba(255,255,255,0.18);
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  border: 1px solid rgba(255,255,255,0.25);
}

.logo-name {
  font-size: 1.0625rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.logo-badge {
  font-size: 0.625rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  background: rgba(255,255,255,0.18);
  border: 1px solid rgba(255,255,255,0.28);
  padding: 0.125rem 0.4rem;
  border-radius: 4px;
}

.panel-hero { flex: 1; display: flex; flex-direction: column; justify-content: center; }

.panel-headline {
  font-size: 1.875rem;
  font-weight: 700;
  line-height: 1.2;
  letter-spacing: -0.03em;
  margin: 0 0 0.875rem;
}

.panel-sub {
  font-size: 0.9rem;
  line-height: 1.65;
  opacity: 0.78;
  margin: 0;
  max-width: 300px;
}

.panel-features {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 1.125rem;
}

.panel-features li {
  display: flex;
  align-items: flex-start;
  gap: 0.875rem;
}

.feature-icon {
  width: 30px;
  height: 30px;
  background: rgba(255,255,255,0.14);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 2px;
}

.panel-features li strong {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  margin-bottom: 0.125rem;
}

.panel-features li p {
  font-size: 0.8rem;
  opacity: 0.68;
  margin: 0;
  line-height: 1.4;
}

.panel-emergency {
  border-top: 1px solid rgba(255,255,255,0.15);
  padding-top: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.emergency-label {
  font-size: 0.6875rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  opacity: 0.55;
}

.emergency-numbers {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  font-size: 0.8125rem;
  font-weight: 500;
  opacity: 0.82;
}

/* ── Right form panel ── */
.auth-form-panel {
  flex: 1;
  background: #fafbfc;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 1.5rem;
  min-height: 100vh;
}

.form-panel-inner {
  width: 100%;
  max-width: 400px;
}

@media (min-width: 900px) {
  .auth-panel { display: flex; }
  .auth-form-panel { background: var(--hmd-surface); }
}
</style>
