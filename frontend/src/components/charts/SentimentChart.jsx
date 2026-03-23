import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export function SentimentChart({ timeline }) {
  const data = timeline.map((point) => ({
    date: point.date.slice(5),
    sentiment: point.sentiment
  }));
  return (
    <div className="h-72 rounded-[28px] border border-white/10 bg-white/5 p-4">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid stroke="rgba(148,163,184,0.18)" />
          <XAxis dataKey="date" stroke="#94a3b8" />
          <YAxis stroke="#94a3b8" />
          <Tooltip />
          <Line type="monotone" dataKey="sentiment" stroke="#2dd4bf" strokeWidth={3} dot={{ r: 4 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
