import Link from "next/link";

export default function AnalyticsPage() {
  return (
    <div className="min-h-screen bg-[#E7E8D1] p-4 sm:p-8">
      <div className="max-w-4xl mx-auto">
        <Link href="/docs" className="inline-block mb-6 text-sm font-bold text-black hover:underline">
          ← Back to Documentation
        </Link>

        <h1 className="text-2xl sm:text-3xl font-bold mb-6 text-black">Analytics and Models</h1>

        <div className="bg-white border-2 border-black p-6 shadow-[3px_3px_0px_black]">
          <p className="text-sm text-gray-600 mb-4">
            For complete analytics and model documentation, please refer to the <a href="https://github.com/Jeevs10/jeevs-cbb/blob/main/docs/ANALYTICS_AND_MODELS.md" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">ANALYTICS_AND_MODELS.md</a> file on GitHub.
          </p>

          <div className="space-y-6 text-sm">
            <section>
              <h2 className="text-lg font-bold mb-2">Key Metrics and Models</h2>
              <ul className="list-disc list-inside text-gray-600 space-y-2">
                <li><strong>Box Plus Minus (BPM):</strong> Estimates player contribution per 100 possessions</li>
                <li><strong>Player Clustering:</strong> K-means clustering on statistical profiles (8 clusters)</li>
                <li><strong>Similarity Scoring:</strong> Cosine similarity on normalized feature vectors</li>
                <li><strong>BPM Projections:</strong> Random Forest regression for future BPM prediction</li>
                <li><strong>Usage Rate Analysis:</strong> Estimates possession usage percentage</li>
                <li><strong>Player Development Tracking:</strong> Year-over-year change analysis</li>
                <li><strong>NIL Valuation Model:</strong> Multiple linear regression for market value</li>
                <li><strong>Badge System:</strong> Achievement-based player badges</li>
                <li><strong>Cluster Transitions:</strong> Matrix of player movement between clusters</li>
                <li><strong>Team Optimization:</strong> Linear programming for optimal usage distribution</li>
              </ul>
            </section>

            <section>
              <h2 className="text-lg font-bold mb-2">Model Performance</h2>
              <ul className="list-disc list-inside text-gray-600 space-y-1">
                <li><strong>BPM Projections:</strong> R² = 0.45, RMSE = 1.8 BPM</li>
                <li><strong>Player Clustering:</strong> Silhouette score = 0.45</li>
                <li><strong>Similarity Search:</strong> Precomputed vectors for O(1) access</li>
              </ul>
            </section>

            <section>
              <h2 className="text-lg font-bold mb-2">Player Clusters</h2>
              <ul className="list-disc list-inside text-gray-600 space-y-1">
                <li>Cluster 1: Elite Scorers (high BPM, high usage)</li>
                <li>Cluster 2: Playmakers (high assist rate)</li>
                <li>Cluster 3: Two-Way Wings (balanced scoring/defense)</li>
                <li>Cluster 4: Rim Protectors (high block/rebound rates)</li>
                <li>Cluster 5: Floor Spacers (high 3P%)</li>
                <li>Cluster 6: Energy Players (high rebounding/steals)</li>
                <li>Cluster 7: Specialists (one standout skill)</li>
                <li>Cluster 8: Bench Players (low usage, low BPM)</li>
              </ul>
            </section>

            <section>
              <h2 className="text-lg font-bold mb-2">Badge Tiers</h2>
              <ul className="list-disc list-inside text-gray-600 space-y-1">
                <li><strong>Gold:</strong> Elite performance (top 5%)</li>
                <li><strong>Silver:</strong> Above average (top 20%)</li>
                <li><strong>Bronze:</strong> Notable achievement (top 40%)</li>
              </ul>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
}
