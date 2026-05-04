import "./globals.css";
import { YearProvider } from "@/app/context/YearContext";
import YearToggle from "@/components/ui/YearToggle";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-[#E7E8D1] font-mono text-black flex justify-center items-start min-h-screen py-6">
        
        <YearProvider>
          <div className="w-[900px] border-4 border-black bg-[#C7D0B8] shadow-[6px_6px_0px_black]">

            {/* 🔥 GLOBAL YEAR TOGGLE */}
            <div className="border-b-2 border-black p-2 bg-[#B7C4A5]">
              <YearToggle />
            </div>

            {children}

          </div>
        </YearProvider>

      </body>
    </html>
  );
}