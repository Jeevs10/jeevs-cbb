"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchAllPlayers } from "@/lib/api";

const BASE_URL = "http://localhost:8000";

// -------------------------
// FETCH YEARS
// -------------------------
async function fetchYears() {
  const res = await fetch(`${BASE_URL}/years`);
  if (!res.ok) throw new Error("Failed to fetch years");
  return res.json();
}

// -------------------------
// FORMAT HELPERS
// -------------------------
function formatYear(p: any) {
  if (p.is_career || p.year === "career") return "Career";
  if (typeof p.year === "number") return p.year;
  return "—";
}

function formatNumber(val: any) {
  if (val === null || val === undefined || val === "") return "—";
  if (typeof val !== "number") return val;
  return val.toFixed(4);
}

function formatHeight(val: any) {
  if (!val) return "—";
  return val; // keep string format intact
}

// -------------------------
// SORTABLE COLUMNS
// -------------------------
const SORTABLE = new Set([
  "year",
  "adj_rapm_margin",
  "off_rtg",
  "def_rtg",
  "off_usage",
  "off_orb",
  "def_orb",
  "off_assist",
  "off_to",
  "def_stl",
  "def_blk",
  "off_ftr",
  "off_threepr",
  "roster.height",
"off_team_poss_pct",
  
]);

