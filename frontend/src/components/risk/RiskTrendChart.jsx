/**
 * AEGISCORE — RiskTrendChart Component
 * Line chart showing risk score trends for top files.
 */
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const COLORS = [
  'var(--red-text)',
  'var(--amber-text)',
  'var(--blue-text)',
  'var(--green-text)',
  'var(--accent)',
];

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
          fontFamily: 'var(--font-mono)',
          fontSize: '12px',
          color: entry.color,
          marginTop: '2px',
        }}>
          {entry.name}: {Number(entry.value).toFixed(3)}
        </div>
      ))}
    </div>
  );
};

export function RiskTrendChart({ data = [], files = [] }) {
  const chartData = data.length > 0 ? data : [
    { date: 'Mar 1', file1: 0.82, file2: 0.65, file3: 0.45, file4: 0.38, file5: 0.22 },
    { date: 'Mar 5', file1: 0.85, file2: 0.62, file3: 0.48, file4: 0.35, file5: 0.25 },
    { date: 'Mar 10', file1: 0.79, file2: 0.68, file3: 0.52, file4: 0.40, file5: 0.20 },
    { date: 'Mar 15', file1: 0.88, file2: 0.71, file3: 0.49, file4: 0.38, file5: 0.28 },
    { date: 'Mar 20', file1: 0.84, file2: 0.66, file3: 0.55, file4: 0.42, file5: 0.24 },
    { date: 'Mar 25', file1: 0.90, file2: 0.63, file3: 0.50, file4: 0.36, file5: 0.30 },
    { date: 'Mar 30', file1: 0.87, file2: 0.70, file3: 0.47, file4: 0.39, file5: 0.22 },
  ];

  const fileNames = files.length > 0 ? files : [
    'auth/handler.py',
    'api/routes.py',
    'db/queries.py',
    'utils/crypto.py',
    'core/config.py',
  ];

  const fileKeys = files.length > 0
    ? files.map((_, i) => `file${i + 1}`)
    : ['file1', 'file2', 'file3', 'file4', 'file5'];

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
        Risk Score Trends
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid
            stroke="var(--border-subtle)"
            strokeDasharray="3 3"
            vertical={false}
          />
          <XAxis
            dataKey="date"
            tick={{
              fontFamily: 'var(--font-mono)',
              fontSize: 10,
              fill: 'var(--text-tertiary)',
            }}
            axisLine={{ stroke: 'var(--border-subtle)' }}
            tickLine={false}
          />
          <YAxis
            domain={[0, 1]}
            tick={{
              fontFamily: 'var(--font-mono)',
              fontSize: 10,
              fill: 'var(--text-tertiary)',
            }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip content={<CustomTooltip />} />
          {fileKeys.map((key, i) => (
            <Line
              key={key}
              type="monotone"
              dataKey={key}
              name={fileNames[i] || key}
              stroke={COLORS[i % COLORS.length]}
              strokeWidth={1.5}
              dot={false}
              activeDot={{ r: 3 }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default RiskTrendChart;
