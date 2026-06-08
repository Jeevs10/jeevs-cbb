import Link from "next/link";

export default function TechStackPage() {
  return (
    <div className="min-h-screen bg-[#E7E8D1] p-4 sm:p-8">
      <div className="max-w-4xl mx-auto">
        <Link href="/docs" className="inline-block mb-6 text-sm font-bold text-black hover:underline">
          ← Back to Documentation
        </Link>

        <h1 className="text-2xl sm:text-3xl font-bold mb-6 text-black">Technology Stack</h1>

        <div className="bg-white border-2 border-black p-6 shadow-[3px_3px_0px-black]">
          <p className="text-sm text-gray-600 mb-4">
            For complete technology stack documentation, please refer to the <a href="https://github.com/Jeevs10/jeevs-cbb/blob/main/docs/TECH_STACK.md" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">TECH_STACK.md</a> file on GitHub.
          </p>

          <div className="space-y-6 text-sm">
            <section>
              <h2 className="text-lg font-bold mb-2">Languages</h2>
              <ul className="list-disc list-inside text-gray-600">
                <li><strong>Backend:</strong> Python 3.11+</li>
                <li><strong>Frontend:</strong> TypeScript 6.0.3, JavaScript</li>
              </ul>
            </section>

            <section>
              <h2 className="text-lg font-bold mb-2">Backend Frameworks</h2>
              <div className="space-y-2">
                <div>
                  <h3 className="font-bold text-black">Core</h3>
                  <ul className="list-disc list-inside text-gray-600 ml-4">
                    <li>FastAPI - Web framework</li>
                    <li>Uvicorn - ASGI server</li>
                  </ul>
                </div>
                <div>
                  <h3 className="font-bold text-black">Data Processing</h3>
                  <ul className="list-disc list-inside text-gray-600 ml-4">
                    <li>Pandas - Data manipulation</li>
                    <li>NumPy - Numerical computing</li>
                    <li>Scikit-learn - Machine learning</li>
                  </ul>
                </div>
                <div>
                  <h3 className="font-bold text-black">Validation & Configuration</h3>
                  <ul className="list-disc list-inside text-gray-600 ml-4">
                    <li>Pydantic - Data validation</li>
                    <li>python-dotenv - Environment variables</li>
                  </ul>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-lg font-bold mb-2">Frontend Frameworks</h2>
              <div className="space-y-2">
                <div>
                  <h3 className="font-bold text-black">Core</h3>
                  <ul className="list-disc list-inside text-gray-600 ml-4">
                    <li>Next.js 14.0.0 - React framework</li>
                    <li>React 18.2.0 - UI library</li>
                    <li>TypeScript 6.0.3 - Type safety</li>
                  </ul>
                </div>
                <div>
                  <h3 className="font-bold text-black">UI & Styling</h3>
                  <ul className="list-disc list-inside text-gray-600 ml-4">
                    <li>Tailwind CSS 3.4.19 - Utility-first CSS</li>
                    <li>Framer Motion 12.40.0 - Animations</li>
                    <li>Lucide React 1.14.0 - Icons</li>
                  </ul>
                </div>
                <div>
                  <h3 className="font-bold text-black">Visualization</h3>
                  <ul className="list-disc list-inside text-gray-600 ml-4">
                    <li>Recharts 3.8.1 - Charts</li>
                    <li>React Simple Maps 3.0.0 - Maps</li>
                    <li>Leaflet 1.9.4 - Interactive maps</li>
                  </ul>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-lg font-bold mb-2">Development Tools</h2>
              <div className="space-y-2">
                <div>
                  <h3 className="font-bold text-black">Testing</h3>
                  <ul className="list-disc list-inside text-gray-600 ml-4">
                    <li>Jest - Frontend testing</li>
                    <li>pytest - Backend testing</li>
                    <li>Testing Library - React testing utilities</li>
                  </ul>
                </div>
                <div>
                  <h3 className="font-bold text-black">Code Quality</h3>
                  <ul className="list-disc list-inside text-gray-600 ml-4">
                    <li>ESLint - JavaScript linter</li>
                    <li>Prettier - Code formatter</li>
                    <li>TypeScript - Type checking</li>
                  </ul>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-lg font-bold mb-2">Deployment</h2>
              <ul className="list-disc list-inside text-gray-600">
                <li><strong>Frontend:</strong> Vercel</li>
                <li><strong>Backend:</strong> Render</li>
                <li><strong>Version Control:</strong> Git, GitHub</li>
              </ul>
            </section>

            <section>
              <h2 className="text-lg font-bold mb-2">Data Storage</h2>
              <ul className="list-disc list-inside text-gray-600">
                <li>CSV files (gzip compressed)</li>
                <li>JSON files (gzip compressed)</li>
                <li>Pickle files (cached vectors)</li>
              </ul>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
}
