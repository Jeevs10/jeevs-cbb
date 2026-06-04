import { useEffect, useState } from "react";
import Panel, { PanelHeader } from "@/components/ui/Panel";
import Badge from "@/components/ui/Badge";
import { fetchPlayerBadges } from "@/lib/api";
import { classMap, posMap } from "@/lib/positionLabels";
import { yearClassMap } from "@/lib/yearClassMap";

function formatHeight(h?: string | number) {
  if (!h) return "—";

  const heightStr = String(h);
  const parts = heightStr.split("-");
  if (parts.length !== 2) return heightStr;

  const feet = parts[0];
  const inches = String(Number(parts[1]));

  return `${feet}'${inches}"`;
}

function formatHometown(city?: string, state?: string, country?: string) {
  if (!city && !state && !country) return "—";
  const parts = [city, state, country].filter(Boolean);
  return parts.join(", ");
}

export default function PlayerHeader({ player }) {
  const [badges, setBadges] = useState<any[]>([]);

  const playerCode = player?.AthleteSourceId || String(player?.roster?.ncaa_id || '');

  useEffect(() => {
    if (!playerCode) return;

    fetchPlayerBadges(playerCode)
      .then(setBadges)
      .catch(() => {});
  }, [playerCode]);

  const isBasicPlayer = player?.data_tier === "basic";

  return (
    <Panel className="relative overflow-hidden mb-6">

      <div className="absolute inset-0 opacity-10 bg-black" />

      <div className="relative space-y-2">

        <PanelHeader>PLAYER SCOUTING REPORT</PanelHeader>

        <h1 className="text-xs font-bold text-black uppercase tracking-wide">
          {player.player_name}
        </h1>

        {/* TEAM + YEAR */}
        <div className="text-xs text-black">
          {player.team} • {player.conf} • {" "}
          {player.is_career
            ? "Career"
            : player.year}
        </div>

        {/* CORE INFO BADGES */}
        <div className="flex gap-2 flex-wrap mt-2">

          {isBasicPlayer ? (
            // Basic players now have Position, Height, Weight, Hometown from roster join
            <>
              <div className="px-2 py-1 text-xs font-mono border-2 border-black bg-[#E7E8D1] text-black shadow-[3px_3px_0px_black]">
                POS: {player.Position ?? "—"}
              </div>
              {player.Height && (
                <div className="px-2 py-1 text-xs font-mono border-2 border-black bg-[#E7E8D1] text-black shadow-[3px_3px_0px_black]">
                  HT: {formatHeight(player.Height)}
                </div>
              )}
              {player.Weight && (
                <div className="px-2 py-1 text-xs font-mono border-2 border-black bg-[#E7E8D1] text-black shadow-[3px_3px_0px_black]">
                  WT: {player.Weight} lbs
                </div>
              )}
              {formatHometown(player.HometownCity, player.HometownState, player.HometownCountry) !== "—" && (
                <div className="px-2 py-1 text-xs font-mono border-2 border-black bg-[#E7E8D1] text-black shadow-[3px_3px_0px_black]">
                  FROM: {formatHometown(player.HometownCity, player.HometownState, player.HometownCountry)}
                </div>
              )}
            </>
          ) : (
            // Enriched players have full roster info
            <>
              <Badge variant="meta">
                CLASS: {classMap[player.roster?.pos] ?? "—"}
              </Badge>

              <Badge variant="meta">
                HT: {formatHeight(player.roster?.height)}
              </Badge>

              <Badge variant="meta">
                POS: {posMap[player.posClass] ?? "—"}
              </Badge>

              <Badge variant="meta">
                YEAR: {player.is_career
                  ? "Career"
                  : yearClassMap[player.roster?.year_class] ?? "—"}
              </Badge>

              {(player.Weight || player.roster?.weight) && (
                <Badge variant="meta">
                  WT: {(player.Weight || player.roster?.weight)} lbs
                </Badge>
              )}

              {formatHometown(
                player.HometownCity || player.roster?.hometown_city,
                player.HometownState || player.roster?.hometown_state,
                player.HometownCountry || player.roster?.hometown_country
              ) !== "—" && (
                <Badge variant="meta">
                  {formatHometown(
                    player.HometownCity || player.roster?.hometown_city,
                    player.HometownState || player.roster?.hometown_state,
                    player.HometownCountry || player.roster?.hometown_country
                  )}
                </Badge>
              )}
            </>
          )}

        </div>

        {/* ❌ REMOVED: skill badges from header */}

      </div>
    </Panel>
  );
}