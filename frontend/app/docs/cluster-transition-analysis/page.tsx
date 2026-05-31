import Link from "next/link";

export default function ClusterTransitionAnalysis() {
  return (
    <div className="max-w-4xl mx-auto p-8">
      <div className="mb-8">
        <Link href="/" className="text-blue-600 hover:underline text-sm">
          ← Back to Home
        </Link>
      </div>

      <div className="prose prose-lg max-w-none">
        <h1>Cluster Transition Analysis & Projection Model Improvements</h1>

        <h2>Overview</h2>
        <p>
          This document describes the cluster transition analysis conducted on historical player data (2019-2025) and how it has been integrated into the BPM projection model to improve prediction accuracy.
        </p>

        <h2>Background</h2>
        <p>
          The projection model uses KMeans clustering to group players into 18 archetypes based on their playing style and performance metrics. Historically, the model only considered how similar players developed within the same cluster. This analysis adds two new dimensions:
        </p>
        <ol>
          <li><strong>Cluster Transitions</strong>: How players move between clusters year-over-year</li>
          <li><strong>Cluster Development Patterns</strong>: How players within the same cluster develop over time</li>
        </ol>

        <h2>Methodology</h2>

        <h3>Data Sources</h3>
        <ul>
          <li><strong>Historical Player Data</strong>: Basic player statistics for 2019-2025 (57,274 players total)</li>
          <li><strong>Cluster Assignments</strong>: Generated for each year using KMeans with 18 clusters</li>
          <li><strong>Features Used</strong>: PPG, RPG, APG, Usage, eFG%, TS%, offensive/defensive ratings</li>
        </ul>

        <h3>Analysis Scripts</h3>

        <h4>1. cluster_historical_players.py</h4>
        <p>Generates cluster assignments for historical players using basic features available across all years.</p>
        <pre><code>python cluster_historical_players.py</code></pre>
        <p><strong>Output</strong>:</p>
        <ul>
          <li><code>player_clusters_[year].csv</code> for each year (2019-2025)</li>
          <li><code>cluster_descriptions_[year].json</code> with cluster metadata</li>
        </ul>

        <h4>2. analyze_cluster_transitions.py</h4>
        <p>Analyzes player movements between clusters and development patterns within clusters.</p>
        <pre><code>python analyze_cluster_transitions.py</code></pre>
        <p><strong>Output</strong>:</p>
        <ul>
          <li><code>cluster_transition_matrix.json</code> - Probability of moving from one cluster to another</li>
          <li><code>cluster_development_stats.json</code> - Average stat changes for players staying in same cluster</li>
          <li><code>player_transitions.csv</code> - Individual player transition records</li>
        </ul>

        <h2>Key Findings</h2>

        <h3>Cluster Transition Matrix</h3>
        <p>
          The transition matrix shows the probability of a player moving from one cluster to another year-over-year. Key insights:
        </p>

        <p><strong>Most players change clusters</strong>: Only 4-7% of players stay in the same cluster year-over-year. This indicates significant player development and role changes.</p>

        <p><strong>Example transitions from Cluster 0</strong>:</p>
        <ul>
          <li>→ Cluster 17: 13.76% (most common destination)</li>
          <li>→ Cluster 3: 12.34%</li>
          <li>→ Cluster 7: 9.29%</li>
          <li>→ Cluster 5: 9.15%</li>
          <li>→ Cluster 0: 4.20% (staying in same cluster)</li>
        </ul>

        <p><strong>High-mobility clusters</strong>: Some clusters have very low retention rates (&lt;5%), suggesting they represent transitional player types (e.g., freshmen adjusting to college basketball).</p>

        <p><strong>Stable clusters</strong>: A few clusters have higher retention rates (&gt;10%), possibly representing established player archetypes (e.g., senior role players).</p>

        <h3>Cluster Development Patterns</h3>
        <p>For players who stay in the same cluster, we analyzed their year-over-year development in key statistics:</p>

        <p><strong>Cluster 1 (Developing scorers)</strong>:</p>
        <ul>
          <li>Mean PPG change: +2.28</li>
          <li>Mean RPG change: +0.46</li>
          <li>Mean APG change: +0.86</li>
          <li>Mean Usage change: +2.28%</li>
          <li>Sample size: 59 players</li>
        </ul>

        <p><strong>Cluster 17 (High-usage stars)</strong>:</p>
        <ul>
          <li>Mean PPG change: +3.31</li>
          <li>Mean RPG change: +1.79</li>
          <li>Mean APG change: +0.40</li>
          <li>Mean Usage change: +1.89%</li>
          <li>Sample size: 139 players</li>
        </ul>

        <p><strong>Cluster 10 (Declining players)</strong>:</p>
        <ul>
          <li>Mean PPG change: -3.12</li>
          <li>Mean RPG change: -0.59</li>
          <li>Mean Usage change: -1.57%</li>
          <li>Sample size: 31 players</li>
        </ul>

        <h2>Integration into Projection Model</h2>

        <h3>Model Changes</h3>
        <p>The projection service (<code>projection_service.py</code>) was updated to incorporate:</p>
        <ol>
          <li><strong>Cluster Transition Matrix</strong>: Loaded from <code>cluster_transition_matrix.json</code></li>
          <li><strong>Cluster Development Stats</strong>: Loaded from <code>cluster_development_stats.json</code></li>
          <li><strong>Blended Projection Approach</strong>: Combines similarity-weighted averages with cluster development patterns</li>
        </ol>

        <h3>Projection Formula</h3>
        <p>The new projection formula blends three components:</p>
        <pre><code>blended_change = 0.7 * similarity_weighted_avg + 0.3 * cluster_development_pattern</code></pre>

        <p><strong>Similarity-weighted average (70%)</strong>: Based on how similar historical players developed, weighted by feature similarity (Usage, PPG, RPG, APG, shooting efficiency).</p>

        <p><strong>Cluster development pattern (30%)</strong>: Based on how players in the same cluster typically develop (using PPG change as a proxy for BPM change when BPM data is limited).</p>

        <p><strong>Cluster transition adjustment</strong>: If a player has a low probability of staying in their current cluster (&lt;50%), the projection is made more conservative (10% reduction) and the confidence interval is widened (20% increase) to account for uncertainty.</p>

        <h3>Example: Keaton Wagler (Cluster 12)</h3>
        <p><strong>Before integration</strong>:</p>
        <ul>
          <li>Projected 2027 BPM: 18.34</li>
          <li>Based solely on similar players</li>
        </ul>

        <p><strong>After integration</strong>:</p>
        <ul>
          <li>Projected 2027 BPM: 15.95</li>
          <li>Blended approach: 70% similarity + 30% cluster development</li>
          <li>Cluster 12 development: +0.98 PPG average change</li>
          <li>Conservative adjustment applied due to low cluster retention</li>
        </ul>

        <h2>Similar Players Display</h2>

        <h3>Career Trajectory View</h3>
        <p>The similar players display was updated to show career trajectories instead of individual year transitions. This provides better context for how similar players developed over their entire careers.</p>

        <p><strong>Before</strong>: Showed duplicate entries for the same player across different years</p>
        <ul>
          <li>Tramon Mark (Texas) 2021→2022: +4.06 BPM</li>
          <li>Tramon Mark (Texas) 2022→2023: -1.97 BPM</li>
          <li>Tramon Mark (Texas) 2023→2024: -1.32 BPM</li>
        </ul>

        <p><strong>After</strong>: Groups by player and shows full career trajectory</p>
        <ul>
          <li>Tramon Mark (Texas) - Similarity: 0.589
            <ul>
              <li>2021→2022: +4.06 BPM</li>
              <li>2022→2023: -1.97 BPM</li>
              <li>2023→2024: -1.32 BPM</li>
              <li>2024→2025: -0.67 BPM</li>
            </ul>
          </li>
        </ul>

        <h3>Career BPM Graph</h3>
        <p>A new visualization component (<code>SimilarPlayersCareerGraph.tsx</code>) displays:</p>
        <ul>
          <li>Line chart showing year-over-year BPM changes for similar players</li>
          <li>Color-coded lines for different years</li>
          <li>Detailed table with all career trajectory data</li>
        </ul>

        <h2>Performance Considerations</h2>

        <h3>Data Loading</h3>
        <p>The projection service now loads additional data files:</p>
        <ul>
          <li><code>cluster_transition_matrix.json</code> (~50KB)</li>
          <li><code>cluster_development_stats.json</code> (~30KB)</li>
          <li>Historical player data for name mapping (~7 years × ~8KB each)</li>
        </ul>
        <p>Total additional load time: &lt;100ms</p>

        <h3>Similar Players Grouping</h3>
        <p>The similar players calculation now:</p>
        <ol>
          <li>Groups by <code>player_key</code> to identify unique players</li>
          <li>Calculates average similarity across all years for each player</li>
          <li>Returns top 5 unique players with full career trajectories</li>
          <li>Filters out invalid player keys (empty, 'nan')</li>
        </ol>

        <h2>Future Improvements</h2>

        <h3>Potential Enhancements</h3>
        <ol>
          <li><strong>BPM-based development patterns</strong>: Use actual BPM changes instead of PPG as proxy when data becomes available</li>
          <li><strong>Multi-year projections</strong>: Extend transition analysis to 2-3 year projections</li>
          <li><strong>Position-specific transitions</strong>: Analyze transitions within position groups</li>
          <li><strong>Team context</strong>: Factor in team quality and role changes</li>
          <li><strong>Age/Year-in-school</strong>: Incorporate class year (freshman, sophomore, etc.) into transition probabilities</li>
        </ol>

        <h3>Data Gaps</h3>
        <ul>
          <li>Historical data before 2019 is limited</li>
          <li>BPM data not consistently available in older datasets</li>
          <li>Transfer portal effects not captured (players changing teams may have different development patterns)</li>
        </ul>

        <h2>Technical Details</h2>

        <h3>File Structure</h3>
        <pre><code>backend/
├── data/
│   ├── cluster_transition_matrix.json
│   ├── cluster_development_stats.json
│   ├── player_transitions.csv
│   ├── player_clusters_2019.csv
│   ├── player_clusters_2020.csv
│   ├── ...
│   ├── cluster_descriptions_2019.json
│   ├── cluster_descriptions_2020.json
│   └── ...
├── cluster_historical_players.py
├── analyze_cluster_transitions.py
└── app/services/
    └── projection_service.py (updated)

frontend/
└── components/player/
    └── SimilarPlayersCareerGraph.tsx (new)</code></pre>

        <h3>API Endpoints</h3>
        <p>The projection API remains unchanged:</p>
        <pre><code>GET /api/v1/players/[player_id]/projections?current_year=2026&years_ahead=1&min_samples=10</code></pre>
        <p>Response now includes:</p>
        <ul>
          <li><code>similar_players</code> array with career trajectories</li>
          <li>Same projection structure but with blended calculations</li>
        </ul>

        <h2>Conclusion</h2>
        <p>The cluster transition analysis provides valuable context for player projections by:</p>
        <ol>
          <li><strong>Accounting for cluster mobility</strong>: Recognizing that most players change clusters year-over-year</li>
          <li><strong>Incorporating development patterns</strong>: Using historical cluster development as a baseline</li>
          <li><strong>Improving uncertainty estimates</strong>: Widening confidence intervals when cluster transitions are likely</li>
          <li><strong>Better similar players display</strong>: Showing career trajectories instead of individual years</li>
        </ol>
        <p>These improvements make the projection model more robust and provide users with better context for understanding player development potential.</p>
      </div>
    </div>
  );
}