export default function Home() {
  const [players, setPlayers] = useState<any[]>([]);
  const [years, setYears] = useState<number[]>([]);
  const [year, setYear] = useState<number | null>(null);

  const [sort, setSort] = useState("adj_rapm_margin");
  const [order, setOrder] = useState<"asc" | "desc">("desc");
  const [page, setPage] = useState(0);

  const limit = 50;

  // -------------------------
  // LOAD YEARS
  // -------------------------
  useEffect(() => {
    fetchYears()
      .then((data) => {
        setYears(data);
        if (data?.length) setYear(Math.max(...data));
      })
      .catch(console.error);
  }, []);

  // -------------------------
  // LOAD PLAYERS
  // -------------------------
  useEffect(() => {
    fetchAllPlayers({
      limit,
      offset: page * limit,
      sort,
      order,
      year: year ?? undefined,
    })
      .then(setPlayers)
      .catch(console.error);
  }, [sort, order, page, year]);

  // -------------------------
  // SORT HANDLER (FIXED)
  // -------------------------
  function handleSort(col: string) {
    if (!SORTABLE.has(col)) return;

    if (sort === col) {
      setOrder((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSort(col);
      setOrder("desc");
    }

    setPage(0);
  }

  const thClass = (col?: string) =>
    `p-2 border border-black select-none bg-[#B7C4A5] ${
      SORTABLE.has(col || "") ? "cursor-pointer hover:bg-[#aab895]" : ""
    }`;

  const tdClass = "p-2 border border-black";

  const arrow = (col: string) => {
    if (sort !== col) return "";
    return order === "asc" ? " ↑" : " ↓";
  };

  return (
    <div className="p-4 font-mono text-xs">
      <h1 className="text-xl font-bold mb-3">Player Leaderboard</h1>

      {/* YEAR TOGGLE */}
      <div className="mb-3 flex gap-2 flex-wrap">
        <button
          onClick={() => {
            setYear(null);
            setPage(0);
          }}
          className={`px-2 border ${year === null ? "font-bold underline" : ""}`}
        >
          ALL
        </button>

        {years.map((y) => (
          <button
            key={y}
            onClick={() => {
              setYear(y);
              setPage(0);
            }}
            className={`px-2 border ${year === y ? "font-bold underline" : ""}`}
          >
            {y}
          </button>
        ))}
      </div>

      {/* TABLE */}
      <div className="overflow-x-auto border-4 border-black bg-[#C7D0B8] shadow-[6px_6px_0px_black]">

        <table className="min-w-[1800px] border-collapse">

          <thead>
            <tr>
              <th className={`${thClass()} sticky left-0 z-30`}>
                Player
              </th>

              <th className={thClass()}>Team</th>

              <th className={thClass("year")} onClick={() => handleSort("year")}>
                Year{arrow("year")}
              </th>

              <th className={thClass("roster.height")} onClick={() => handleSort("roster.height")}>
            Height{arrow("roster.height")}
            </th>

            <th className={thClass("off_team_poss_pct")} onClick={() => handleSort("off_team_poss_pct")}>
            Poss%{arrow("off_team_poss_pct")}
            </th>

              <th className={thClass("adj_rapm_margin")} onClick={() => handleSort("adj_rapm_margin")}>
                RAPM{arrow("adj_rapm_margin")}
              </th>

              <th className={thClass("off_rtg")} onClick={() => handleSort("off_rtg")}>
                ORtg{arrow("off_rtg")}
              </th>

              <th className={thClass("def_rtg")} onClick={() => handleSort("def_rtg")}>
                DRtg{arrow("def_rtg")}
              </th>

              <th className={thClass("off_usage")} onClick={() => handleSort("off_usage")}>
                USG{arrow("off_usage")}
              </th>
              

            <th className={thClass("off_orb")} onClick={() => handleSort("off_orb")}>
            OR%{arrow("off_orb")}
            </th>

            <th className={thClass("def_orb")} onClick={() => handleSort("def_orb")}>
            DR%{arrow("def_orb")}
            </th>

            <th className={thClass("off_assist")} onClick={() => handleSort("off_assist")}>
            AST%{arrow("off_assist")}
            </th>

            <th className={thClass("off_to")} onClick={() => handleSort("off_to")}>
            TO%{arrow("off_to")}
            </th>

            <th className={thClass("def_stl")} onClick={() => handleSort("def_stl")}>
            STL%{arrow("def_stl")}
            </th>

            <th className={thClass("def_blk")} onClick={() => handleSort("def_blk")}>
            BLK%{arrow("def_blk")}
            </th>

            

              <th className={thClass("off_ftr")} onClick={() => handleSort("off_ftr")}>
            FTR{arrow("off_ftr")}
            </th>

            <th className={thClass("off_threep")} onClick={() => handleSort("off_threep")}>
            3P%{arrow("off_threep")}
            </th>
            </tr>
          </thead>

          <tbody>
            {players.map((p, i) => (
              <tr key={`${p.player_code}-${p.year ?? i}`} className="bg-[#E7E8D1] hover:bg-[#dfe2c6]">

                <td className="p-2 border border-black sticky left-0 bg-[#E7E8D1] z-20 whitespace-nowrap">
                  <Link href={`/player/${p.player_code}`} className="underline">
                    {p.player_name}
                  </Link>
                </td>

                <td className={tdClass}>{p.team}</td>
                <td className={tdClass}>{formatYear(p)}</td>
                <td className={tdClass}>{formatHeight(p["roster.height"])}</td>
                <td className={tdClass}>{formatNumber(p.off_team_poss_pct)}</td>

                <td className={tdClass}>{formatNumber(p.adj_rapm_margin)}</td>
                <td className={tdClass}>{formatNumber(p.off_rtg)}</td>
                <td className={tdClass}>{formatNumber(p.def_rtg)}</td>
                <td className={tdClass}>{formatNumber(p.off_usage)}</td>

                <td className={tdClass}>{formatNumber(p.off_orb)}</td>
                <td className={tdClass}>{formatNumber(p.def_orb)}</td>
                <td className={tdClass}>{formatNumber(p.off_assist)}</td>
                <td className={tdClass}>{formatNumber(p.off_to)}</td>
                <td className={tdClass}>{formatNumber(p.def_stl)}</td>
                <td className={tdClass}>{formatNumber(p.def_blk)}</td>
                <td className={tdClass}>{formatNumber(p.off_ftr)}</td>

                <td className={tdClass}>{formatNumber(p.off_threep)}</td>
              </tr>
            ))}
          </tbody>

        </table>
      </div>

      {/* PAGINATION */}
      <div className="mt-4 flex gap-2">
        <button onClick={() => setPage((p) => Math.max(p - 1, 0))}>
          Prev
        </button>
        <button onClick={() => setPage((p) => p + 1)}>
          Next
        </button>
      </div>
    </div>
  );
}