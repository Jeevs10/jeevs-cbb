import { cn } from "@/lib/utils";

interface ErrorMessageProps {
  message: string;
  onRetry?: () => void;
  className?: string;
}

export function ErrorMessage({ message, onRetry, className }: ErrorMessageProps) {
  return (
    <div className={cn(
      "p-4 border-2 border-black bg-red-100",
      className
    )}>
      <div className="flex items-start justify-between">
        <div>
          <h3 className="font-bold text-red-800">Error</h3>
          <p className="text-red-700 mt-1">{message}</p>
        </div>
        {onRetry && (
          <button
            onClick={onRetry}
            className="ml-4 px-3 py-1 bg-black text-white text-sm border border-black hover:bg-gray-800"
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
      <h3 className="text-lg font-medium text-gray-900">{title}</h3>
      {description && (
        <p className="mt-2 text-sm text-gray-500">{description}</p>
      )}
      {action && (
        <button
          onClick={action.onClick}
          className="mt-4 px-4 py-2 bg-black text-white border border-black hover:bg-gray-800"
        >
          {action.label}
        </button>
      )}
    </div>
  );
}
