/**
 * AEGISCORE — Skeleton Component
 * Loading placeholder with no shimmer animation.
 */

export function Skeleton({ width = '100%', height = '20px', borderRadius = '4px', style = {} }) {
  return (
    <div
      style={{
        width,
        height,
        borderRadius,
        backgroundColor: 'var(--bg-elevated)',
        opacity: 0.6,
        ...style,
      }}
    />
  );
}

export function SkeletonRow({ columns = 4 }) {
  return (
    <div style={{ display: 'flex', gap: '16px', padding: '12px 16px' }}>
      {Array.from({ length: columns }).map((_, i) => (
        <Skeleton
          key={i}
          width={i === 0 ? '80px' : i === columns - 1 ? '60px' : 'auto'}
          height="16px"
          style={{ flex: i === 0 || i === columns - 1 ? 'none' : 1 }}
        />
      ))}
    </div>
  );
}

export function SkeletonCard() {
  return (
    <div style={{
      backgroundColor: 'var(--bg-surface)',
      border: '1px solid var(--border-subtle)',
      borderRadius: '8px',
      padding: '20px 24px',
    }}>
      <Skeleton width="80px" height="10px" style={{ marginBottom: '12px' }} />
      <Skeleton width="120px" height="34px" style={{ marginBottom: '8px' }} />
      <Skeleton width="140px" height="11px" />
    </div>
  );
}

export default Skeleton;
