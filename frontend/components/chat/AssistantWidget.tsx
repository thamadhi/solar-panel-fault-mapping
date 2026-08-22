'use client';

import { useEffect, useRef, useState } from 'react';
import { usePathname } from 'next/navigation';
import { assistantChat, assistantHistory } from '@/lib/api';
import { Bot, MessageCircle, Send, Sparkles, X } from 'lucide-react';
import styles from './AssistantWidget.module.css';

interface Msg {
  role: 'user' | 'assistant';
  content: string;
}

export default function AssistantWidget() {
  const [open, setOpen]         = useState(false);
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput]       = useState('');
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState('');
  const restored = useRef(false);
  const pathname = usePathname();
  const bodyRef  = useRef<HTMLDivElement>(null);

  // Restore the server-persisted conversation the first time the panel opens
  useEffect(() => {
    if (!open || restored.current) return;
    restored.current = true;
    (async () => {
      try {
        const data = await assistantHistory();
        if (Array.isArray(data.messages)) {
          setMessages(data.messages.map((m: { role?: string; content?: string }) => ({
            role: m.role === 'user' ? ('user' as const) : ('assistant' as const),
            content: m.content ?? '',
          })).filter((m: Msg) => m.content));
        }
      } catch {
        /* history is best-effort */
      }
    })();
  }, [open]);

  // Keep the latest message in view
  useEffect(() => {
    bodyRef.current?.scrollTo({ top: bodyRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages, loading]);

  async function send() {
    const text = input.trim();
    if (!text || loading) return;
    setInput('');
    setError('');
    setMessages(prev => [...prev, { role: 'user', content: text }]);
    setLoading(true);
    try {
      const data = await assistantChat(text, pathname);
      setMessages(prev => [...prev, { role: 'assistant', content: data.reply ?? data.message ?? JSON.stringify(data) }]);
    } catch {
      setError('The assistant is unavailable right now. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      {!open && (
        <button className={styles.bubble} onClick={() => setOpen(true)} aria-label="Open AI assistant">
          <MessageCircle size={24} />
        </button>
      )}

      {open && (
        <div className={styles.panel}>
          <div className={styles.header}>
            <div className={styles.headerInfo}>
              <Bot size={20} />
              <div>
                <div className={styles.title}>Solar PV Assistant</div>
                <div className={styles.subtitle}>{pathname.split('/').pop()?.replace(/^\w/, c => c.toUpperCase()) || 'Dashboard'}</div>
              </div>
            </div>
            <button className={styles.close} onClick={() => setOpen(false)} aria-label="Close assistant">
              <X size={16} />
            </button>
          </div>

          <div className={styles.body} ref={bodyRef}>
            {messages.length === 0 && !loading && (
              <div className={styles.empty}>
                <Sparkles />
                <p>Ask about detected faults, severity, thermal imagery or I-V characteristics.</p>
              </div>
            )}
            {messages.map((m, i) => (
              <div key={i} className={`${styles.msg} ${m.role === 'user' ? styles.msgUser : ''}`}>
                {m.content}
              </div>
            ))}
            {loading && (
              <div className={`${styles.msg} ${styles.thinking}`}>
                <span className="spinner" style={{ width: 14, height: 14, borderWidth: 2 }} />
                Thinking…
              </div>
            )}
            {error && <div className="alert alert-error" style={{ fontSize: '0.75rem' }}>{error}</div>}
          </div>

          <div className={styles.footer}>
            <input
              className={styles.input}
              value={input}
              placeholder="Type a message…"
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } }}
            />
            <button className={styles.send} onClick={send} disabled={loading || !input.trim()} aria-label="Send">
              <Send size={15} />
            </button>
          </div>
        </div>
      )}
    </>
  );
}
