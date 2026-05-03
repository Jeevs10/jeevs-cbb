import clsx from "clsx";

export default function Panel({ children, className = "" }) {
  return (
    <div
      className={clsx(
        "border-2 border-black bg-[#C7D0B8] shadow-[3px_3px_0px_black]",
        "p-3",
        className
      )}
    >
      {children}
    </div>
  );
}

export function PanelDark({ children, className = "" }) {
  return (
    <div
      className={clsx(
        "border-2 border-green-400 bg-black text-green-400",
        "shadow-[3px_3px_0px_black] p-3",
        className
      )}
    >
      {children}
    </div>
  );
}

export function PanelHeader({ children }) {
  return (
    <div className="border-b-2 border-black mb-2 pb-1 text-xs font-bold uppercase tracking-wide">
      {children}
    </div>
  );
}