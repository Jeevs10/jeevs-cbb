"use client";

import { useEffect, useState } from "react";
import { useParams, useSearchParams } from "next/navigation";

import {
  fetchPlayer,
  fetchPlayerMoves,
  fetchPlayerBadges,
  fetchPlayerSimilar,
  fetchPlayerEvolution, // ✅ added
  fetchPlayerHistory, // ✅ added
} from "@/lib/api";

import { useYear } from "@/app/context/YearContext";

import Panel from "@/components/ui/Panel";
import { PanelHeader } from "@/components/ui/Panel";

import PlayerRadar from "@/components/ui/PlayerRadar";
import Badge from "@/components/ui/Badge";

import PlayerHeader from "@/components/player/PlayerHeader";
import PlayerStatsPanel from "@/components/player/PlayerStatsPanel";
import PlayerMovesPanel from "@/components/player/PlayerMovesPanel";
import PlayerSimilarPanel from "@/components/player/PlayerSimilarPanel";
import PlayerEvolutionPanel from "@/components/player/PlayerEvolutionPanel";
import PlayerProgressionChart from "@/components/player/PlayerProgressionChart";
import PlayerTimeline from "@/components/player/PlayerTimeline";
import PlayerLocationPanel from "@/components/player/PlayerLocationPanel";
import PlayerLatestGamesPanel from "@/components/player/PlayerLatestGamesPanel";
import YearToggle from "@/components/ui/YearToggle";

type Player = {
  AthleteSourceId?: string;
  roster?: { 
    ncaa_id: string;
    hometown_city?: string;
    hometown_state?: string;
    hometown_country?: string;
    weight?: number;
  };
  data_tier?: string;
  player_name?: string;
  HometownCity?: string;
  HometownState?: string;
  HometownCountry?: string;
  Weight?: number;
  Height?: string;
  Position?: string;
  BPM?: number;
};

type PlayerRadar = any;
type Badge = { level: string; name: string };

