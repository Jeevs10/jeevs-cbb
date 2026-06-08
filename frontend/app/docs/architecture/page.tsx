import Link from "next/link";

export default function ArchitecturePage() {
  return (
    <div className="min-h-screen bg-[#E7E8D1] p-4 sm:p-8">
      <div className="max-w-4xl mx-auto">
        <Link href="/docs" className="inline-block mb-6 text-sm font-bold text-black hover:underline">
          ← Back to Documentation
        </Link>

        <h1 className="text-2xl sm:text-3xl font-bold mb-6 text-black">System Architecture</h1>

        <div className="bg-white border-2 border-black p-6 shadow-[3px_3px_0px_black]">
          <p className="text-sm text-gray-600 mb-4">
            For complete system architecture documentation, please refer to the <a href="https://github.com/Jeevs10/jeevs-cbb/blob/main/docs/SYSTEM_ARCHITECTURE.md" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">SYSTEM_ARCHITECTURE.md</a> file on GitHub.
          </p>

          <div className="space-y-6 text-sm">
            <section>
              <h2 className="text-lg font-bold mb-2">Technology Stack</h2>
              <div className="space-y-3">
                <div>
                  <h3 className="font-bold text-black">Frontend</h3>
                  <ul className="list-disc list-inside text-gray-600 ml-4">
                    <li>Next.js 14 (React)</li>
                    <li>TypeScript</li>
                    <li>Tailwind CSS</li>
                    <li>Victory (charts)</li>
                    <li>React Simple Maps</li>
                  </ul>
                </div>
                <div>
                  <h3 className="font-bold text-black">Backend</h3>
                  <ul className="list-disc list-inside text-gray-600 ml-4">
                    <li>FastAPI (Python 3.11+)</li>
                    <li>Pandas, NumPy</li>
                    <li>Scikit-learn</li>
                    <li>SlowAPI (rate limiting)</li>
                  </ul>
                </div>
                <div>
                  <h3 className="font-bold text-black">Data Storage</h3>
                  <ul className="list-disc list-inside text-gray-600 ml-4">
                    <li>CSV files (compressed with gzip)</li>
                    <li>JSON files (compressed with gzip)</li>
                    <li>Pickle files (cached vectors)</li>
                  </ul>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-lg font-bold mb-2">Architecture Overview</h2>
              <p className="text-gray-700">
                The system follows a three-tier architecture:
              </p>
              <ul className="list-disc list-inside text-gray-600 mt-2">
                <li><strong>Frontend:</strong> Next.js application with React components</li>
                <li><strong>Backend:</strong> FastAPI REST API with service layer</li>
                <li><strong>Data:</strong> File-based storage with in-memory caching</li>
              </ul>
            </section>

            <section>
              <h2 className="text-lg font-bold mb-2">Key Components</h2>
              <ul className="list-disc list-inside text-gray-600 space-y-1">
                <li><strong>Data Loader:</strong> Loads and caches player/team data at startup</li>
                <li><strong>Service Layer:</strong> Business logic for data processing</li>
                <li><strong>API Layer:</strong> REST endpoints with validation</li>
                <li><strong>Frontend API Client:</strong> Centralized API communication</li>
              </ul>
            </section>

            <section>
              <h2 className="text-lg font-bold mb-2">Performance Optimizations</h2>
              <ul className="list-disc list-inside text-gray-600 space-y-1">
                <li>In-memory caching of player data</li>
                <li>Gzip compression for data files (70-85% reduction)</li>
                <li>Efficient data structures (DataFrames, dictionaries)</li>
                <li>Lazy loading for game data</li>
                <li>Code splitting in Next.js</li>
              </ul>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
}
