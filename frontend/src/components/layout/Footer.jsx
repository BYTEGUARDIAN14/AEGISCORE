/**
 * AEGISCORE — Footer Component
 * Minimal footer with version and brand info.
 */

export function Footer() {
  return (
    <footer style={{
      padding: '16px 24px',
      borderTop: '1px solid var(--border-subtle)',
      backgroundColor: 'var(--bg-base)',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
    }}>
      <span style={{
        fontFamily: 'var(--font-mono)',
        fontSize: '11px',
        color: 'var(--text-tertiary)',
      }}>
        AEGISCORE v1.0.0
      </span>
      <span style={{
        fontFamily: 'var(--font-mono)',
        fontSize: '11px',
        color: 'var(--text-tertiary)',
      }}>
        BYTEAEGIS — byteaegis.in
      </span>
    </footer>
  );
}

export default Footer;
