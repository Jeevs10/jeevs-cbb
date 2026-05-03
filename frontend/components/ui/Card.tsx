// components/ui/Card.tsx
import Panel from "./Panel";

export default function Card({ children, className = "" }) {
  return (
    <Panel className={`hover:bg-[#b8c0a8] transition ${className}`}>
      {children}
    </Panel>
  );
}