export default function PlayerPage() {
  const { id } = useParams();
  const searchParams = useSearchParams();
  const { year, setYear } = useYear();

  const [player, setPlayer] = useState<Player | null>(null);
  const [availableYears, setAvailableYears] = useState<number[]>([]);
  const [styleWeight, setStyleWeight] = useState(0.7);
  const [playerHistory, setPlayerHistory] = useState<any[]>([]);
  const [moves, setMoves] = useState<any[]>([]);
  const [badges, setBadges] = useState<any[]>([]);
  const [similar, setSimilar] = useState<any>(null);
  const [evolution, setEvolution] = useState<any>(null);
  const [evolutionMetric, setEvolutionMetric] = useState("rapm");

  const playerCode = player?.AthleteSourceId || String(player?.roster?.ncaa_id || '');

  // Set year from URL query parameter on mount
  useEffect(() => {
    const yearParam = searchParams.get('year');
    if (yearParam) {
      setYear(parseInt(yearParam));
    }
  }, [searchParams, setYear]);

  // -------------------------
  // PLAYER
  // -------------------------
  useEffect(() => {
    if (!id) return;

    fetchPlayer(Array.isArray(id) ? id[0] : id, year)
      .then((data) => {
        setPlayer(data.player);
        setAvailableYears(data.available_years || []);
      })
      .catch(() => {});
  }, [id, year]);

  // -------------------------
  // PLAYER HISTORY
  // -------------------------
  useEffect(() => {
    if (!playerCode) return;

    fetchPlayerHistory(playerCode)
      .then((data) => {
        setPlayerHistory(data.history || []);
      })
      .catch(() => {});
  }, [playerCode]);

  // -------------------------
  // DEPENDENT DATA
  // -------------------------
  useEffect(() => {
    if (!playerCode) return;

    // Only fetch advanced data for enriched players
    if (player?.data_tier === 'enriched') {
      Promise.all([
        fetchPlayerMoves(playerCode, year),
        fetchPlayerBadges(playerCode, year),
        fetchPlayerSimilar(playerCode, styleWeight, year),
        fetchPlayerEvolution(playerCode, year, evolutionMetric),
      ])
        .then(
          ([
            movesRes,
            badgesRes,
            similarRes,
            evolutionRes,
          ]) => {
            setMoves(movesRes || []);
            setBadges(badgesRes || []);
            setSimilar(similarRes || null);
            setEvolution(evolutionRes || null);
          }
        )
        .catch(() => {});
    } else {
      // For basic players, set empty states
      setMoves([]);
      setBadges([]);
      setSimilar(null);
      setEvolution(null);
    }
  }, [playerCode, year, styleWeight, player?.data_tier, evolutionMetric]);

  // -------------------------
  // LOADING STATE
  // -------------------------
  if (!player) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#E7E8D1] text-black font-mono">
        LOADING PLAYER DATA...
      </div>
    );
  }

  return (
    <div className="p-3 space-y-6">
      <PlayerHeader player={player} />

      {/* YEAR TOGGLE */}
      {availableYears.length > 0 && (
        <YearToggle availableYears={availableYears} />
      )}

      <div className="text-xs font-bold">
        Viewing: {year ?? "Latest Season"}
      </div>

      {/* ✅ PLAYER TIMELINE (MOVED TO TOP) */}
      <PlayerTimeline
        playerHistory={playerHistory}
        playerName={player?.player_name || 'Player'}
        currentYear={year}
      />

      {/* HOMETOWN LOCATION */}
      <PlayerLocationPanel
        city={player.HometownCity || player.roster?.hometown_city}
        state={player.HometownState || player.roster?.hometown_state}
        primaryColor="#000000"
      />

      {/* DATA TIER INDICATOR */}
      <div className="text-xs font-bold mb-4">
        Data Tier: <span className={player.data_tier === 'enriched' ? 'text-green-600' : 'text-orange-600'}>
          {player.data_tier?.toUpperCase() || 'BASIC'}
        </span>
        {player.data_tier === 'basic' && (
          <span className="ml-2 text-gray-600">(Limited advanced metrics available)</span>
        )}
      </div>

      {/* MAIN GRID */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

        {/* BASE STATS */}
        <Panel>
          <PanelHeader>BASE STATS</PanelHeader>
          <PlayerStatsPanel player={player} />
        </Panel>

        {/* RADAR */}
        {player?.data_tier === "enriched" && (
          <Panel>
            <PanelHeader>PLAYER RADAR</PanelHeader>
            <div className="p-4">
              <PlayerRadar playerId={playerCode} year={year} />
            </div>
          </Panel>
        )}

        {/* BASIC ONLY MESSAGE */}
        {player.data_tier === 'basic' && (
          <Panel>
            <PanelHeader>ADVANCED PROFILE</PanelHeader>
            <div className="p-4 text-center text-black">
              <p className="text-xs font-bold mb-2 uppercase tracking-wide">Advanced analytics not available</p>
              <p className="text-xs">This player has basic statistics only</p>
            </div>
          </Panel>
        )}

      </div>

      {/* LATEST 5 GAMES */}
      <Panel>
        <PanelHeader>LATEST 5 GAMES</PanelHeader>
        <PlayerLatestGamesPanel playerId={playerCode} year={year ?? undefined} />
      </Panel>

      {/* BADGES - Only for enriched data */}
      {player.data_tier === 'enriched' ? (
        <Panel>
          <PanelHeader>PLAYER BADGES</PanelHeader>

          <div className="flex flex-wrap gap-2">
            {badges.map((b, i) => (
              <Badge key={i} level={b.level} name={b.name}>
                {b.name}
              </Badge>
            ))}
          </div>
        </Panel>
      ) : (
        <Panel>
          <PanelHeader>PLAYER BADGES</PanelHeader>
          <div className="p-4 text-center text-black">
            <p className="text-xs font-bold mb-2 uppercase tracking-wide">Badges not available</p>
            <p className="text-xs">Requires advanced analytics data</p>
          </div>
        </Panel>
      )}

      {/* MOVES - Only for enriched data */}
      {player.data_tier === 'enriched' ? (
        <Panel>
          <PanelHeader>MOVES</PanelHeader>
          <PlayerMovesPanel moves={moves} />
        </Panel>
      ) : (
        <Panel>
          <PanelHeader>MOVES</PanelHeader>
          <div className="p-4 text-center text-black">
            <p className="text-xs font-bold mb-2 uppercase tracking-wide">Play style analysis not available</p>
            <p className="text-xs">Requires advanced analytics data</p>
          </div>
        </Panel>
      )}

      {/* SIMILAR PLAYERS - Only for enriched players */}
      {player.data_tier === 'enriched' ? (
        <Panel>
          <PanelHeader>SIMILAR PLAYERS</PanelHeader>

          <PlayerSimilarPanel
            player={player}
            similar={similar}
            styleWeight={styleWeight}
            setStyleWeight={setStyleWeight}
          />
        </Panel>
      ) : (
        <Panel>
          <PanelHeader>SIMILAR PLAYERS</PanelHeader>
          <div className="p-4 text-center text-black">
            <p className="text-xs font-bold mb-2 uppercase tracking-wide">Similar players not available</p>
            <p className="text-xs">Requires advanced analytics data</p>
          </div>
        </Panel>
      )}

      {/* EVOLUTION - Only for enriched players */}
      {player.data_tier === 'enriched' ? (
        <PlayerEvolutionPanel
          data={evolution}
          player={player}
          onMetricChange={setEvolutionMetric}
        />
      ) : (
        <Panel>
          <PanelHeader>EVOLUTION PATH</PanelHeader>
          <div className="p-4 text-center text-black">
            <p className="text-xs font-bold mb-2 uppercase tracking-wide">Evolution data not available</p>
            <p className="text-xs">Requires advanced analytics data</p>
          </div>
        </Panel>
      )}

      {/* ✅ PROGRESSION CHART (NEW) */}
      <PlayerProgressionChart
        playerHistory={playerHistory}
        dataTier={(player.data_tier || 'basic') as "enriched" | "basic"}
      />

    </div>
  );
}