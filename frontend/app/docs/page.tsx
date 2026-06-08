import Link from "next/link";

export default function DocsPage() {
  const docs = [
    {
      title: "API Documentation",
      description: "Complete API reference with all endpoints, parameters, and response formats",
      href: "/docs/api",
    },
    {
      title: "Data Sources",
      description: "Information about data providers, data processing, and data quality",
      href: "/docs/data-sources",
    },
    {
      title: "System Architecture",
      description: "Technical architecture, technology stack, and system design",
      href: "/docs/architecture",
    },
    {
      title: "Analytics and Models",
      description: "In-depth explanations of analytics, metrics, and machine learning models",
      href: "/docs/analytics",
    },
    {
      title: "Technology Stack",
      description: "Complete list of technologies, packages, and tools used",
      href: "/docs/tech-stack",
    },
  ];

  return (
    <div className="min-h-screen bg-[#E7E8D1] p-4 sm:p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl sm:text-3xl font-bold mb-6 text-black">Documentation</h1>
        <p className="text-sm sm:text-base mb-8 text-gray-700">
          Comprehensive documentation for JEEVS CBB, covering API usage, data sources, system architecture, and analytics methodologies.
        </p>

        <div className="grid gap-4">
          {docs.map((doc) => (
            <Link
              key={doc.href}
              href={doc.href}
              className="block p-6 border-2 border-black bg-white hover:bg-[#C7D0B8] transition-colors shadow-[3px_3px_0px_black]"
            >
              <h2 className="text-lg font-bold mb-2 text-black">{doc.title}</h2>
              <p className="text-sm text-gray-600">{doc.description}</p>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
