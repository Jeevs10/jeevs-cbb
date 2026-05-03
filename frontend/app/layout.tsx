import "./globals.css";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-[#E7E8D1] font-mono text-black flex justify-center items-start min-h-screen py-6">
        <div className="w-[900px] border-4 border-black bg-[#C7D0B8] shadow-[6px_6px_0px_black]">
          {children}
        </div>
      </body>
    </html>
  );
}