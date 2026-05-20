"use client";

interface TeamResumePanelProps {
  analytics?: any;
}

function safe(v: any): number {
  const n = parseFloat(v);
  return isNaN(n) ? 0 : n;
}

export default function TeamResumePanel({ analytics }: TeamResumePanelProps) {
  if (!analytics) {
    return (
      <div className="border-2 border-black bg-[#C7D0B8] text-black p-3 font-mono">
        <div className="text-center text-gray-600">
          <p className="text-sm mb-2">Resume not available</p>
          <p className="text-xs">This team does not have analytics data</p>
        </div>
      </div>
    );
  }

  const wins = safe(analytics.wins);
  const losses = safe(analytics.losses);
  const wab = safe(analytics.wab);
  const adjNet = safe(analytics.adj_net);
  const power = safe(analytics.power);

  const rankWab = safe(analytics.rank_wab);
  const rankAdjNet = safe(analytics.rank_adj_net);
  const rankPower = safe(analytics.rank_power);

  return (
    <div className="border-2 border-black bg-[#C7D0B8] text-black p-3 font-mono">
      <div className="text-xs font-bold mb-3 border-b border-black pb-2">
        TEAM RESUME
      </div>

      <div className="space-y-3">
        {/* RECORD */}
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold">RECORD</span>
          <span className="text-xs font-mono">
            {wins}-{losses}
          </span>
        </div>

        {/* WAB */}
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold">WAB</span>
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono">
              {wab.toFixed(2)}
            </span>
            {rankWab !== 0 && (
              <span className="text-[10px] text-gray-600">
                #{rankWab.toFixed(0)}
              </span>
            )}
          </div>
        </div>

        {/* NET RATING */}
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold">NET RATING</span>
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono">
              {adjNet.toFixed(2)}
            </span>
            {rankAdjNet !== 0 && (
              <span className="text-[10px] text-gray-600">
                #{rankAdjNet.toFixed(0)}
              </span>
            )}
          </div>
        </div>

        {/* POWER */}
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold">POWER</span>
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono">
              {power.toFixed(2)}
            </span>
            {rankPower !== 0 && (
              <span className="text-[10px] text-gray-600">
                #{rankPower.toFixed(0)}
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
