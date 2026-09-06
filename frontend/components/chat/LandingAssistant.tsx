'use client';

import { useEffect, useRef, useState } from 'react';
import { Send, X } from 'lucide-react';
import BotAvatar from '@/components/marketing/BotAvatar';
import styles from './LandingAssistant.module.css';

interface Msg { role: 'user' | 'bot'; content: string }

/**
 * A lightweight, client-only FAQ guide for visitors landing on the marketing
 * site — distinct from the authenticated Solar PV Assistant in the dashboard
 * (which needs a login and talks to the real inference backend). This one
 * answers common "what is this" questions instantly, with no server round
 * trip, so it works the moment the page loads.
 */
const FAQ: { keywords: string[]; answer: string }[] = [
  {
    keywords: ['what', 'do', 'does', 'insight', 'product', 'platform'],
    answer: "Insight watches every string in your solar array and answers four questions: what's wrong, where it is, how serious it is, and what to do about it — combining electrical readings with thermal imagery instead of relying on either alone.",
  },
  {
    keywords: ['hardware', 'sensor', 'install', 'equipment', 'device'],
    answer: 'No proprietary hardware. Insight runs on the data and thermal imagery your plant already produces — nothing to bolt onto the panels.',
  },
  {
    keywords: ['accurate', 'accuracy', 'reliable', 'confidence'],
    answer: "Around 99.2% detection accuracy in our validation set, with analysis returned in under 2 seconds. Every prediction also comes with a plain-language explanation, not just a score.",
  },
  {
    keywords: ['open', 'source', 'github', 'license'],
    answer: "We're building this in the open — there isn't an end-to-end open pipeline for solar fault detection, localisation, severity and rectification today, especially not for markets like Sri Lanka, and we're aiming to close that gap.",
  },
  {
    keywords: ['sri', 'lanka', 'where', 'based'],
    answer: 'The team is based in Sri Lanka, building this out of an academic partnership between the Informatics Institute of Technology and Robert Gordon University, Aberdeen.',
  },
  {
    keywords: ['price', 'pricing', 'cost', 'free', 'pay'],
    answer: "We're pre-launch and validating with early plant partners rather than publishing a price list yet. Message us via LinkedIn and we'll talk through a pilot.",
  },
  {
    keywords: ['start', 'try', 'demo', 'access', 'login', 'sign'],
    answer: 'Hit "Enter Dashboard" in the top right to explore it — or scroll to "See it in action" below for a quick look first.',
  },
  {
    keywords: ['team', 'who', 'built', 'company', 'contact'],
    answer: "We're a small team out of Sri Lanka's solar-engineering and AI research community. Reach us through the OpenSunray LinkedIn page — link's in the footer.",
  },
];

const FALLBACK = "That one's outside what I can answer here — try one of the topics below, or reach the team on LinkedIn (link in the footer) and they'll get back to you.";

const SUGGESTIONS = ['What does Insight do?', 'Do I need new hardware?', 'Is this open source?', 'How accurate is it?'];

function answerFor(question: string): string {
  const q = question.toLowerCase();
  let best: { score: number; answer: string } | null = null;
  for (const entry of FAQ) {
    const score = entry.keywords.reduce((n, k) => n + (q.includes(k) ? 1 : 0), 0);
    if (score > 0 && (!best || score > best.score)) best = { score, answer: entry.answer };
  }
  return best?.answer ?? FALLBACK;
}

export default function LandingAssistant() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState('');
  const bodyRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bodyRef.current?.scrollTo({ top: bodyRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages]);

  function ask(text: string) {
    const q = text.trim();
    if (!q) return;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: q }, { role: 'bot', content: answerFor(q) }]);
  }

  return (
    <>
      {!open && (
        <button className={styles.bubble} onClick={() => setOpen(true)} aria-label="Ask about OpenSunray Insight">
          <span className={styles.pulse} aria-hidden="true" />
          <BotAvatar size={28} />
        </button>
      )}

      {open && (
        <div className={styles.panel}>
          <div className={styles.header}>
            <div className={styles.headerInfo}>
              <BotAvatar size={22} />
              <div>
                <div className={styles.title}>Ask about Insight</div>
                <div className={styles.subtitle}>Usually answers instantly</div>
              </div>
            </div>
            <button className={styles.close} onClick={() => setOpen(false)} aria-label="Close">
              <X size={16} />
            </button>
          </div>

          <div className={styles.body} ref={bodyRef}>
            {messages.length === 0 && (
              <div className={styles.empty}>
                <p>Curious what Insight actually does? Ask, or pick a question below.</p>
                <div className={styles.chips}>
                  {SUGGESTIONS.map(s => (
                    <button key={s} className={styles.chip} onClick={() => ask(s)}>{s}</button>
                  ))}
                </div>
              </div>
            )}
            {messages.map((m, i) => (
              <div key={i} className={`${styles.msg} ${m.role === 'user' ? styles.msgUser : ''}`}>
                {m.content}
              </div>
            ))}
          </div>

          <div className={styles.footer}>
            <input
              className={styles.input}
              value={input}
              placeholder="Ask a question…"
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter') ask(input); }}
            />
            <button className={styles.send} onClick={() => ask(input)} disabled={!input.trim()} aria-label="Send">
              <Send size={15} />
            </button>
          </div>
        </div>
      )}
    </>
  );
}
