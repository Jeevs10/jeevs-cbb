"use client";

interface D1FilterProps {
  d1Only: boolean;
  onD1Change: (d1Only: boolean) => void;
}

export function D1Filter({ d1Only, onD1Change }: D1FilterProps) {
  return (
    <div className="mb-3 flex gap-2 flex-wrap">
      <button
        onClick={() => onD1Change(false)}
        className={`px-2 border transition-colors ${
          !d1Only 
            ? "font-bold underline bg-[#B7C4A5]" 
            : "hover:bg-[#e7e8d1]"
        }`}
      >
        ALL
      </button>
      <button
        onClick={() => onD1Change(true)}
        className={`px-2 border transition-colors ${
          d1Only 
            ? "font-bold underline bg-[#B7C4A5]" 
            : "hover:bg-[#e7e8d1]"
        }`}
      >
        D1
      </button>
    </div>
  );
}
