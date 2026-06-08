import Link from "next/link";

export default function DataSourcesPage() {
  return (
    <div className="min-h-screen bg-[#E7E8D1] p-4 sm:p-8">
      <div className="max-w-4xl mx-auto">
        <Link href="/docs" className="inline-block mb-6 text-sm font-bold text-black hover:underline">
          ← Back to Documentation
        </Link>

        <h1 className="text-2xl sm:text-3xl font-bold mb-6 text-black">Data Sources</h1>

        <div className="bg-white border-2 border-black p-6 shadow-[3px_3px_0px_black]">
          <p className="text-sm text-gray-600 mb-4">
            For complete data source documentation, please refer to the <a href="https://github.com/Jeevs10/jeevs-cbb/blob/main/docs/DATA_SOURCES.md" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">DATA_SOURCES.md</a> file on GitHub.
          </p>

          <div className="space-y-6 text-sm">
            <section>
              <h2 className="text-lg font-bold mb-2">Primary Data Sources</h2>
              <ul className="list-disc list-inside text-gray-600 space-y-2">
                <li><strong>Bart Torvik:</strong> Player statistics, BPM calculations, team efficiency metrics</li>
                <li><strong>Hoop Explorer:</strong> Roster information, biographical data, team rosters</li>
                <li><strong>Game Data:</strong> Game-by-game box scores for individual players</li>
                <li><strong>All-Time Historical Data:</strong> Aggregated historical player data for comparisons</li>
              </ul>
            </section>

            <section>
              <h2 className="text-lg font-bold mb-2">Derived Data</h2>
              <ul className="list-disc list-inside text-gray-600 space-y-2">
                <li><strong>Player Clusters:</strong> ML-derived player clusters based on statistical profiles</li>
                <li><strong>BPM Projections:</strong> ML projections for future season BPM values</li>
                <li><strong>Similarity Vectors:</strong> Precomputed vectors for efficient similarity search</li>
              </ul>
            </section>

            <section>
              <h2 className="text-lg font-bold mb-2">Data Coverage</h2>
              <ul className="list-disc list-inside text-gray-600">
                <li><strong>Years:</strong> 2019-2026 (8 seasons)</li>
                <li><strong>Players:</strong> ~15,000+ unique players</li>
                <li><strong>Teams:</strong> 350+ D1 teams</li>
                <li><strong>Games:</strong> ~50,000+ game records</li>
              </ul>
            </section>

            <section>
              <h2 className="text-lg font-bold mb-2">Data Freshness</h2>
              <ul className="list-disc list-inside text-gray-600">
                <li><strong>Daily:</strong> Game data, current season player stats</li>
                <li><strong>Weekly:</strong> Similarity vectors, roster updates</li>
                <li><strong>Monthly:</strong> Team efficiency updates</li>
                <li><strong>End of Season:</strong> Historical data, clusters, projections</li>
              </ul>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
}
