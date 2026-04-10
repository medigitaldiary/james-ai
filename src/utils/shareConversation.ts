import type { Message } from '../types'

const DISCLAIMER =
  'Investments in bonds are subject to market risks. Please read all offer documents carefully before investing. ' +
  'Past returns are not indicative of future performance. BondScanner is a SEBI-registered Online Bond Platform ' +
  'Provider (OBPP). This is not investment advice.'

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

function formatMessage(content: string): string {
  // Bold: **text**
  let html = escapeHtml(content)
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    // Bullet points: lines starting with * or -
    .replace(/^[*-]\s+(.+)$/gm, '<li>$1</li>')
  // Wrap consecutive <li> in <ul>
  html = html.replace(/(<li>.*<\/li>\n?)+/g, (match) => `<ul>${match}</ul>`)
  // Newlines to <br>
  html = html.replace(/\n/g, '<br>')
  return html
}

function formatDate(date: Date): string {
  return date.toLocaleString('en-IN', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit', hour12: true,
  })
}

export function shareConversation(messages: Message[]): void {
  const exportedAt = formatDate(new Date())
  const hasDisclaimer = messages.some((m) => m.showDisclaimer)

  const messageRows = messages
    .map((msg) => {
      const isUser = msg.role === 'user'
      return `
        <div class="message ${isUser ? 'user-message' : 'james-message'}">
          <div class="message-label">${isUser ? 'You' : 'James AI'}</div>
          <div class="bubble ${isUser ? 'bubble-user' : 'bubble-james'}">
            ${formatMessage(msg.content)}
          </div>
          <div class="message-time">${formatDate(msg.timestamp)}</div>
        </div>
      `
    })
    .join('')

  const html = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>James AI Conversation — BondScanner</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: #fff;
      color: #1a1a2e;
      padding: 40px;
      max-width: 780px;
      margin: 0 auto;
    }

    /* Header */
    .header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding-bottom: 20px;
      border-bottom: 2px solid #e8eaf0;
      margin-bottom: 32px;
    }
    .header-left { display: flex; align-items: center; gap: 12px; }
    .header-logo {
      width: 36px; height: 36px; background: #2d3a8c;
      border-radius: 50%; display: flex; align-items: center;
      justify-content: center; color: white; font-weight: 700; font-size: 16px;
    }
    .header-title { font-size: 18px; font-weight: 700; color: #2d3a8c; }
    .header-subtitle { font-size: 12px; color: #8890a4; margin-top: 2px; }
    .header-date { font-size: 12px; color: #8890a4; text-align: right; }

    /* Messages */
    .messages { display: flex; flex-direction: column; gap: 20px; }

    .message { display: flex; flex-direction: column; max-width: 75%; }
    .user-message { align-self: flex-end; align-items: flex-end; }
    .james-message { align-self: flex-start; align-items: flex-start; }

    .message-label {
      font-size: 11px; font-weight: 600; color: #8890a4;
      margin-bottom: 4px; letter-spacing: 0.3px;
    }
    .james-message .message-label { color: #2d3a8c; }

    .bubble {
      padding: 12px 16px;
      border-radius: 16px;
      font-size: 13.5px;
      line-height: 1.6;
    }
    .bubble-user {
      background: #2d3a8c;
      color: #fff;
      border-bottom-right-radius: 4px;
    }
    .bubble-james {
      background: #f5f6fa;
      color: #1a1a2e;
      border: 1px solid #e8eaf0;
      border-top-left-radius: 4px;
    }
    .bubble ul { padding-left: 18px; margin-top: 6px; }
    .bubble li { margin-bottom: 4px; }

    .message-time {
      font-size: 10px; color: #b0b5c4; margin-top: 4px;
    }

    /* Disclaimer */
    .disclaimer {
      margin-top: 40px;
      padding: 14px 16px;
      background: #fffbeb;
      border: 1px solid #fcd34d;
      border-radius: 10px;
      font-size: 11.5px;
      color: #92400e;
      line-height: 1.6;
    }
    .disclaimer strong { display: block; margin-bottom: 4px; }

    /* Footer */
    .footer {
      margin-top: 28px;
      padding-top: 16px;
      border-top: 1px solid #e8eaf0;
      font-size: 11px;
      color: #b0b5c4;
      display: flex;
      justify-content: space-between;
    }

    @media print {
      body { padding: 24px; }
      @page { margin: 1.5cm; }
    }
  </style>
</head>
<body>
  <!-- Header -->
  <div class="header">
    <div class="header-left">
      <div class="header-logo">J</div>
      <div>
        <div class="header-title">James AI</div>
        <div class="header-subtitle">BondScanner · SEBI-registered OBPP</div>
      </div>
    </div>
    <div class="header-date">
      Exported on<br/>${exportedAt}
    </div>
  </div>

  <!-- Messages -->
  <div class="messages">
    ${messageRows}
  </div>

  <!-- SEBI Disclaimer (if any investment topic was discussed) -->
  ${
    hasDisclaimer
      ? `<div class="disclaimer">
           <strong>⚠️ Investment Disclaimer</strong>
           ${escapeHtml(DISCLAIMER)}
         </div>`
      : ''
  }

  <!-- Footer -->
  <div class="footer">
    <span>Generated by James AI · bondscanner.com</span>
    <span>${exportedAt}</span>
  </div>

  <script>window.onload = () => window.print()</script>
</body>
</html>
  `.trim()

  const blob = new Blob([html], { type: 'text/html' })
  const url = URL.createObjectURL(blob)
  const win = window.open(url, '_blank')
  // Clean up the object URL after the window loads
  if (win) {
    win.onload = () => setTimeout(() => URL.revokeObjectURL(url), 1000)
  }
}
