/**
 * AEGISCORE — SeverityBreakdown Component
 * Bar chart showing findings by severity over recent scans.
 */
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload) return null;

  return (
    <div style={{
      backgroundColor: 'var(--bg-elevated)',
      border: '1px solid var(--border-default)',
      borderRadius: '6px',
      padding: '10px 14px',
    }}>
      <div style={{
        fontFamily: 'var(--font-sans)',
        fontSize: '13px',
        color: 'var(--text-primary)',
        marginBottom: '4px',
      }}>
        {label}
      </div>
      {payload.map((entry, i) => (
        <div key={i} style={{
          fontFamily: 'var(--font-sans)',
          fontSize: '12px',
          color: entry.color,
          marginTop: '2px',
        }}>
          {entry.name}: {entry.value}
        </div>
      ))}
    </div>
  );
};

export function SeverityBreakdown({ data = [] }) {
  const chartData = data.length > 0 ? data : [
    { name: 'Scan 1', critical: 2, high: 5, medium: 12 },
    { name: 'Scan 2', critical: 1, high: 8, medium: 15 },
    { name: 'Scan 3', critical: 3, high: 6, medium: 10 },
    { name: 'Scan 4', critical: 0, high: 4, medium: 18 },
    { name: 'Scan 5', critical: 2, high: 7, medium: 11 },
    { name: 'Scan 6', critical: 1, high: 3, medium: 14 },
    { name: 'Scan 7', critical: 4, high: 9, medium: 8 },
    { name: 'Scan 8', critical: 1, high: 5, medium: 16 },
    { name: 'Scan 9', critical: 0, high: 2, medium: 13 },
    { name: 'Scan 10', critical: 2, high: 6, medium: 9 },
  ];

  return (
    <div style={{
      backgroundColor: 'var(--bg-surface)',
      border: '1px solid var(--border-subtle)',
      borderRadius: '8px',
      padding: '20px 24px',
    }}>
      <div style={{
        fontFamily: 'var(--font-sans)',
        fontWeight: 600,
        fontSize: '13px',
        color: 'var(--text-primary)',
        marginBottom: '20px',
      }}>
        Findings Trend
      </div>

      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={chartData} barGap={2}>
          <CartesianGrid
            stroke="var(--border-subtle)"
            strokeDasharray="3 3"
            vertical={false}
          />
          <XAxis
            dataKey="name"
            tick={{
              fontFamily: 'var(--font-mono)',
              fontSize: 10,
              fill: 'var(--text-tertiary)',
            }}
            axisLine={{ stroke: 'var(--border-subtle)' }}
            tickLine={false}
          />
          <YAxis
            tick={{
              fontFamily: 'var(--font-mono)',
              fontSize: 10,
              fill: 'var(--text-tertiary)',
            }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip content={<CustomTooltip />} cursor={false} />
          <Bar dataKey="critical" name="Critical" fill="#5C1C1C" radius={[2, 2, 0, 0]} />
          <Bar dataKey="high" name="High" fill="#5C4300" radius={[2, 2, 0, 0]} />
          <Bar dataKey="medium" name="Medium" fill="#1A3060" radius={[2, 2, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default SeverityBreakdown;
