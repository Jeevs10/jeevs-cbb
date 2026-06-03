"use client";

import Panel, { PanelHeader } from "@/components/ui/Panel";

function pct(v: number) {
  return Math.round((v || 0) * 100);
}

function ppp(v: number) {
  return (v || 0).toFixed(2);
}

function getGrade(efficiencyPercentile: number, frequencyPercentile: number, isDefense: boolean = false) {
  // For defense: lower PPP is good, so invert efficiency percentile
  // For offense: higher PPP is good, so use efficiency percentile as-is
  const effPctile = isDefense ? (1 - efficiencyPercentile) : efficiencyPercentile;
  
  // Adjust weighting based on frequency
  // High frequency = efficiency matters more (70% eff, 30% freq)
  // Low frequency = efficiency matters less (less sample size, less impact)
  // Use frequency as a weight multiplier for efficiency importance
  const freqWeight = 0.3 + (frequencyPercentile * 0.4); // 0.3 to 0.7 based on frequency
  const effWeight = 1 - freqWeight;
  
  const overallPercentile = (effPctile * effWeight) + (frequencyPercentile * freqWeight);
  
  if (overallPercentile >= 0.90) return "S";
  if (overallPercentile >= 0.88) return "A+";
  if (overallPercentile >= 0.85) return "A";
  if (overallPercentile >= 0.80) return "A-";
  if (overallPercentile >= 0.78) return "B+";
  if (overallPercentile >= 0.75) return "B";
  if (overallPercentile >= 0.70) return "B-";
  if (overallPercentile >= 0.68) return "C+";
  if (overallPercentile >= 0.65) return "C";
  if (overallPercentile >= 0.60) return "C-";
  if (overallPercentile >= 0.58) return "D+";
  if (overallPercentile >= 0.55) return "D";
  if (overallPercentile >= 0.50) return "D-";
  return "F";
}

function safe(v: any): number {
  const n = parseFloat(v);
  return isNaN(n) ? 0 : n;
}

interface StyleRowProps {
  label: string;
  frequency: number;
  effectiveness: number;
  frequencyPctile?: number;
  efficiencyPctile?: number;
  isGood?: boolean;
  isDefense?: boolean;
}

function StyleRow({ label, frequency, effectiveness, frequencyPctile = 0, efficiencyPctile = 0, isGood = true, isDefense = false }: StyleRowProps) {
  const freqPct = pct(frequency);
  const effValue = ppp(effectiveness);
  const grade = getGrade(efficiencyPctile, frequencyPctile, isDefense);
  
  return (
    <div className="flex justify-between items-center text-xs border border-black p-2 bg-[#E7E8D1]">
      <div>
        <div className="font-bold">{label}</div>
        <div className="text-[10px] opacity-70">
          Usage: {freqPct}%
        </div>
        <div className="text-[10px] opacity-90">
          League Freq: {(frequencyPctile * 100).toFixed(0)}th %
        </div>
        <div className="w-full h-1 bg-black/20 mt-1">
          <div
            className="h-1 bg-black"
            style={{ width: `${frequencyPctile * 100}%` }}
          />
        </div>
      </div>
      <div className="text-right">
        <div className="font-bold">{effValue} PPP</div>
        <div className="text-[10px]">
          Grade: {grade}
        </div>
      </div>
    </div>
  );
}


