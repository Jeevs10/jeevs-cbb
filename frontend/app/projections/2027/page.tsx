"use client";

import { useState } from "react";
import { useProjections } from "@/hooks/useProjections";
import { usePlayers } from "@/hooks/usePlayers";
import { useHistoricalBpm } from "@/hooks/useHistoricalBpm";
import { useClusterBpmDistribution } from "@/hooks/useClusterBpmDistribution";
import PlayerProjectionGraph from "@/components/player/PlayerProjectionGraph";
import PlayerProjectionTable from "@/components/player/PlayerProjectionTable";
import ClusterTransitionMap from "@/components/player/ClusterTransitionMap";
import PlayerClusterDistribution from "@/components/player/PlayerClusterDistribution";
import { PlayerSearch } from "@/components/player/PlayerSearch";
import Panel, { PanelHeader } from "@/components/ui/Panel";

interface Player {
  AthleteSourceId?: string;
  player_name?: string;
  Name?: string;
  team?: string;
  Team?: string;
  Position?: string;
  position?: string;
  BPM?: number;
}

export default function Projections2027() {
  const [search, setSearch] = useState<string>("");
  const [selectedPlayer, setSelectedPlayer] = useState<Player | null>(null);
  const [currentYear] = useState<number>(2026);

  // Fetch players for search - only fetch when there's search text
  const { players: searchResults, loading: searchLoading, error: searchError } = usePlayers({
    limit: 10,
    search: search.trim() || undefined,
    sort: "Name",
    order: "asc",
    year: 2026, // Only show 2026 players
  });

  // Projections hook - only fetch when we have a selected player
  const player_id = selectedPlayer?.AthleteSourceId || "";
  const { data: projectionData, loading, error } = useProjections(
    player_id,
    currentYear,
    1, // Only 1 year ahead (2027)
    10
  );

  // Historical BPM hook - fetch when we have a selected player
  const { data: historicalBpm } = useHistoricalBpm(player_id);

  // Cluster BPM distribution hook - fetch when we have cluster info
  const clusterId = projectionData?.cluster_description?.cluster_id;
  const { data: clusterDistribution } = useClusterBpmDistribution(clusterId || 0);

  const handlePlayerSelect = (player: Player) => {
    setSelectedPlayer(null); // Clear first to show loading
    setTimeout(() => {
      setSelectedPlayer(player);
    }, 0);
    setSearch("");
  };

  const currentBpm = selectedPlayer?.BPM || 0;

  return (
    <div className="p-6 font-mono text-xs">
      <h1 className="text-xs font-bold mb-6 uppercase tracking-wide">Cluster-Based Player Projections</h1>

      {/* Player Search */}
      <Panel>
        <PanelHeader>SEARCH PLAYER</PanelHeader>
        <div className="flex-1">
          <PlayerSearch
            value={search}
            onChange={setSearch}
            placeholder="Search player name (e.g., Keaton Wagler)"
          />
        </div>

        {/* Search Results Dropdown */}
        {search && search.trim().length >= 2 && (
          <>
            {searchLoading && (
              <div className="mt-2 text-xs text-black">Loading...</div>
            )}
            {searchError && (
              <div className="mt-2 text-xs text-black">{searchError}</div>
            )}
            {searchResults && searchResults.length > 0 && (
              <div className="mt-2 border-2 border-black bg-[#E7E8D1] max-h-60 overflow-y-auto">
                {searchResults.map((player: any) => (
                  <button
                    key={player.AthleteSourceId || player.id}
                    onClick={() => handlePlayerSelect(player)}
                    className="w-full text-left px-3 py-2 hover:bg-[#B8C0A8] border-b-2 border-black last:border-b-0 text-xs"
                  >
                    <div className="font-bold">{player.player_name || player.Name || 'Unknown'}</div>
                    <div className="text-xs text-black">{player.team || player.Team || 'Unknown'} - {player.Position || player.position || 'N/A'}</div>
                  </button>
                ))}
              </div>
            )}
            {searchResults && searchResults.length === 0 && !searchLoading && (
              <div className="mt-2 text-xs text-black">No players found</div>
            )}
          </>
        )}

        {/* Selected Player Display */}
        {selectedPlayer && (
          <div className="mt-4 p-3 border-2 border-black bg-[#E7E8D1]">
            <div className="font-bold text-xs">{selectedPlayer.player_name || selectedPlayer.Name}</div>
            <div className="text-xs text-black">
              {selectedPlayer.team || selectedPlayer.Team} - {selectedPlayer.Position} | Current BPM: {currentBpm.toFixed(2)}
            </div>
            <button
              onClick={() => setSelectedPlayer(null)}
              className="mt-2 text-xs text-black hover:underline"
            >
              Clear selection
            </button>
          </div>
        )}
      </Panel>

      {/* Methodology Info */}
      <Panel>
        <PanelHeader>HOW IT WORKS</PanelHeader>
        <p className="text-xs text-black mb-2">
          This system uses historical year-over-year BPM changes from players in the same cluster to predict a target player's growth, weighted by feature similarity.
        </p>
        <ul className="text-xs text-black list-disc list-inside space-y-1">
          <li>Players are grouped into clusters based on playing style and physical attributes</li>
          <li>Historical BPM changes from similar players are weighted by feature similarity</li>
          <li>Confidence intervals show the range of likely outcomes</li>
          <li>Percentile ranks indicate how good the projection is compared to historical peers</li>
        </ul>
      </Panel>

      {/* Projection Results */}
      {loading && selectedPlayer && (
        <div className="p-4 text-center text-black">Loading projections...</div>
      )}

      {error && (
        <div className="p-4 text-center text-black border-2 border-black bg-[#E7E8D1]">
          {error}
        </div>
      )}

      {projectionData && (
        <div className="space-y-6">
          {/* Cluster Info */}
          <Panel>
            <PanelHeader>CLUSTER INFORMATION</PanelHeader>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
              <div>
                <span className="text-black">Cluster:</span>
                <span className="ml-2 font-bold">
                  #{projectionData.cluster_id} {(projectionData.cluster_description as any)?.name ? `- ${(projectionData.cluster_description as any).name}` : ''}
                </span>
              </div>
              <div>
                <span className="text-black">Historical Samples:</span>
                <span className="ml-2 font-bold">{projectionData.historical_samples}</span>
              </div>
              {projectionData.cluster_description && (
                <>
                  <div>
                    <span className="text-black">Players in Cluster:</span>
                    <span className="ml-2 font-bold">{projectionData.cluster_description.count}</span>
                  </div>
                  <div>
                    <span className="text-black">Avg BPM:</span>
                    <span className="ml-2 font-bold">
                      {projectionData.cluster_description.avg_bpm !== null && projectionData.cluster_description.avg_bpm !== undefined
                        ? projectionData.cluster_description.avg_bpm.toFixed(2)
                        : 'N/A'}
                    </span>
                  </div>
                  <div>
                    <span className="text-black">Avg Height:</span>
                    <span className="ml-2 font-bold">
                      {projectionData.cluster_description.avg_height !== null && projectionData.cluster_description.avg_height !== undefined
                        ? projectionData.cluster_description.avg_height.toFixed(1) + '"'
                        : 'N/A'}
                    </span>
                  </div>
                  <div>
                    <span className="text-black">Avg Usage:</span>
                    <span className="ml-2 font-bold">
                      {projectionData.cluster_description.avg_usage !== null && projectionData.cluster_description.avg_usage !== undefined
                        ? projectionData.cluster_description.avg_usage.toFixed(1) + '%'
                        : 'N/A'}
                    </span>
                  </div>
                  <div>
                    <span className="text-black">3PT Attempt Rate:</span>
                    <span className="ml-2 font-bold">
                      {projectionData.cluster_description.avg_3pt_pct !== null && projectionData.cluster_description.avg_3pt_pct !== undefined
                        ? projectionData.cluster_description.avg_3pt_pct.toFixed(1) + '%'
                        : 'N/A'}
                    </span>
                  </div>
                  <div>
                    <span className="text-black">Rim Frequency:</span>
                    <span className="ml-2 font-bold">
                      {projectionData.cluster_description.avg_rim_freq !== null && projectionData.cluster_description.avg_rim_freq !== undefined
                        ? projectionData.cluster_description.avg_rim_freq.toFixed(1) + '%'
                        : 'N/A'}
                    </span>
                  </div>
                </>
              )}
            </div>
            {projectionData.cluster_description && projectionData.cluster_description.top_players && projectionData.cluster_description.top_players.length > 0 && (
              <div className="mt-3 text-xs">
                <span className="text-black font-bold">Top Players in Cluster:</span>
                <div className="mt-1 text-black">
                  {projectionData.cluster_description.top_players.slice(0, 5).map((player: any, idx: number) => (
                    <span key={idx} className="inline-block mr-3">
                      {player.Name} ({player.BPM !== null && player.BPM !== undefined ? player.BPM.toFixed(1) : 'N/A'})
                    </span>
                  ))}
                </div>
              </div>
            )}
          </Panel>

          {/* Projection Graph */}
          <Panel>
            <PanelHeader>2027 PROJECTION GRAPH</PanelHeader>
            <PlayerProjectionGraph
              currentBpm={currentBpm}
              currentYear={projectionData.current_year}
              projections={projectionData.projections}
              historicalBpm={historicalBpm}
            />
          </Panel>

          {/* Projection Table */}
          <Panel>
            <PanelHeader>2027 PROJECTION DETAILS</PanelHeader>
            <PlayerProjectionTable
              currentBpm={currentBpm}
              currentYear={projectionData.current_year}
              projections={projectionData.projections}
              clusterDescription={projectionData.cluster_description}
              similarPlayers={projectionData.similar_players as any}
              historicalSamples={projectionData.historical_samples}
              playerName={selectedPlayer?.player_name || selectedPlayer?.Name}
            />
          </Panel>

          {/* Cluster Transition Map */}
          {projectionData.cluster_transitions && (
            <ClusterTransitionMap transitions={projectionData.cluster_transitions as any} />
          )}

          {/* Player Cluster Distribution */}
          {projectionData.cluster_description && projectionData.projections && (
            <PlayerClusterDistribution
              currentBpm={currentBpm}
              clusterDescription={projectionData.cluster_description as any}
              projections={projectionData.projections as any}
              distribution={clusterDistribution?.distribution}
            />
          )}

        </div>
      )}

      {!selectedPlayer && !projectionData && (
        <div className="p-8 text-center text-black border-2 border-black bg-[#E7E8D1]">
          <p className="text-xs font-bold mb-2 uppercase tracking-wide">Search for a player above to view their 2027 projection</p>
          <p className="text-xs">Type a player name to search and select from the results</p>
        </div>
      )}
    </div>
  );
}
