import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis } from "recharts";

export function RetentionChart({ values }) {
  const points = values.map((value, index) => ({ day: `D${index + 1}`, value: Math.round(value * 100) }));
  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={points}>
          <defs>
            <linearGradient id="retention" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#2dd4bf" stopOpacity={0.8} />
              <stop offset="100%" stopColor="#2dd4bf" stopOpacity={0.05} />
            </linearGradient>
          </defs>
          <XAxis dataKey="day" stroke="#94a3b8" />
          <Tooltip />
          <Area type="monotone" dataKey="value" stroke="#2dd4bf" fill="url(#retention)" strokeWidth={3} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