export default function TeamStylePanel({ analytics }: { analytics: any }) {
  if (!analytics) {
    return (
      <Panel className="mt-6">
        <PanelHeader>PLAY STYLE</PanelHeader>
        <div className="p-3 text-xs text-center opacity-60">
          No style data available
        </div>
      </Panel>
    );
  }

  return (
    <Panel className="mt-6">
      <PanelHeader>PLAY STYLE</PanelHeader>

      <div className="space-y-0">
        <div className="bg-black text-white px-2 py-1 text-xs font-bold mb-1 mt-2">
          OFFENSIVE STYLE
        </div>

        <StyleRow
          label="RIM ATTACK"
          frequency={analytics.off_style_rim_attack_pct}
          effectiveness={analytics.off_style_rim_attack_ppp}
          frequencyPctile={safe(analytics.pctile_off_style_rim_attack_pct)}
          efficiencyPctile={safe(analytics.pctile_off_style_rim_attack_ppp)}
          isGood={analytics.off_style_rim_attack_ppp > 1.0}
        />

        <StyleRow
          label="TRANSITION"
          frequency={analytics.off_style_transition_pct}
          effectiveness={analytics.off_style_transition_ppp}
          frequencyPctile={safe(analytics.pctile_off_style_transition_pct)}
          efficiencyPctile={safe(analytics.pctile_off_style_transition_ppp)}
          isGood={analytics.off_style_transition_ppp > 1.0}
        />

        <StyleRow
          label="MID RANGE"
          frequency={analytics.off_style_mid_range_pct}
          effectiveness={analytics.off_style_mid_range_ppp}
          frequencyPctile={safe(analytics.pctile_off_style_mid_range_pct)}
          efficiencyPctile={safe(analytics.pctile_off_style_mid_range_ppp)}
          isGood={analytics.off_style_mid_range_ppp > 0.9}
        />

        <StyleRow
          label="POST UP"
          frequency={analytics.off_style_post_up_pct}
          effectiveness={analytics.off_style_post_up_ppp}
          frequencyPctile={safe(analytics.pctile_off_style_post_up_pct)}
          efficiencyPctile={safe(analytics.pctile_off_style_post_up_ppp)}
          isGood={analytics.off_style_post_up_ppp > 0.9}
        />

        <StyleRow
          label="PERIMETER CUT"
          frequency={analytics.off_style_perimeter_cut_pct}
          effectiveness={analytics.off_style_perimeter_cut_ppp}
          frequencyPctile={safe(analytics.pctile_off_style_perimeter_cut_pct)}
          efficiencyPctile={safe(analytics.pctile_off_style_perimeter_cut_ppp)}
          isGood={analytics.off_style_perimeter_cut_ppp > 1.0}
        />

        <StyleRow
          label="BIG CUT/ROLL"
          frequency={analytics.off_style_big_cut_roll_pct}
          effectiveness={analytics.off_style_big_cut_roll_ppp}
          frequencyPctile={safe(analytics.pctile_off_style_big_cut_roll_pct)}
          efficiencyPctile={safe(analytics.pctile_off_style_big_cut_roll_ppp)}
          isGood={analytics.off_style_big_cut_roll_ppp > 1.0}
        />

        <StyleRow
          label="PICK & POP"
          frequency={analytics.off_style_pick_pop_pct}
          effectiveness={analytics.off_style_pick_pop_ppp}
          frequencyPctile={safe(analytics.pctile_off_style_pick_pop_pct)}
          efficiencyPctile={safe(analytics.pctile_off_style_pick_pop_ppp)}
          isGood={analytics.off_style_pick_pop_ppp > 1.0}
        />

        <StyleRow
          label="DRIBBLE JUMPER"
          frequency={analytics.off_style_dribble_jumper_pct}
          effectiveness={analytics.off_style_dribble_jumper_ppp}
          frequencyPctile={safe(analytics.pctile_off_style_dribble_jumper_pct)}
          efficiencyPctile={safe(analytics.pctile_off_style_dribble_jumper_ppp)}
          isGood={analytics.off_style_dribble_jumper_ppp > 0.9}
        />

        <div className="bg-black text-white px-2 py-1 text-xs font-bold mt-4 mb-1">
          DEFENSIVE STYLE
        </div>

        <StyleRow
          label="VS RIM ATTACK"
          frequency={analytics.def_style_rim_attack_pct}
          effectiveness={analytics.def_style_rim_attack_ppp}
          frequencyPctile={safe(analytics.pctile_def_style_rim_attack_pct)}
          efficiencyPctile={safe(analytics.pctile_def_style_rim_attack_ppp)}
          isGood={analytics.def_style_rim_attack_ppp < 1.0}
          isDefense={true}
        />

        <StyleRow
          label="VS TRANSITION"
          frequency={analytics.def_style_transition_pct}
          effectiveness={analytics.def_style_transition_ppp}
          frequencyPctile={safe(analytics.pctile_def_style_transition_pct)}
          efficiencyPctile={safe(analytics.pctile_def_style_transition_ppp)}
          isGood={analytics.def_style_transition_ppp < 1.0}
          isDefense={true}
        />

        <StyleRow
          label="VS MID RANGE"
          frequency={analytics.def_style_mid_range_pct}
          effectiveness={analytics.def_style_mid_range_ppp}
          frequencyPctile={safe(analytics.pctile_def_style_mid_range_pct)}
          efficiencyPctile={safe(analytics.pctile_def_style_mid_range_ppp)}
          isGood={analytics.def_style_mid_range_ppp < 0.9}
          isDefense={true}
        />

        <StyleRow
          label="VS POST UP"
          frequency={analytics.def_style_post_up_pct}
          effectiveness={analytics.def_style_post_up_ppp}
          frequencyPctile={safe(analytics.pctile_def_style_post_up_pct)}
          efficiencyPctile={safe(analytics.pctile_def_style_post_up_ppp)}
          isGood={analytics.def_style_post_up_ppp < 0.9}
          isDefense={true}
        />

        <StyleRow
          label="VS PERIMETER CUT"
          frequency={analytics.def_style_perimeter_cut_pct}
          effectiveness={analytics.def_style_perimeter_cut_ppp}
          frequencyPctile={safe(analytics.pctile_def_style_perimeter_cut_pct)}
          efficiencyPctile={safe(analytics.pctile_def_style_perimeter_cut_ppp)}
          isGood={analytics.def_style_perimeter_cut_ppp < 1.0}
          isDefense={true}
        />

        <StyleRow
          label="VS BIG CUT/ROLL"
          frequency={analytics.def_style_big_cut_roll_pct}
          effectiveness={analytics.def_style_big_cut_roll_ppp}
          frequencyPctile={safe(analytics.pctile_def_style_big_cut_roll_pct)}
          efficiencyPctile={safe(analytics.pctile_def_style_big_cut_roll_ppp)}
          isGood={analytics.def_style_big_cut_roll_ppp < 1.0}
          isDefense={true}
        />

        <StyleRow
          label="VS PICK & POP"
          frequency={analytics.def_style_pick_pop_pct}
          effectiveness={analytics.def_style_pick_pop_ppp}
          frequencyPctile={safe(analytics.pctile_def_style_pick_pop_pct)}
          efficiencyPctile={safe(analytics.pctile_def_style_pick_pop_ppp)}
          isGood={analytics.def_style_pick_pop_ppp < 1.0}
          isDefense={true}
        />

        <StyleRow
          label="VS DRIBBLE JUMPER"
          frequency={analytics.def_style_dribble_jumper_pct}
          effectiveness={analytics.def_style_dribble_jumper_ppp}
          frequencyPctile={safe(analytics.pctile_def_style_dribble_jumper_pct)}
          efficiencyPctile={safe(analytics.pctile_def_style_dribble_jumper_ppp)}
          isGood={analytics.def_style_dribble_jumper_ppp < 0.9}
          isDefense={true}
        />
      </div>
    </Panel>
  );
}
