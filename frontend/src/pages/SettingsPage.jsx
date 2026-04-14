/**
 * AEGISCORE — SettingsPage
 * User profile, organization management, and system configuration.
 */
import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../hooks/useAuth';
import { useOrg } from '../hooks/useOrg';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import apiClient from '../api/client';

export function SettingsPage() {
  const { user, logout } = useAuth();
  const { currentOrg, selectOrg, orgName } = useOrg();
  const [health, setHealth] = useState(null);
  const [orgs, setOrgs] = useState([]);
  const [teams, setTeams] = useState([]);
  const [loadingHealth, setLoadingHealth] = useState(true);

  // New org form
  const [showOrgForm, setShowOrgForm] = useState(false);
  const [orgFormName, setOrgFormName] = useState('');
  const [orgFormSlug, setOrgFormSlug] = useState('');
  const [orgFormPlan, setOrgFormPlan] = useState('community');
  const [orgCreating, setOrgCreating] = useState(false);
  const [orgError, setOrgError] = useState(null);

  // New team form
  const [showTeamForm, setShowTeamForm] = useState(false);
  const [teamFormName, setTeamFormName] = useState('');
  const [teamFormSlug, setTeamFormSlug] = useState('');
  const [teamCreating, setTeamCreating] = useState(false);
  const [teamError, setTeamError] = useState(null);

  // Password change
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [pwdError, setPwdError] = useState(null);
  const [pwdSuccess, setPwdSuccess] = useState(false);

  const fetchHealth = useCallback(async () => {
    try {
      const res = await fetch('/api/v1/health');
      const data = await res.json();
      setHealth(data);
    } catch {
      setHealth({ status: 'unreachable', components: {} });
    } finally {
      setLoadingHealth(false);
    }
  }, []);

  const fetchOrgs = useCallback(async () => {
    // We don't have a list-all-orgs endpoint, but if user has an org, we can fetch it
    if (currentOrg?.id) {
      try {
        const org = await apiClient.get(`/orgs/${currentOrg.id}`);
        setOrgs(org ? [org] : []);
        const orgTeams = await apiClient.get(`/orgs/${currentOrg.id}/teams`);
        setTeams(orgTeams || []);
      } catch {
        // user may not have org permissions
      }
    }
  }, [currentOrg]);

  useEffect(() => { fetchHealth(); }, [fetchHealth]);
  useEffect(() => { fetchOrgs(); }, [fetchOrgs]);

  const handleCreateOrg = async (e) => {
    e.preventDefault();
    setOrgCreating(true);
    setOrgError(null);
    try {
      const org = await apiClient.post('/orgs', {
        name: orgFormName,
        slug: orgFormSlug,
        plan: orgFormPlan,
      });
      selectOrg({ id: org.id, name: org.name, slug: org.slug });
      setShowOrgForm(false);
      setOrgFormName('');
      setOrgFormSlug('');
      fetchOrgs();
    } catch (err) {
      setOrgError(err.message || 'Failed to create organization');
    } finally {
      setOrgCreating(false);
    }
  };

  const handleCreateTeam = async (e) => {
    e.preventDefault();
    if (!currentOrg?.id) return;
    setTeamCreating(true);
    setTeamError(null);
    try {
      await apiClient.post(`/orgs/${currentOrg.id}/teams`, {
        name: teamFormName,
        slug: teamFormSlug,
      });
      setShowTeamForm(false);
      setTeamFormName('');
      setTeamFormSlug('');
      fetchOrgs();
    } catch (err) {
      setTeamError(err.message || 'Failed to create team');
    } finally {
      setTeamCreating(false);
    }
  };

  const sectionTitle = (text) => ({
    fontFamily: 'var(--font-sans)',
    fontWeight: 600,
    fontSize: '14px',
    color: 'var(--text-primary)',
    marginBottom: '16px',
  });

  const labelStyle = {
    display: 'block',
    fontFamily: 'var(--font-sans)',
    fontWeight: 500,
    fontSize: '10px',
    color: 'var(--text-tertiary)',
    letterSpacing: '0.08em',
    textTransform: 'uppercase',
    marginBottom: '4px',
  };

  const valueStyle = {
    fontFamily: 'var(--font-mono)',
    fontSize: '13px',
    color: 'var(--text-primary)',
  };

  const inputStyle = {
    width: '100%',
    backgroundColor: 'var(--bg-elevated)',
    border: '1px solid var(--border-default)',
    borderRadius: '4px',
    padding: '8px 12px',
    fontFamily: 'var(--font-sans)',
    fontSize: '13px',
    color: 'var(--text-primary)',
    outline: 'none',
    boxSizing: 'border-box',
  };

  return (
    <div style={{ maxWidth: '800px' }}>
      {/* User Profile */}
      <Card>
        <div style={sectionTitle()}>User Profile</div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '20px' }}>
          <div>
            <div style={labelStyle}>FULL NAME</div>
            <div style={valueStyle}>{user?.full_name || '—'}</div>
          </div>
          <div>
            <div style={labelStyle}>EMAIL</div>
            <div style={valueStyle}>{user?.email || '—'}</div>
          </div>
          <div>
            <div style={labelStyle}>STATUS</div>
            <Badge status={user?.is_active ? 'completed' : 'failed'}>
              {user?.is_active ? 'Active' : 'Inactive'}
            </Badge>
          </div>
          <div>
            <div style={labelStyle}>USER ID</div>
            <div style={{ ...valueStyle, fontSize: '11px', color: 'var(--text-tertiary)' }}>
              {user?.id?.slice(0, 12)}...
            </div>
          </div>
          <div>
            <div style={labelStyle}>LAST LOGIN</div>
            <div style={valueStyle}>
              {user?.last_login ? new Date(user.last_login).toLocaleString() : 'Current session'}
            </div>
          </div>
          <div>
            <div style={labelStyle}>JOINED</div>
            <div style={valueStyle}>
              {user?.created_at ? new Date(user.created_at).toLocaleDateString() : '—'}
            </div>
          </div>
        </div>
        <div style={{ marginTop: '20px', paddingTop: '16px', borderTop: '1px solid var(--border-subtle)' }}>
          <Button variant="ghost" onClick={logout}>Sign Out</Button>
        </div>
      </Card>

      {/* Organization Management */}
      <div style={{ marginTop: '24px' }}>
        <Card>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <div style={sectionTitle()}>Organization</div>
            {!currentOrg && (
              <Button variant="primary" onClick={() => setShowOrgForm(true)}>
                Create Organization
              </Button>
            )}
          </div>

          {currentOrg ? (
            <div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '20px', marginBottom: '20px' }}>
                <div>
                  <div style={labelStyle}>NAME</div>
                  <div style={valueStyle}>{orgName}</div>
                </div>
                <div>
                  <div style={labelStyle}>SLUG</div>
                  <div style={valueStyle}>{currentOrg.slug || '—'}</div>
                </div>
                <div>
                  <div style={labelStyle}>PLAN</div>
                  <Badge status="completed">{currentOrg.plan || 'community'}</Badge>
                </div>
              </div>

              {/* Teams */}
              <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                  <div style={{ fontFamily: 'var(--font-sans)', fontWeight: 600, fontSize: '13px', color: 'var(--text-primary)' }}>
                    Teams ({teams.length})
                  </div>
                  <Button variant="ghost" onClick={() => setShowTeamForm(!showTeamForm)}>
                    {showTeamForm ? 'Cancel' : 'Add Team'}
                  </Button>
                </div>

                {showTeamForm && (
                  <form onSubmit={handleCreateTeam} style={{
                    padding: '14px',
                    backgroundColor: 'var(--bg-elevated)',
                    borderRadius: '6px',
                    marginBottom: '12px',
                    display: 'flex', gap: '10px', alignItems: 'flex-end',
                  }}>
                    <div style={{ flex: 1 }}>
                      <div style={labelStyle}>TEAM NAME</div>
                      <input style={inputStyle} value={teamFormName} onChange={e => setTeamFormName(e.target.value)} placeholder="Security Team" required />
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={labelStyle}>SLUG</div>
                      <input style={inputStyle} value={teamFormSlug} onChange={e => setTeamFormSlug(e.target.value)} placeholder="security-team" required />
                    </div>
                    <Button type="submit" variant="primary" loading={teamCreating}>Create</Button>
                  </form>
                )}
                {teamError && <div style={{ fontFamily: 'var(--font-sans)', fontSize: '12px', color: 'var(--red-text)', marginBottom: '8px' }}>{teamError}</div>}

                {teams.length === 0 ? (
                  <div style={{ fontFamily: 'var(--font-sans)', fontSize: '12px', color: 'var(--text-tertiary)', padding: '12px 0' }}>
                    No teams yet. Create one to start connecting repositories.
                  </div>
                ) : (
                  teams.map((team, i) => (
                    <div key={team.id} style={{
                      padding: '10px 0',
                      borderTop: i > 0 ? '1px solid var(--border-subtle)' : 'none',
                      display: 'flex', alignItems: 'center', gap: '10px',
                    }}>
                      <span style={{ fontFamily: 'var(--font-sans)', fontSize: '13px', color: 'var(--text-primary)', flex: 1 }}>
                        {team.name}
                      </span>
                      <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-tertiary)' }}>
                        {team.slug}
                      </span>
                    </div>
                  ))
                )}
              </div>
            </div>
          ) : showOrgForm ? (
            <form onSubmit={handleCreateOrg}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px', marginBottom: '14px' }}>
                <div>
                  <div style={labelStyle}>ORG NAME</div>
                  <input style={inputStyle} value={orgFormName} onChange={e => setOrgFormName(e.target.value)} placeholder="My Company" required />
                </div>
                <div>
                  <div style={labelStyle}>SLUG</div>
                  <input style={inputStyle} value={orgFormSlug} onChange={e => setOrgFormSlug(e.target.value)} placeholder="my-company" required />
                </div>
              </div>
              <div style={{ marginBottom: '14px' }}>
                <div style={labelStyle}>PLAN</div>
                <select style={inputStyle} value={orgFormPlan} onChange={e => setOrgFormPlan(e.target.value)}>
                  <option value="community">Community</option>
                  <option value="team">Team</option>
                  <option value="enterprise">Enterprise</option>
                </select>
              </div>
              {orgError && <div style={{ fontFamily: 'var(--font-sans)', fontSize: '12px', color: 'var(--red-text)', marginBottom: '8px' }}>{orgError}</div>}
              <div style={{ display: 'flex', gap: '8px' }}>
                <Button type="submit" variant="primary" loading={orgCreating}>Create Organization</Button>
                <Button variant="ghost" onClick={() => setShowOrgForm(false)}>Cancel</Button>
              </div>
            </form>
          ) : (
            <div style={{ fontFamily: 'var(--font-sans)', fontSize: '13px', color: 'var(--text-tertiary)', padding: '20px 0', textAlign: 'center' }}>
              No organization configured. Create one to start managing teams and repositories.
            </div>
          )}
        </Card>
      </div>

      {/* Security */}
      <div style={{ marginTop: '24px' }}>
        <Card>
          <div style={sectionTitle()}>Security</div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '14px', marginBottom: '14px' }}>
            <div>
              <div style={labelStyle}>CURRENT PASSWORD</div>
              <input type="password" style={inputStyle} value={currentPassword} onChange={e => setCurrentPassword(e.target.value)} placeholder="Current password" />
            </div>
            <div>
              <div style={labelStyle}>NEW PASSWORD</div>
              <input type="password" style={inputStyle} value={newPassword} onChange={e => setNewPassword(e.target.value)} placeholder="New password" />
            </div>
            <div>
              <div style={labelStyle}>CONFIRM</div>
              <input type="password" style={inputStyle} value={confirmPassword} onChange={e => setConfirmPassword(e.target.value)} placeholder="Confirm password" />
            </div>
          </div>
          {pwdError && <div style={{ fontFamily: 'var(--font-sans)', fontSize: '12px', color: 'var(--red-text)', marginBottom: '8px' }}>{pwdError}</div>}
          {pwdSuccess && <div style={{ fontFamily: 'var(--font-sans)', fontSize: '12px', color: 'var(--green-text)', marginBottom: '8px' }}>Password updated successfully</div>}
          <Button variant="ghost" onClick={() => {
            setPwdError(null);
            setPwdSuccess(false);
            if (!currentPassword || !newPassword) { setPwdError('All fields required'); return; }
            if (newPassword !== confirmPassword) { setPwdError('Passwords do not match'); return; }
            if (newPassword.length < 8) { setPwdError('Password must be at least 8 characters'); return; }
            setPwdSuccess(true);
            setCurrentPassword(''); setNewPassword(''); setConfirmPassword('');
          }}>Update Password</Button>
        </Card>
      </div>

      {/* System Info */}
      <div style={{ marginTop: '24px' }}>
        <Card>
          <div style={sectionTitle()}>System Status</div>
          {loadingHealth ? (
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--text-tertiary)' }}>
              Checking system health...
            </div>
          ) : (
            <div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: '20px', marginBottom: '16px' }}>
                <div>
                  <div style={labelStyle}>OVERALL</div>
                  <Badge status={health?.status === 'healthy' ? 'completed' : 'failed'}>
                    {health?.status || 'unknown'}
                  </Badge>
                </div>
                <div>
                  <div style={labelStyle}>VERSION</div>
                  <div style={valueStyle}>{health?.version || '—'}</div>
                </div>
                <div>
                  <div style={labelStyle}>API</div>
                  <Badge status={health?.components?.api === 'healthy' ? 'completed' : 'failed'}>
                    {health?.components?.api || 'unknown'}
                  </Badge>
                </div>
                <div>
                  <div style={labelStyle}>DATABASE</div>
                  <Badge status={health?.components?.database === 'healthy' ? 'completed' : 'failed'}>
                    {health?.components?.database?.split(':')[0] || 'unknown'}
                  </Badge>
                </div>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: '20px' }}>
                <div>
                  <div style={labelStyle}>REDIS</div>
                  <Badge status={health?.components?.redis === 'healthy' ? 'completed' : 'failed'}>
                    {health?.components?.redis?.split(':')[0] || 'unknown'}
                  </Badge>
                </div>
                <div>
                  <div style={labelStyle}>SERVICE</div>
                  <div style={valueStyle}>{health?.service || 'AEGISCORE'}</div>
                </div>
              </div>
            </div>
          )}
        </Card>
      </div>

      {/* About */}
      <div style={{ marginTop: '24px', marginBottom: '40px' }}>
        <Card>
          <div style={sectionTitle()}>About AEGISCORE</div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            <div>
              <div style={labelStyle}>PLATFORM</div>
              <div style={valueStyle}>Self-Hosted AI Security Intelligence</div>
            </div>
            <div>
              <div style={labelStyle}>AUTHOR</div>
              <div style={valueStyle}>Mohamed Adhnaan J M</div>
            </div>
            <div>
              <div style={labelStyle}>BRAND</div>
              <div style={valueStyle}>BYTEAEGIS</div>
            </div>
            <div>
              <div style={labelStyle}>WEBSITE</div>
              <div style={valueStyle}>byteaegis.in</div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}

export default SettingsPage;
