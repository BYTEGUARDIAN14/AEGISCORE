/**
 * AEGISCORE — Tooltip Component
 * Simple hover tooltip with dark background.
 */
import { useState, useRef, useEffect } from 'react';

export function Tooltip({ children, content, position = 'top' }) {
  const [visible, setVisible] = useState(false);
  const [coords, setCoords] = useState({ top: 0, left: 0 });
  const triggerRef = useRef(null);
  const tooltipRef = useRef(null);

  useEffect(() => {
    if (visible && triggerRef.current && tooltipRef.current) {
      const triggerRect = triggerRef.current.getBoundingClientRect();
      const tooltipRect = tooltipRef.current.getBoundingClientRect();

      let top = 0;
      let left = 0;

      switch (position) {
        case 'top':
          top = triggerRect.top - tooltipRect.height - 8;
          left = triggerRect.left + (triggerRect.width - tooltipRect.width) / 2;
          break;
        case 'bottom':
          top = triggerRect.bottom + 8;
          left = triggerRect.left + (triggerRect.width - tooltipRect.width) / 2;
          break;
        case 'left':
          top = triggerRect.top + (triggerRect.height - tooltipRect.height) / 2;
          left = triggerRect.left - tooltipRect.width - 8;
          break;
        case 'right':
          top = triggerRect.top + (triggerRect.height - tooltipRect.height) / 2;
          left = triggerRect.right + 8;
          break;
        default:
          break;
      }

      setCoords({ top, left });
    }
  }, [visible, position]);

  if (!content) return children;

  return (
    <span
      ref={triggerRef}
      onMouseEnter={() => setVisible(true)}
      onMouseLeave={() => setVisible(false)}
      style={{ position: 'relative', display: 'inline-flex' }}
    >
      {children}
      {visible && (
        <div
          ref={tooltipRef}
          style={{
            position: 'fixed',
            top: `${coords.top}px`,
            left: `${coords.left}px`,
            backgroundColor: 'var(--bg-elevated)',
            border: '1px solid var(--border-default)',
            borderRadius: '6px',
            padding: '6px 10px',
            fontFamily: 'var(--font-sans)',
            fontSize: '11px',
            color: 'var(--text-secondary)',
            whiteSpace: 'nowrap',
            zIndex: 9999,
            pointerEvents: 'none',
          }}
        >
          {content}
        </div>
      )}
    </span>
  );
}

export default Tooltip;
