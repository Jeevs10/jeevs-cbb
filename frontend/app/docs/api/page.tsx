import Link from "next/link";

export default function ApiDocsPage() {
  return (
    <div className="min-h-screen bg-[#E7E8D1] p-4 sm:p-8">
      <div className="max-w-4xl mx-auto">
        <Link href="/docs" className="inline-block mb-6 text-sm font-bold text-black hover:underline">
          ← Back to Documentation
        </Link>

        <h1 className="text-2xl sm:text-3xl font-bold mb-6 text-black">API Documentation</h1>

        <div className="bg-white border-2 border-black p-6 shadow-[3px_3px_0px_black]">
          <p className="text-sm text-gray-600 mb-4">
            For the complete API documentation, please refer to the <a href="https://github.com/Jeevs10/jeevs-cbb/blob/main/docs/API_DOCUMENTATION.md" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">API_DOCUMENTATION.md</a> file on GitHub.
          </p>

          <div className="space-y-6 text-sm">
            <section>
              <h2 className="text-lg font-bold mb-2">Overview</h2>
              <p className="text-gray-700">
                The JEEVS CBB API provides endpoints for accessing college basketball player and team statistics, analytics, and projections. The API is built with FastAPI and follows RESTful conventions.
              </p>
              <ul className="mt-2 list-disc list-inside text-gray-600">
                <li><strong>Base URL:</strong> http://localhost:8000 (development) or your deployed URL</li>
                <li><strong>API Version:</strong> v1</li>
                <li><strong>All endpoints are prefixed with:</strong> /api/v1</li>
              </ul>
            </section>

            <section>
              <h2 className="text-lg font-bold mb-2">Rate Limiting</h2>
              <ul className="list-disc list-inside text-gray-600">
                <li><strong>Default:</strong> 100 requests per minute per IP address</li>
                <li><strong>Health Check:</strong> 100 requests per minute</li>
              </ul>
            </section>

            <section>
              <h2 className="text-lg font-bold mb-2">Main Endpoints</h2>
              <ul className="list-disc list-inside text-gray-600 space-y-1">
                <li><strong>Players:</strong> /api/v1/players - Get all players with filtering</li>
                <li><strong>Player Detail:</strong> /api/v1/players/:id - Get specific player</li>
                <li><strong>Player Games:</strong> /api/v1/players/:id/games - Get player game log</li>
                <li><strong>Teams:</strong> /api/v1/teams - Get all teams</li>
                <li><strong>Team Detail:</strong> /api/v1/teams/:id - Get specific team</li>
                <li><strong>Projections:</strong> /api/v1/projections/2027 - Get 2027 projections</li>
                <li><strong>Clusters:</strong> /api/v1/clusters - Get cluster analysis</li>
                <li><strong>Similarity:</strong> /api/v1/similarity/nearest/:id - Get similar players</li>
                <li><strong>Years:</strong> /api/v1/years - Get available years</li>
                <li><strong>Health:</strong> /health - Health check endpoint</li>
              </ul>
            </section>

            <section>
              <h2 className="text-lg font-bold mb-2">Interactive API Docs</h2>
              <p className="text-gray-700">
                When running in development mode, interactive API documentation is available at:
              </p>
              <ul className="mt-2 list-disc list-inside text-gray-600">
                <li><strong>Swagger UI:</strong> http://localhost:8000/docs</li>
                <li><strong>ReDoc:</strong> http://localhost:8000/redoc</li>
              </ul>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
}
