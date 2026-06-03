import { cn } from "@/lib/utils";

interface ErrorMessageProps {
  message: string;
  onRetry?: () => void;
  className?: string;
}

export function ErrorMessage({ message, onRetry, className }: ErrorMessageProps) {
  return (
    <div className={cn(
      "p-4 border-2 border-black bg-[#E7E8D1] shadow-[3px_3px_0px_black]",
      className
    )}>
      <div className="flex items-start justify-between">
        <div>
          <h3 className="font-bold text-black uppercase tracking-wide">Error</h3>
          <p className="text-black mt-1">{message}</p>
        </div>
        {onRetry && (
          <button
            onClick={onRetry}
            className="ml-4 px-3 py-1 bg-black text-white text-xs border-2 border-black hover:bg-gray-800 shadow-[3px_3px_0px_black]"
          >
            Retry
          </button>
        )}
      </div>
    </div>
  );
}

interface EmptyStateProps {
  title: string;
  description?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  className?: string;
}

export function EmptyState({ title, description, action, className }: EmptyStateProps) {
  return (
    <div className={cn("text-center py-12", className)}>
      <h3 className="text-xs font-medium text-black uppercase tracking-wide">{title}</h3>
      {description && (
        <p className="mt-2 text-xs text-black">{description}</p>
      )}
      {action && (
        <button
          onClick={action.onClick}
          className="mt-4 px-4 py-2 bg-black text-white border-2 border-black hover:bg-gray-800 shadow-[3px_3px_0px_black]"
        >
          {action.label}
        </button>
      )}
    </div>
  );
}
