"use client";

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface CareerTrajectory {
  year_from: number;
  year_to: number;
  bpm_change: number;
}

interface SimilarPlayer {
  player_key: string;
  player_name: string;
  similarity: number;
  career_trajectory: CareerTrajectory[];
}

interface SimilarPlayersCareerGraphProps {
  similarPlayers: SimilarPlayer[];
}

export default function SimilarPlayersCareerGraph({ similarPlayers }: SimilarPlayersCareerGraphProps) {
  // Transform data for the chart
  const chartData = similarPlayers.map(player => {
    const data: any = {
      name: player.player_name,
      similarity: player.similarity,
    };

    // Add BPM changes for each year
    player.career_trajectory.forEach((traj) => {
      data[`year_${traj.year_from}`] = traj.bpm_change;
    });

    return data;
  });

  // Get all unique years from trajectories
  const allYears = new Set<number>();
  similarPlayers.forEach(player => {
    player.career_trajectory.forEach(traj => {
      allYears.add(traj.year_from);
    });
  });

  const sortedYears = Array.from(allYears).sort();

  // Generate colors for each player
  const colors = [
    '#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#0088fe',
    '#00c49f', '#ffbb28', '#ff8042', '#8dd1e1', '#d084d0'
  ];

  return (
    <div className="w-full">
      <h4 className="font-bold text-sm mb-4">Similar Players Career BPM Changes</h4>
      <div className="text-xs text-gray-600 mb-2">
        Shows year-over-year BPM changes for the most similar historical players
      </div>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="name" 
            tick={{ fontSize: 10 }}
            angle={-45}
            textAnchor="end"
            height={80}
          />
          <YAxis 
            label={{ value: 'BPM Change', angle: -90, position: 'insideLeft', fontSize: 10 }}
            tick={{ fontSize: 10 }}
          />
          <Tooltip
            formatter={(value: any, name: any) => [
              value ? value.toFixed(2) : 'N/A',
              name ? name.replace('year_', 'Year ') : 'N/A'
            ]}
            labelFormatter={(label: any) => label || 'N/A'}
          />
          <Legend 
            wrapperStyle={{ fontSize: 10 }}
          />
          {sortedYears.map((year) => (
            <Line
              key={year}
              type="monotone"
              dataKey={`year_${year}`}
              stroke={colors[sortedYears.indexOf(year) % colors.length]}
              strokeWidth={2}
              dot={{ r: 4 }}
              name={`Year ${year}`}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
      
      {/* Player details table */}
      <div className="mt-4 border border-black">
        <table className="w-full text-xs">
          <thead className="bg-gray-100">
            <tr>
              <th className="p-2 text-left border-b border-black">Player</th>
              <th className="p-2 text-center border-b border-black">Similarity</th>
              {sortedYears.map(year => (
                <th key={year} className="p-2 text-center border-b border-black">
                  {year} Change
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {similarPlayers.map((player) => (
              <tr key={player.player_key} className={similarPlayers.indexOf(player) % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                <td className="p-2 border-b border-black font-medium">
                  {player.player_name}
                </td>
                <td className="p-2 text-center border-b border-black">
                  {(player.similarity * 100).toFixed(1)}%
                </td>
                {sortedYears.map(year => {
                  const traj = player.career_trajectory.find(t => t.year_from === year);
                  return (
                    <td key={year} className="p-2 text-center border-b border-black">
                      {traj ? traj.bpm_change.toFixed(2) : '-'}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
