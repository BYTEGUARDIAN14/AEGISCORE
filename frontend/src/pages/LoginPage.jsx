/**
 * AEGISCORE — LoginPage
 * Standalone login page with email/password form.
 */
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import Button from '../components/ui/Button';

export function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const success = await login(email, password);
    if (success) {
      navigate('/dashboard');
    } else {
      setError('Invalid email or password');
    }
    setLoading(false);
  };

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: 'var(--bg-base)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
    }}>
      <div style={{
        width: '360px',
        backgroundColor: 'var(--bg-surface)',
        border: '1px solid var(--border-subtle)',
        borderRadius: '10px',
        padding: '40px 32px',
      }}>
        {/* Logo */}
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '10px',
            marginBottom: '8px',
          }}>
            <svg width="24" height="24" viewBox="0 0 20 20" fill="none">
              <path d="M10 1L18 5.5V14.5L10 19L2 14.5V5.5L10 1Z" stroke="var(--accent)" strokeWidth="1.5" strokeLinejoin="round"/>
              <path d="M10 5L14 7.5V12.5L10 15L6 12.5V7.5L10 5Z" stroke="var(--accent)" strokeWidth="1.5" strokeLinejoin="round"/>
              <circle cx="10" cy="10" r="1.5" fill="var(--accent)"/>
            </svg>
            <span style={{
              fontFamily: 'var(--font-sans)',
              fontWeight: 600,
              fontSize: '18px',
              color: 'var(--text-primary)',
              letterSpacing: '0.05em',
            }}>
              AEGISCORE
            </span>
          </div>
          <p style={{
            fontFamily: 'var(--font-sans)',
            fontWeight: 400,
            fontSize: '12px',
            color: 'var(--text-tertiary)',
          }}>
            Security Intelligence Platform
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '16px' }}>
            <label style={{
              display: 'block',
              fontFamily: 'var(--font-sans)',
              fontWeight: 500,
              fontSize: '11px',
              color: 'var(--text-secondary)',
              letterSpacing: '0.06em',
              textTransform: 'uppercase',
              marginBottom: '6px',
            }}>
              EMAIL
            </label>
            <input
              id="login-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="engineer@company.com"
              required
              style={{
                width: '100%',
                backgroundColor: 'var(--bg-elevated)',
                border: '1px solid var(--border-default)',
                borderRadius: '4px',
                padding: '10px 14px',
                fontFamily: 'var(--font-sans)',
                fontSize: '13px',
                color: 'var(--text-primary)',
                outline: 'none',
              }}
              onFocus={(e) => { e.target.style.borderColor = 'var(--border-accent)'; }}
              onBlur={(e) => { e.target.style.borderColor = 'var(--border-default)'; }}
            />
          </div>

          <div style={{ marginBottom: '24px' }}>
            <label style={{
              display: 'block',
              fontFamily: 'var(--font-sans)',
              fontWeight: 500,
              fontSize: '11px',
              color: 'var(--text-secondary)',
              letterSpacing: '0.06em',
              textTransform: 'uppercase',
              marginBottom: '6px',
            }}>
              PASSWORD
            </label>
            <input
              id="login-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter password"
              required
              style={{
                width: '100%',
                backgroundColor: 'var(--bg-elevated)',
                border: '1px solid var(--border-default)',
                borderRadius: '4px',
                padding: '10px 14px',
                fontFamily: 'var(--font-sans)',
                fontSize: '13px',
                color: 'var(--text-primary)',
                outline: 'none',
              }}
              onFocus={(e) => { e.target.style.borderColor = 'var(--border-accent)'; }}
              onBlur={(e) => { e.target.style.borderColor = 'var(--border-default)'; }}
            />
          </div>

          {error && (
            <div style={{
              fontFamily: 'var(--font-sans)',
              fontSize: '12px',
              color: 'var(--red-text)',
              marginBottom: '16px',
            }}>
              {error}
            </div>
          )}

          <Button
            type="submit"
            variant="primary"
            size="large"
            fullWidth
            loading={loading}
            id="login-submit"
            style={{
              fontWeight: 600,
              fontSize: '13px',
            }}
          >
            Sign In
          </Button>
        </form>

        <p style={{
          textAlign: 'center',
          marginTop: '24px',
          fontFamily: 'var(--font-mono)',
          fontSize: '10px',
          color: 'var(--text-muted)',
        }}>
          BYTEAEGIS — byteaegis.in
        </p>
      </div>
    </div>
  );
}

export default LoginPage;
